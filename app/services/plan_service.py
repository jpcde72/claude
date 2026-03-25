from sqlalchemy.orm import Session

from app.models import Task


def reorder_tasks(db: Session, plan_id: int, task_ids: list[int]) -> None:
    """Reorder tasks in a plan based on the provided list of task IDs."""
    tasks = db.query(Task).filter(Task.plan_id == plan_id).all()
    task_map = {t.id: t for t in tasks}

    for index, task_id in enumerate(task_ids):
        if task_id in task_map:
            task_map[task_id].order = index

    db.commit()
