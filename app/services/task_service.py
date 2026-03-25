from collections import deque
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Task, TaskStatus, task_dependencies


def update_task_status(db: Session, task_id: int, new_status: TaskStatus) -> Task:
    task = db.query(Task).get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    if new_status == TaskStatus.IN_PROGRESS:
        incomplete_deps = [
            d for d in task.dependencies if d.status != TaskStatus.COMPLETED
        ]
        if incomplete_deps:
            names = ", ".join(d.title for d in incomplete_deps)
            raise ValueError(f"Cannot start: dependencies not completed: {names}")

    task.status = new_status
    task.completed_at = datetime.utcnow() if new_status == TaskStatus.COMPLETED else None
    db.commit()
    db.refresh(task)
    return task


def has_dependency_cycle(db: Session, task_id: int, depends_on_id: int) -> bool:
    """Check if adding depends_on_id as a dependency of task_id would create a cycle."""
    if task_id == depends_on_id:
        return True

    visited: set[int] = set()
    queue: deque[int] = deque([task_id])

    while queue:
        current = queue.popleft()
        if current == depends_on_id:
            continue
        if current in visited:
            continue
        visited.add(current)

        # Find tasks that depend on current (current is a dependency of those tasks)
        dependents = (
            db.query(task_dependencies.c.task_id)
            .filter(task_dependencies.c.depends_on_id == current)
            .all()
        )
        for (dep_task_id,) in dependents:
            if dep_task_id == depends_on_id:
                return True
            queue.append(dep_task_id)

    return False


def add_dependency(db: Session, task_id: int, depends_on_id: int) -> None:
    task = db.query(Task).get(task_id)
    depends_on = db.query(Task).get(depends_on_id)
    if not task or not depends_on:
        raise ValueError("Task not found")
    if depends_on in task.dependencies:
        raise ValueError("Dependency already exists")
    if has_dependency_cycle(db, task_id, depends_on_id):
        raise ValueError("Adding this dependency would create a cycle")

    task.dependencies.append(depends_on)
    db.commit()


def remove_dependency(db: Session, task_id: int, depends_on_id: int) -> None:
    task = db.query(Task).get(task_id)
    depends_on = db.query(Task).get(depends_on_id)
    if not task or not depends_on:
        raise ValueError("Task not found")
    task.dependencies.remove(depends_on)
    db.commit()


def calculate_plan_progress(db: Session, plan_id: int) -> dict:
    tasks = db.query(Task).filter(Task.plan_id == plan_id).all()
    total = len(tasks)
    if total == 0:
        return {"total": 0, "completed": 0, "in_progress": 0, "failed": 0, "percent": 0}

    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
    failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "failed": failed,
        "percent": int((completed / total) * 100),
    }


def calculate_intent_progress(db: Session, intent_id: int) -> dict:
    from app.models import Plan

    plans = db.query(Plan).filter(Plan.intent_id == intent_id).all()
    total = 0
    completed = 0
    in_progress = 0
    failed = 0

    for plan in plans:
        for task in plan.tasks:
            total += 1
            if task.status == TaskStatus.COMPLETED:
                completed += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                in_progress += 1
            elif task.status == TaskStatus.FAILED:
                failed += 1

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "failed": failed,
        "percent": int((completed / total) * 100) if total > 0 else 0,
    }


def get_ready_tasks(db: Session, plan_id: int) -> list[Task]:
    """Get tasks whose dependencies are all completed and status is pending."""
    tasks = (
        db.query(Task)
        .filter(Task.plan_id == plan_id, Task.status == TaskStatus.PENDING)
        .all()
    )
    return [
        t for t in tasks
        if all(d.status == TaskStatus.COMPLETED for d in t.dependencies)
    ]
