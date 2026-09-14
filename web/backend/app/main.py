"""FastAPI entrypoint for the CEO Operating System web backend."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import db
from .api import content, history, llm, tools
from .core.config import FRONTEND_DIST


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="CEO Operating System", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


api = FastAPI(title="CEO Operating System API")
api.include_router(tools.router)
api.include_router(llm.router)
api.include_router(history.router)
api.include_router(content.router)


@api.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


app.mount("/api", api)


def _mount_frontend() -> None:
    if not FRONTEND_DIST.is_dir():
        return
    index = FRONTEND_DIST / "index.html"
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets", check_dir=False),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str) -> FileResponse:
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file() and candidate.resolve().is_relative_to(
            FRONTEND_DIST.resolve()
        ):
            return FileResponse(candidate)
        return FileResponse(index)


_mount_frontend()


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
