from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import models_geo  # noqa: F401  (registers GEO Studio tables)
from app.database import init_db
from app.routers import geo, intents, plans, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Intent Planner", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(intents.router)
app.include_router(plans.router)
app.include_router(tasks.router)
app.include_router(geo.router)
