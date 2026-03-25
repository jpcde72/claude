from sqlalchemy.orm import Session

from app.models import Intent, IntentStatus, TaskStatus


def auto_update_intent_status(db: Session, intent_id: int) -> Intent:
    """Auto-complete intent if all tasks across all plans are completed."""
    intent = db.query(Intent).get(intent_id)
    if not intent:
        raise ValueError(f"Intent {intent_id} not found")

    all_tasks = [task for plan in intent.plans for task in plan.tasks]

    if not all_tasks:
        return intent

    if all(t.status == TaskStatus.COMPLETED for t in all_tasks):
        intent.status = IntentStatus.COMPLETED
        db.commit()
        db.refresh(intent)

    return intent
