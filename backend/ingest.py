"""Document ingestion — Docling + HybridChunker (same pattern as advanced_rag.ipynb)."""

from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from transformers import AutoTokenizer

from backend.config import (
    ACCESS_ROLES_BY_COLLECTION,
    COLLECTION_NAME,
    DATA_DIR,
    EMBED_MODEL,
    QDRANT_PATH,
)

COLLECTION_FOLDERS = {
    "general": DATA_DIR / "general",
    "clinical": DATA_DIR / "clinical",
    "nursing": DATA_DIR / "nursing",
    "billing": DATA_DIR / "billing",
    "equipment": DATA_DIR / "equipment",
}


def _chunk_type(chunk) -> str:
    label = str(getattr(chunk, "label", "") or "").lower()
    if "table" in label:
        return "table"
    if "heading" in label or "title" in label:
        return "heading"
    if "code" in label:
        return "code"
    return "text"


def _section_title(chunk) -> str:
    meta = getattr(chunk, "meta", None)
    if meta and getattr(meta, "headings", None):
        return " > ".join(meta.headings)
    return "General"


def parse_documents() -> list[Document]:
    converter = DocumentConverter()
    tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=128,
        merge_peers=True,
    )

    all_docs: list[Document] = []
    for collection, folder in COLLECTION_FOLDERS.items():
        if not folder.exists():
            continue
        for file_path in sorted(folder.iterdir()):
            if file_path.suffix.lower() not in {".pdf", ".md"}:
                continue

            dl_doc = converter.convert(str(file_path)).document
            for chunk in chunker.chunk(dl_doc=dl_doc):
                all_docs.append(
                    Document(
                        page_content=chunker.serialize(chunk=chunk),
                        metadata={
                            "source_document": file_path.name,
                            "collection": collection,
                            "access_roles": ACCESS_ROLES_BY_COLLECTION[collection],
                            "section_title": _section_title(chunk),
                            "chunk_type": _chunk_type(chunk),
                        },
                    )
                )

    return all_docs


def build_vectorstore(docs: list[Document]) -> QdrantVectorStore:
    dense_embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25", batch_size=32)

    return QdrantVectorStore.from_documents(
        documents=docs,
        embedding=dense_embeddings,
        sparse_embedding=sparse_embeddings,
        path=QDRANT_PATH,
        collection_name=COLLECTION_NAME,
        retrieval_mode=RetrievalMode.HYBRID,
    )


def run_ingestion() -> int:
    docs = parse_documents()
    if not docs:
        raise RuntimeError(f"No documents found under {DATA_DIR}")
    build_vectorstore(docs)
    print(f"Indexed {len(docs)} chunks into '{COLLECTION_NAME}'")
    return len(docs)


if __name__ == "__main__":
    run_ingestion()
