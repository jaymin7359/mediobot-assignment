"""Lightweight chat routing — no ML model imports."""


def is_analytical_question(question: str) -> bool:
    """Route to SQL RAG for numbers/stats and database record lookups."""
    q = question.lower()

    analytical_keywords = [
        "how many", "count", "total", "average", "sum", "most", "least",
        "number of", "statistics", "how much", "which department", "open tickets",
    ]
    if any(kw in q for kw in analytical_keywords):
        return True

    db_entities = [
        "patient", "claim", "ticket", "maintenance", "department",
        "insurer", "amount", "status", "equipment", "billing",
    ]
    list_patterns = ["list all", "list ", "show all", "show me all", "get all", "all "]
    if any(p in q for p in list_patterns) and any(e in q for e in db_entities):
        return True

    if "patient name" in q or "patient names" in q:
        return True

    record_patterns = [
        "claim type of", "claim type for", "type of claim",
        "claim status of", "claim status for", "status of claim",
        "approved amount for", "claimed amount for",
        "insurer for", "department for", "diagnosis code for",
    ]
    if any(p in q for p in record_patterns):
        return True

    db_lookup_fields = [
        "claim type", "claim status", "approved amount", "claimed amount",
        "insurer", "department", "diagnosis code", "claim id", "ticket status",
    ]
    if any(f in q for f in db_lookup_fields) and (" of " in q or " for " in q):
        return True

    return False
