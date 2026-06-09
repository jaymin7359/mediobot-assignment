from qdrant_client.models import FieldCondition, Filter, MatchValue

from backend.config import ROLE_COLLECTIONS

RESTRICTED_KEYWORDS = {
    "billing": ["billing", "insurance", "claim", "icd", "reimbursement", "pre-auth"],
    "equipment": ["equipment", "calibration", "maintenance schedule", "ventilator"],
    "clinical": ["drug formulary", "treatment protocol", "diagnostic"],
    "nursing": ["icu nursing", "infection control"],
}


def get_collections_for_role(role: str) -> list[str]:
    return ROLE_COLLECTIONS[role]


def build_rbac_filter(role: str) -> Filter | None:
    """Apply access_roles filter at Qdrant query level."""
    if role == "admin":
        return None
    return Filter(
        must=[
            FieldCondition(
                key="metadata.access_roles",
                match=MatchValue(value=role),
            )
        ]
    )


def rbac_refusal_message(role: str, topic: str) -> str:
    allowed = ", ".join(get_collections_for_role(role))
    return (
        f"As a {role.replace('_', ' ')}, you don't have access to {topic} documents. "
        f"I can only answer questions from the {allowed} collections."
    )


def detect_restricted_topic(question: str, role: str) -> str | None:
    allowed = set(get_collections_for_role(role))
    q = question.lower()
    for collection, keywords in RESTRICTED_KEYWORDS.items():
        if collection not in allowed and any(kw in q for kw in keywords):
            return collection
    return None
