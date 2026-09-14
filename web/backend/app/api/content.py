"""Routes serving framework references and document templates."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..core.config import CONTENT_DIR
from ..schemas import Framework, FrameworksResponse, Template, TemplatesResponse

router = APIRouter(tags=["content"])

_FRAMEWORKS = [
    ("fundraising", "Fundraising Framework", "fundraising.md"),
    ("pmf", "Product-Market Fit Framework", "pmf.md"),
]

_TEMPLATES = [
    ("pitch-deck-outline", "Pitch Deck Outline", "pitch-deck-outline.md"),
    ("one-on-one-agenda", "1:1 Agenda", "one-on-one-agenda.md"),
]


def _read_content(filename: str) -> str:
    path = CONTENT_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=500, detail=f"Content file missing: {filename}")
    return path.read_text(encoding="utf-8")


@router.get("/frameworks", response_model=FrameworksResponse)
def frameworks() -> FrameworksResponse:
    return FrameworksResponse(
        frameworks=[
            Framework(id=fid, title=title, content=_read_content(filename))
            for fid, title, filename in _FRAMEWORKS
        ]
    )


@router.get("/templates", response_model=TemplatesResponse)
def templates() -> TemplatesResponse:
    return TemplatesResponse(
        templates=[
            Template(
                id=tid,
                title=title,
                filename=filename,
                content=_read_content(filename),
            )
            for tid, title, filename in _TEMPLATES
        ]
    )
