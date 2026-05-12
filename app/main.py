from __future__ import annotations

import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from app.render import (
    render_api_summary,
    render_evidence,
    render_overview,
    render_queue,
)
from app.services.geo_service import build_service

app = FastAPI(
    title="SaaS Help Center GEO Optimizer",
    version="0.1.0",
    description=(
        "Scores SaaS help center content for GEO readiness, structured answer "
        "quality, and AI visibility opportunities."
    ),
)

service = build_service()


@app.get("/", response_class=HTMLResponse)
def overview() -> str:
    return render_overview()


@app.get("/queue", response_class=HTMLResponse)
def queue_page() -> str:
    return render_queue()


@app.get("/evidence", response_class=HTMLResponse)
def evidence_page() -> str:
    return render_evidence()


@app.get("/api-summary", response_class=HTMLResponse)
def api_summary_page() -> str:
    return render_api_summary()


@app.get("/api/dashboard/summary")
def dashboard_summary() -> dict:
    return service.summary()


@app.get("/api/articles")
def api_articles() -> list[dict]:
    return service.queue()


@app.get("/api/articles/{slug}")
def api_article(slug: str) -> dict:
    article = service.article(slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/api/sample")
def api_sample() -> dict:
    return service.sample_payload()


@app.get("/openapi.json")
def openapi_spec() -> JSONResponse:
    return JSONResponse(json.loads(json.dumps(app.openapi())))


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", "4617"))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False)
