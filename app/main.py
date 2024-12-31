from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from .db.main import init_db
from .routers import (admin, user, course, editor, course_tag, tag)
from .errors import register_all_errors
from .middleware import register_middleware


@asynccontextmanager
async def life_span(app:FastAPI):
    print(f"Server is starting...")
    await init_db()
    yield
    print(f"Server has been stopped")

version = "v1"

app = FastAPI(
    title="CaseSimpli LegalPadi",
    description="An App for everyday legal learning.",
    version=version,
    lifespan=life_span
)

register_all_errors(app)
register_middleware(app)


api_router = APIRouter()
api_router.include_router(admin.router)
api_router.include_router(user.router)
api_router.include_router(course.router)
api_router.include_router(editor.router)
api_router.include_router(tag.router)
api_router.include_router(course_tag.router)


app.include_router(api_router, prefix=f"/api/{version}")


@app.get('/')
async def read_root():
    return {"message": "Welcome to CaseSimpli LegalPadi"}



