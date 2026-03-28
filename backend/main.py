import json
import logging
import os
import time
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Any
from starlette import status

from pdf_parser import extract_text_from_pdf, validate_pdf
from agent import run_agent, get_demo_data
from report_gen import generate_pdf_report
from settings import load_settings


settings = load_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("lexai.api")

app = FastAPI(title="LexAI - Agentic Legal Case Analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def make_error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def raise_api_error(status_code: int, code: str, message: str) -> None:
    raise HTTPException(status_code=status_code, detail={"code": code, "message": message})


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))

    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.request_max_body_bytes:
        return make_error_response(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            code="request_too_large",
            message="Request size exceeds server limit.",
        )

    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["x-request-id"] = request_id
    response.headers["x-process-time-ms"] = f"{elapsed_ms:.2f}"

    logger.info(
        "%s %s -> %s (%.2f ms) [%s]",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        request_id,
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return make_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="invalid_request",
        message="Request validation failed.",
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        return make_error_response(exc.status_code, detail["code"], detail["message"])
    message = str(detail) if detail else "Request failed."
    return make_error_response(exc.status_code, "request_failed", message)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error on %s", request.url.path)
    return make_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_error",
        message="Unexpected server error.",
    )


class AnalysisRequest(BaseModel):
    analysis: dict[str, Any]


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "LexAI Legal Analysis API",
        "profile": settings.env_profile,
    }


@app.get("/ready")
async def readiness_check():
    if settings.readiness_require_groq and not os.getenv("GROQ_API_KEY"):
        raise_api_error(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="dependency_unavailable",
            message="GROQ_API_KEY is required but not configured.",
        )
    mode = "live" if os.getenv("GROQ_API_KEY") else "demo"
    return {
        "status": "ready",
        "mode": mode,
        "profile": settings.env_profile,
    }


@app.post("/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise_api_error(status.HTTP_400_BAD_REQUEST, "invalid_file_type", "Please upload PDF files only")
    try:
        file_bytes = await file.read()
        validate_pdf(file_bytes, file.filename)
    except ValueError as e:
        raise_api_error(status.HTTP_400_BAD_REQUEST, "invalid_pdf", str(e))
    try:
        text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise_api_error(status.HTTP_400_BAD_REQUEST, "pdf_parse_failed", str(e))
    if not os.getenv("GROQ_API_KEY"):
        demo = get_demo_data()
        demo["_demo_note"] = "GROQ_API_KEY not set. Returning demo analysis."
        demo["_mode"] = "demo"
        return demo
    try:
        results = await run_agent(text)
        return results
    except Exception as e:
        raise_api_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "analysis_failed",
            f"Analysis failed, please try again: {str(e)}",
        )


@app.post("/report")
async def generate_report(request: AnalysisRequest):
    try:
        pdf_bytes = generate_pdf_report(request.analysis)
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=lexai-report.pdf"},
        )
    except Exception as e:
        raise_api_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "report_generation_failed",
            f"Report generation failed: {str(e)}",
        )


@app.get("/demo")
async def get_demo():
    demo = get_demo_data()
    demo["_mode"] = "demo"
    return demo


@app.get("/analyze-stream")
async def analyze_stream_demo():
    """SSE endpoint that streams demo analysis progress."""
    demo = get_demo_data()
    demo["_mode"] = "demo"

    async def event_generator():
        import asyncio
        for i in range(9):
            from agent import STEP_LABELS, STEP_ICONS
            icon = STEP_ICONS[i] if i < len(STEP_ICONS) else "\u2699\ufe0f"
            label = STEP_LABELS[i] if i < len(STEP_LABELS) else "Processing..."
            data = json.dumps({"step": i + 1, "total": 9, "label": label, "icon": icon})
            yield f"data: {data}\n\n"
            await asyncio.sleep(1.2)
        final = json.dumps({"step": 9, "total": 9, "label": "Analysis complete!", "icon": "\u2705", "result": demo})
        yield f"data: {final}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/analyze-stream-upload")
async def analyze_stream_upload(file: UploadFile = File(...)):
    """SSE endpoint that streams analysis progress for an uploaded PDF."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise_api_error(status.HTTP_400_BAD_REQUEST, "invalid_file_type", "Please upload PDF files only")

    file_bytes = await file.read()
    try:
        validate_pdf(file_bytes, file.filename)
        text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise_api_error(status.HTTP_400_BAD_REQUEST, "invalid_pdf", str(e))

    import asyncio
    from agent import STEP_LABELS, STEP_ICONS

    async def event_generator():
        if not os.getenv("GROQ_API_KEY"):
            demo = get_demo_data()
            demo["_mode"] = "demo"
            demo["_demo_note"] = "GROQ_API_KEY not set. Returning demo analysis."
            for i in range(9):
                icon = STEP_ICONS[i] if i < len(STEP_ICONS) else "\u2699\ufe0f"
                label = STEP_LABELS[i] if i < len(STEP_LABELS) else "Processing..."
                data = json.dumps({"step": i + 1, "total": 9, "label": label, "icon": icon})
                yield f"data: {data}\n\n"
                await asyncio.sleep(1.2)
            final = json.dumps({"step": 9, "total": 9, "label": "Analysis complete!", "icon": "\u2705", "result": demo})
            yield f"data: {final}\n\n"
        else:
            queue = asyncio.Queue()

            async def on_step(idx: int):
                await queue.put(idx)

            async def run_analysis():
                try:
                    results = await run_agent(text, progress_callback=on_step)
                    await queue.put(("done", results))
                except Exception as e:
                    await queue.put(("error", str(e)))

            asyncio.create_task(run_analysis())
            last_step = -1

            while True:
                item = await queue.get()
                if isinstance(item, tuple):
                    if item[0] == "done":
                        final = json.dumps({"step": 9, "total": 9, "label": "Analysis complete!", "icon": "\u2705", "result": item[1]})
                        yield f"data: {final}\n\n"
                        break
                    elif item[0] == "error":
                        err = json.dumps({"step": -1, "total": 9, "label": f"Error: {item[1]}", "icon": "\u274c"})
                        yield f"data: {err}\n\n"
                        break
                elif isinstance(item, int) and item != last_step:
                    last_step = item
                    icon = STEP_ICONS[item] if item < len(STEP_ICONS) else "\u2699\ufe0f"
                    label = STEP_LABELS[item] if item < len(STEP_LABELS) else "Processing..."
                    data = json.dumps({"step": item + 1, "total": 9, "label": label, "icon": icon})
                    yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
