"""Routes for run history."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import HistoryListResponse, OkResponse, RunDetail

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryListResponse)
def history_list(tool: str | None = None) -> HistoryListResponse:
    return HistoryListResponse(runs=db.list_runs(tool))  # type: ignore[arg-type]


@router.get("/{run_id}", response_model=RunDetail)
def history_detail(run_id: int) -> RunDetail:
    run = db.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")
    return RunDetail(**run)


@router.delete("/{run_id}", response_model=OkResponse)
def history_delete(run_id: int) -> OkResponse:
    if not db.delete_run(run_id):
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")
    return OkResponse(ok=True)
