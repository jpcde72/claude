from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp import types
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from starlette.requests import Request

from app.config import settings
from app.database import SessionLocal
from app.models import Intent, IntentStatus, Plan, Task, TaskStatus
from app.schemas import IntentCreate, PlanCreate, TaskCreate
from app.services.task_service import (
    calculate_intent_progress,
    calculate_plan_progress,
    update_task_status as svc_update_task_status,
)

_server = Server("intent-planner")
_sse = SseServerTransport("/mcp/messages/")


def _db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


@_server.list_tools()
async def _list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_intents",
            description="List all intents",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_intent",
            description="Get a specific intent with its plans and tasks",
            inputSchema={
                "type": "object",
                "properties": {"intent_id": {"type": "integer"}},
                "required": ["intent_id"],
            },
        ),
        types.Tool(
            name="create_intent",
            description="Create a new intent",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["title"],
            },
        ),
        types.Tool(
            name="update_intent_status",
            description="Update an intent's status",
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": [s.value for s in IntentStatus],
                    },
                },
                "required": ["intent_id", "status"],
            },
        ),
        types.Tool(
            name="create_plan",
            description="Create a plan for an intent",
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["intent_id", "title"],
            },
        ),
        types.Tool(
            name="create_task",
            description="Create a task in a plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["plan_id", "title"],
            },
        ),
        types.Tool(
            name="update_task_status",
            description="Update a task's status",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": [s.value for s in TaskStatus],
                    },
                },
                "required": ["task_id", "status"],
            },
        ),
        types.Tool(
            name="get_plan_progress",
            description="Get progress statistics for a plan",
            inputSchema={
                "type": "object",
                "properties": {"plan_id": {"type": "integer"}},
                "required": ["plan_id"],
            },
        ),
    ]


@_server.call_tool()
async def _call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    import json

    db = SessionLocal()
    try:
        result = _dispatch(db, name, arguments)
        return [types.TextContent(type="text", text=json.dumps(result, default=str))]
    finally:
        db.close()


def _dispatch(db, name: str, args: dict):
    if name == "list_intents":
        intents = db.query(Intent).order_by(Intent.updated_at.desc()).all()
        return [
            {
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "status": i.status,
                "created_at": str(i.created_at),
            }
            for i in intents
        ]

    if name == "get_intent":
        intent = db.query(Intent).get(args["intent_id"])
        if not intent:
            return {"error": f"Intent {args['intent_id']} not found"}
        progress = calculate_intent_progress(db, intent.id)
        return {
            "id": intent.id,
            "title": intent.title,
            "description": intent.description,
            "status": intent.status,
            "progress": progress,
            "plans": [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "tasks": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "status": t.status,
                            "order": t.order,
                        }
                        for t in p.tasks
                    ],
                }
                for p in intent.plans
            ],
        }

    if name == "create_intent":
        intent = Intent(
            title=args["title"],
            description=args.get("description"),
        )
        db.add(intent)
        db.commit()
        db.refresh(intent)
        return {"id": intent.id, "title": intent.title, "status": intent.status}

    if name == "update_intent_status":
        intent = db.query(Intent).get(args["intent_id"])
        if not intent:
            return {"error": f"Intent {args['intent_id']} not found"}
        intent.status = IntentStatus(args["status"])
        db.commit()
        db.refresh(intent)
        return {"id": intent.id, "status": intent.status}

    if name == "create_plan":
        intent = db.query(Intent).get(args["intent_id"])
        if not intent:
            return {"error": f"Intent {args['intent_id']} not found"}
        order = len(intent.plans)
        plan = Plan(
            intent_id=args["intent_id"],
            title=args["title"],
            description=args.get("description"),
            order=order,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return {"id": plan.id, "title": plan.title, "intent_id": plan.intent_id}

    if name == "create_task":
        plan = db.query(Plan).get(args["plan_id"])
        if not plan:
            return {"error": f"Plan {args['plan_id']} not found"}
        order = len(plan.tasks)
        task = Task(
            plan_id=args["plan_id"],
            title=args["title"],
            description=args.get("description"),
            order=order,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return {"id": task.id, "title": task.title, "status": task.status}

    if name == "update_task_status":
        try:
            task = svc_update_task_status(db, args["task_id"], TaskStatus(args["status"]))
            return {"id": task.id, "status": task.status}
        except ValueError as e:
            return {"error": str(e)}

    if name == "get_plan_progress":
        return calculate_plan_progress(db, args["plan_id"])

    return {"error": f"Unknown tool: {name}"}


router = APIRouter()


def _check_auth(request: Request) -> None:
    token = settings.META_ACCESS_TOKEN
    if not token:
        return
    auth = request.headers.get("authorization", "")
    if auth != f"Bearer {token}":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


@router.get("/mcp")
async def handle_sse(request: Request):
    _check_auth(request)
    async with _sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await _server.run(streams[0], streams[1], _server.create_initialization_options())
    return Response()


@router.post("/mcp/messages/")
async def handle_messages(request: Request):
    await _sse.handle_post_message(request.scope, request.receive, request._send)
    return Response()
