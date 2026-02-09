import asyncio
import json
import random
import time
import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException, Request
from starlette.responses import Response

from .config import settings
from .utils import utils

LOG_HEADER_ALLOWLIST = {
    "accept",
    "accept-encoding",
    "accept-language",
    "cache-control",
    "content-length",
    "content-type",
    "etag",
    "user-agent",
    "x-device",
    "x-lang",
    "x-forwarded-for",
    "x-real-ip",
    "x-request-id",
}


def _filter_headers(headers: dict) -> dict:
    return {key: value for key, value in headers.items() if key in LOG_HEADER_ALLOWLIST}


def _ensure_api_logger(request: Request) -> None:
    api_log_date = date.today().strftime("%Y%m%d")
    if getattr(request.app.state, "api_log_date", None) != api_log_date:
        request.app.state.api_logger = utils.create_log("api")
        request.app.state.api_log_date = api_log_date


def _get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _get_user_name(request: Request) -> str | None:
    user_name = getattr(request.state, "user", None)
    if user_name:
        return user_name
    return request.headers.get("x-user") or request.headers.get("x-auth-user")


def _get_body_size(request: Request) -> int | None:
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit():
        return int(content_length)
    return None


def _coerce_body_bytes(body) -> bytes | None:
    if body is None:
        return None
    if isinstance(body, (bytes, bytearray)):
        return bytes(body)
    return str(body).encode()


def _truncate_body(body_bytes: bytes) -> bytes:
    if settings.log_db_max_body_bytes > 0 and len(body_bytes) > settings.log_db_max_body_bytes:
        return body_bytes[: settings.log_db_max_body_bytes] + b"...[truncated]"
    return body_bytes


def _body_to_text(body_bytes: bytes | None) -> str | None:
    if not body_bytes:
        return None
    return _truncate_body(body_bytes).decode("utf-8", errors="replace")


def _get_response_size(response_body: bytes | None) -> int | None:
    if not response_body:
        return None
    try:
        return len(response_body)
    except TypeError:
        return None


async def _capture_response_body(response):
    if response is None:
        return None, None
    body = getattr(response, "body", None)
    if body is not None:
        return response, _coerce_body_bytes(body)
    body_iterator = getattr(response, "body_iterator", None)
    if body_iterator is None:
        return response, None

    chunks: list[bytes] = []
    async for chunk in body_iterator:
        if isinstance(chunk, (bytes, bytearray)):
            chunks.append(bytes(chunk))
        else:
            chunks.append(str(chunk).encode())
    body_bytes = b"".join(chunks)
    headers = dict(response.headers)
    headers.pop("content-length", None)
    new_response = Response(
        content=body_bytes,
        status_code=response.status_code,
        headers=headers,
        media_type=response.media_type,
        background=response.background,
    )
    return new_response, body_bytes


def _build_log_record(
    request: Request,
    response,
    response_body: bytes | None,
    request_id: uuid.UUID,
    status_code: int,
    duration_ms: int,
    error: Exception | None,
    request_body: bytes,
):
    request_headers = _filter_headers({key.lower(): value for key, value in request.headers.items()})
    response_headers = None
    response_body_text = None
    if response is not None:
        response_headers = _filter_headers({key.lower(): value for key, value in response.headers.items()})
        response_body_text = _body_to_text(response_body)

    return {
        "ts": datetime.now(timezone.utc),
        "method": request.method,
        "endpoint": request.url.path,
        "status": status_code,
        "duration_ms": duration_ms,
        "user_name": _get_user_name(request),
        "request_id": request_id,
        "client_ip": _get_client_ip(request),
        "query_params": dict(request.query_params),
        "body_size": _get_body_size(request),
        "response_size": _get_response_size(response_body),
        "request_headers": request_headers,
        "request_body": _body_to_text(request_body),
        "response_headers": response_headers,
        "response_body": response_body_text,
        "error": str(error) if error else None,
    }


def _should_log_db() -> bool:
    if not settings.log_db_enabled or settings.log_db_sample_rate <= 0.0:
        return False
    return settings.log_db_sample_rate >= 1.0 or random.random() <= settings.log_db_sample_rate


async def request_logging_middleware(request: Request, call_next):
    start = time.monotonic()
    request_id = uuid.uuid4()
    request.state.request_id = request_id
    token = utils.REQUEST_ID_CTX.set(request_id)
    request_body = await request.body()

    response = None
    response_body = None
    status_code = 500
    error = None
    try:
        response = await call_next(request)
        status_code = response.status_code
    except HTTPException as exc:
        status_code = exc.status_code
        error = exc
        raise
    except Exception as exc:  # noqa: BLE001
        status_code = 500
        error = exc
        raise
    finally:
        utils.REQUEST_ID_CTX.reset(token)
        duration_ms = int((time.monotonic() - start) * 1000)
        response, response_body = await _capture_response_body(response)
        _ensure_api_logger(request)
        log_record = _build_log_record(
            request=request,
            response=response,
            response_body=response_body,
            request_id=request_id,
            status_code=status_code,
            duration_ms=duration_ms,
            error=error,
            request_body=request_body,
        )

        api_logger = getattr(request.app.state, "api_logger", None)
        if api_logger:
            api_logger.info(json.dumps(log_record, default=str))

        if _should_log_db():
            asyncio.create_task(utils.insert_api_log(request.app.state.db_manager, log_record))

        if response is not None:
            response.headers["X-Request-ID"] = str(request_id)

    return response
