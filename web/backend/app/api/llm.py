"""Routes for LLM connection testing and AI analysis."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    LLMAnalyzeRequest,
    LLMAnalyzeResponse,
    LLMTestRequest,
    LLMTestResponse,
)
from ..services.llm_client import LLMError, analyze_result, test_connection

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/test", response_model=LLMTestResponse)
async def llm_test(req: LLMTestRequest) -> LLMTestResponse:
    ok, message = await test_connection(req.base_url, req.api_key, req.model)
    return LLMTestResponse(ok=ok, message=message)


@router.post("/analyze", response_model=LLMAnalyzeResponse)
async def llm_analyze(req: LLMAnalyzeRequest) -> LLMAnalyzeResponse:
    if req.run_id is not None and db.get_run(req.run_id) is None:
        raise HTTPException(status_code=404, detail=f"Run {req.run_id} not found.")
    try:
        analysis = await analyze_result(
            req.base_url, req.api_key, req.model, req.tool, req.result
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if req.run_id is not None:
        db.update_analysis(req.run_id, analysis)
    return LLMAnalyzeResponse(analysis=analysis)
