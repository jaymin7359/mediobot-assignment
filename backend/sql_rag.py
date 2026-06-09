"""SQL RAG — same 3-step pattern as advanced_rag.ipynb."""

import re

from langchain_classic.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from backend.config import DB_PATH, GROQ_MODEL

SYSTEM_PROMPT = """You are a MediAssist operations analytics assistant.
Given a user question and the SQL query result from our database,
provide a clear, concise natural language answer.
Be specific with numbers and facts from the data."""

_db: SQLDatabase | None = None
_llm: ChatGroq | None = None
_sql_query_chain = None


def _init_sql_rag():
    global _db, _llm, _sql_query_chain
    if _db is None:
        _db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
        _llm = ChatGroq(model=GROQ_MODEL, temperature=0, max_retries=2)
        _sql_query_chain = create_sql_query_chain(_llm, _db)


def clean_sql(raw: str) -> str:
    raw = re.sub(r"```(?:sql)?", "", raw).strip("`").strip()
    if "SQLQuery:" in raw:
        raw = raw.split("SQLQuery:")[-1].strip()
    return raw


def sql_rag_chain(question: str) -> str:
    _init_sql_rag()

    # Step 1: Translate question to SQL
    raw_sql = _sql_query_chain.invoke({"question": question})
    sql = clean_sql(raw_sql)

    # Step 2: Execute SQL
    result = _db.run(sql)

    # Step 3: Natural language answer
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Question: {question}\nSQL Result: {result}\n\nAnswer:"),
    ])
    response = answer_prompt | _llm
    return response.invoke({"question": question, "result": result}).content
