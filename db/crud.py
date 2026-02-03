from db.database import SessionLocal
from db.models import ChatMessage, ConversationSummary


# ---------- WRITE OPERATIONS ----------

def save_message(session_id: str, role: str, content: str):
    db = SessionLocal()
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(msg)
    db.commit()
    db.close()


def save_summary(session_id: str, summary: str):
    db = SessionLocal()

    existing = (
        db.query(ConversationSummary)
        .filter(ConversationSummary.session_id == session_id)
        .first()
    )

    if existing:
        existing.summary = summary
    else:
        existing = ConversationSummary(
            session_id=session_id,
            summary=summary
        )
        db.add(existing)

    db.commit()
    db.close()


# ---------- READ OPERATIONS ----------

def get_messages(session_id: str):
    db = SessionLocal()
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    db.close()
    return messages


def get_summary(session_id: str):
    db = SessionLocal()
    summary = (
        db.query(ConversationSummary)
        .filter(ConversationSummary.session_id == session_id)
        .first()
    )
    db.close()
    return summary.summary if summary else ""
