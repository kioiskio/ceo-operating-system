"""Async client for OpenAI-compatible chat-completions endpoints."""

from __future__ import annotations

from typing import Any

import httpx

TIMEOUT_SECONDS = 60.0
DISCLAIMER = (
    "Decision support only — not legal, tax, or investment advice. "
    "Verify with counsel and accountants."
)


class LLMError(Exception):
    """User-friendly LLM call failure."""


def _endpoint(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"


def _friendly_error(exc: Exception, base_url: str, model: str) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        if status == 401:
            return "Authentication failed (401): the API key is invalid or missing."
        if status == 403:
            return "Access denied (403): the API key lacks permission for this model."
        if status == 404:
            return (
                "Not found (404): check the base_url path and the model name "
                f"('{model}')."
            )
        if status == 429:
            return "Rate limited (429): too many requests or quota exhausted."
        return f"LLM request failed with HTTP {status}: {exc.response.text[:300]}"
    if isinstance(exc, httpx.TimeoutException):
        return f"LLM request timed out after {TIMEOUT_SECONDS:.0f}s: {exc}"
    if isinstance(exc, httpx.ConnectError):
        return f"Could not connect to {base_url}: {exc}"
    return f"LLM request failed: {exc}"


async def chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int = 1024,
) -> str:
    """Call POST {base_url}/chat/completions and return the assistant message content."""
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            resp = await client.post(_endpoint(base_url), json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as exc:
        raise LLMError(_friendly_error(exc, base_url, model)) from exc
    except httpx.HTTPError as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"Unexpected LLM response shape: {str(data)[:300]}") from exc


async def test_connection(base_url: str, api_key: str, model: str) -> tuple[bool, str]:
    """Probe an OpenAI-compatible endpoint with a minimal request."""
    try:
        await chat_completion(
            base_url,
            api_key,
            model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=8,
        )
        return True, "Connection successful."
    except LLMError as exc:
        return False, str(exc)


_SYSTEM_PROMPTS: dict[str, str] = {
    "saas-health": (
        "You are a seasoned VC and founder operating advisor. The user will give you "
        "the JSON result of a SaaS health check tool (ARR growth, churn, NRR, CAC "
        "payback, gross margin, runway, each with a GREEN/AMBER/RED rating, plus an "
        "overall score and recommendations).\n"
        "Requirements:\n"
        "- Respond entirely in English, in markdown, organized into sections;\n"
        "- Lead with the conclusion, then the supporting evidence;\n"
        "- Call out the 3 most critical risks / action items;\n"
        "- Tie the analysis to the fundraising framework: how investors read these "
        "metrics, when to start the next raise, and how runway drives fundraising "
        "cadence;\n"
        f"- End with this exact disclaimer: \"{DISCLAIMER}\""
    ),
    "equity-dilution": (
        "You are a seasoned VC and founder operating advisor. The user will give you "
        "the JSON result of an equity dilution simulation (per-round snapshots: "
        "founder ownership, cumulative investor ownership, option pool, valuations, "
        "plus a dilution summary).\n"
        "Requirements:\n"
        "- Respond entirely in English, in markdown, organized into sections;\n"
        "- Lead with the conclusion, then the supporting evidence;\n"
        "- Call out the 3 most critical risks / action items;\n"
        "- Tie the analysis to dilution and fundraising-cadence fundamentals: whether "
        "per-round dilution is healthy, who absorbs the option pool expansion, "
        "long-term founder control and board implications, and the valuation step-up "
        "needed for the next round;\n"
        f"- End with this exact disclaimer: \"{DISCLAIMER}\""
    ),
    "deck-score": (
        "You are a seasoned VC and founder operating advisor. The user will give you "
        "the JSON result of a pitch deck scoring tool (overall score, verdict, "
        "per-slide scores with missed criteria, and priority_fixes).\n"
        "Requirements:\n"
        "- Respond entirely in English, in markdown, organized into sections;\n"
        "- Lead with the conclusion, then the supporting evidence;\n"
        "- Call out the 3 most critical risks / action items;\n"
        "- Tie the analysis to the fundraising framework: the order in which "
        "investors read a deck and what they look for, and how the high-weight "
        "slides (Problem / Solution / Traction / Ask) win or lose investor "
        "conviction;\n"
        f"- End with this exact disclaimer: \"{DISCLAIMER}\""
    ),
}


async def analyze_result(
    base_url: str,
    api_key: str,
    model: str,
    tool: str,
    result: dict[str, Any],
) -> str:
    """Run an advisor-style analysis of a tool result. Raises LLMError on failure."""
    import json

    system_prompt = _SYSTEM_PROMPTS[tool]
    user_content = (
        "Here is the tool result JSON. Analyze it per the system instructions:\n\n"
        f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"
    )
    return await chat_completion(
        base_url,
        api_key,
        model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=2048,
    )
