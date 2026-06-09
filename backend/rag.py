"""Hybrid RAG + Reranking — same pattern as advanced_rag.ipynb."""

from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode

from backend.config import COLLECTION_NAME, EMBED_MODEL, GROQ_MODEL, QDRANT_PATH
from backend.rbac import build_rbac_filter

SYSTEM_PROMPT = """You are MediBot, an internal assistant for MediAssist Health Network.
Answer using ONLY the context below. Cite the source document when possible.
If the answer is not in the context, say you could not find that information.

When using tables, use valid GitHub-flavored markdown:
- one header row, then a separator row (| --- | --- |), then one row per line
- every row must start and end with |
- never break a table row across multiple lines

When the user asks to list all codes or items, include EVERY matching entry from the context.
Do not truncate, summarize, or stop early — list all codes you can see.

Context:
{context}"""

_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

_llm: ChatGroq | None = None
_question_answer_chain = None
_cross_encoder: HuggingFaceCrossEncoder | None = None
_vectorstore: QdrantVectorStore | None = None


def _get_llm_chain():
    global _llm, _question_answer_chain
    if _llm is None:
        _llm = ChatGroq(model=GROQ_MODEL, temperature=0, max_retries=2)
        _question_answer_chain = create_stuff_documents_chain(_llm, _prompt)
    return _question_answer_chain


def _get_cross_encoder() -> HuggingFaceCrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        _cross_encoder = HuggingFaceCrossEncoder(
            model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
    return _cross_encoder


def _load_vectorstore() -> QdrantVectorStore:
    dense_embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25", batch_size=32)
    return QdrantVectorStore.from_existing_collection(
        embedding=dense_embeddings,
        sparse_embedding=sparse_embeddings,
        path=QDRANT_PATH,
        collection_name=COLLECTION_NAME,
        retrieval_mode=RetrievalMode.HYBRID,
    )


def is_list_question(question: str) -> bool:
    q = question.lower()
    keywords = [
        "list all", "all codes", "all diagnosis", "every code",
        "complete list", "full list", "top 30", "nosis codes",
    ]
    return any(kw in q for kw in keywords)


def _get_reranking_chain(role: str, question: str):
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = _load_vectorstore()

    # List queries need more chunks — Top 30 codes span multiple document chunks
    broad_k = 20 if is_list_question(question) else 10
    top_n = 8 if is_list_question(question) else 3

    rbac_filter = build_rbac_filter(role)
    search_kwargs = {"k": broad_k}
    if rbac_filter is not None:
        search_kwargs["filter"] = rbac_filter

    reranker = CrossEncoderReranker(model=_get_cross_encoder(), top_n=top_n)
    broad_retriever = _vectorstore.as_retriever(search_kwargs=search_kwargs)
    reranking_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=broad_retriever,
    )
    return create_retrieval_chain(reranking_retriever, _get_llm_chain())


def hybrid_rag_answer(question: str, role: str) -> tuple[str, list[dict]]:
    chain = _get_reranking_chain(role, question)
    result = chain.invoke({"input": question})

    sources = []
    for doc in result.get("context", []):
        sources.append({
            "source_document": doc.metadata.get("source_document", "unknown"),
            "section_title": doc.metadata.get("section_title", ""),
            "collection": doc.metadata.get("collection", ""),
        })

    return result["answer"], sources


