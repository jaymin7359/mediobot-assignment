import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import ROLE_COLLECTIONS  # loads .env on import
from backend.auth import authenticate, create_token, decode_token
from backend.rbac import detect_restricted_topic, get_collections_for_role, rbac_refusal_message
from backend.routing import is_analytical_question

app = FastAPI(title="MediBot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    question: str


def _get_role_from_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    return payload["role"]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/login")
def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    token = create_token(req.username, user["role"])
    return {"token": token, "role": user["role"], "username": req.username}


@app.get("/collections/{role}")
def collections(role: str):
    if role not in ROLE_COLLECTIONS:
        raise HTTPException(status_code=404, detail="Unknown role")
    return {"role": role, "collections": get_collections_for_role(role)}


@app.post("/chat")
def chat(req: ChatRequest, authorization: str | None = Header(default=None)):
    # Lazy import — keeps /login fast (models load on first chat only)
    from backend.rag import hybrid_rag_answer
    from backend.sql_rag import sql_rag_chain

    role = _get_role_from_token(authorization)

    restricted = detect_restricted_topic(req.question, role)
    if restricted:
        return {
            "answer": rbac_refusal_message(role, restricted),
            "sources": [],
            "retrieval_type": "hybrid_rag",
            "role": role,
            "blocked": True,
        }

    if is_analytical_question(req.question):
        if role not in {"billing_executive", "admin"}:
            return {
                "answer": (
                    f"As a {role.replace('_', ' ')}, you don't have access to database analytics. "
                    "Only billing executives and admins can run SQL queries."
                ),
                "sources": [],
                "retrieval_type": "sql_rag",
                "role": role,
                "blocked": True,
            }
        answer = sql_rag_chain(req.question)
        return {
            "answer": answer,
            "sources": [],
            "retrieval_type": "sql_rag",
            "role": role,
            "blocked": False,
        }

    answer, sources = hybrid_rag_answer(req.question, role)
    return {
        "answer": answer,
        "sources": sources,
        "retrieval_type": "hybrid_rag",
        "role": role,
        "blocked": False,
    }


if __name__ == "__main__":
    import uvicorn

    if not os.getenv("GROQ_API_KEY"):
        print("Set GROQ_API_KEY in .env before running.")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
