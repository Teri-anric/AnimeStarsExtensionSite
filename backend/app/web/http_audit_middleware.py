"""Optional structured HTTP audit logs (request/response bodies). Disabled by default — leaks secrets."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive

logger = logging.getLogger("http.audit")


def _preview_bytes(raw: bytes, max_len: int) -> str:
    if not raw:
        return ""
    truncated = len(raw) > max_len
    snippet = raw[:max_len] if truncated else raw
    text = snippet.decode("utf-8", errors="replace")
    if truncated:
        text += f"... [truncated, total {len(raw)} bytes]"
    return text


def _receive_with_body(body: bytes, receive: Receive) -> Receive:
    sent = False

    async def new_receive() -> Message:
        nonlocal sent
        if not sent:
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return await receive()

    return new_receive


class HttpAuditLogMiddleware(BaseHTTPMiddleware):
    """JSON log lines for Loki; bodies only when enabled and under size caps."""

    def __init__(self, app: ASGIApp, *, enabled: bool, max_bytes: int) -> None:
        super().__init__(app)
        self.enabled = enabled
        self.max_bytes = max_bytes

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not self.enabled:
            return await call_next(request)

        if request.url.path == "/metrics":
            return await call_next(request)

        scope = request.scope
        receive = request.receive
        req_preview: str | None = None

        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            cl_header = request.headers.get("content-length")
            if cl_header is not None:
                try:
                    cl = int(cl_header)
                except ValueError:
                    cl = self.max_bytes + 1
                if cl > self.max_bytes:
                    req_preview = f"<skipped request body {cl} bytes>"
                else:
                    body = await request.body()
                    req_preview = _preview_bytes(body, self.max_bytes)
                    receive = _receive_with_body(body, request.receive)
            else:
                body = await request.body()
                if len(body) > self.max_bytes:
                    req_preview = (
                        _preview_bytes(body[: self.max_bytes], self.max_bytes)
                        + f"... [truncated, total {len(body)} bytes]"
                    )
                else:
                    req_preview = _preview_bytes(body, self.max_bytes)
                receive = _receive_with_body(body, request.receive)

        new_request = Request(scope, receive)
        response = await call_next(new_request)

        resp_preview: str | None = None
        rcl_header = response.headers.get("content-length")
        should_read = False
        if rcl_header is not None:
            try:
                should_read = int(rcl_header) <= self.max_bytes
            except ValueError:
                should_read = False

        if should_read and hasattr(response, "body_iterator"):
            chunks: list[bytes] = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            body = b"".join(chunks)
            resp_preview = _preview_bytes(body, self.max_bytes)
            self._emit(request, response, req_preview, resp_preview)
            new_headers = MutableHeaders()
            for k, v in response.headers.items():
                if k.lower() != "content-length":
                    new_headers.append(k, v)
            return Response(
                content=body,
                status_code=response.status_code,
                headers=new_headers,
                media_type=response.media_type,
                background=getattr(response, "background", None),
            )

        raw_body = getattr(response, "body", None)
        if should_read and raw_body is not None:
            b = raw_body
            if isinstance(b, memoryview):
                b = b.tobytes()
            elif not isinstance(b, bytes):
                b = bytes(b)
            resp_preview = _preview_bytes(b, self.max_bytes)

        self._emit(request, response, req_preview, resp_preview)
        return response

    def _emit(
        self,
        request: Request,
        response: Response,
        request_body: str | None,
        response_body: str | None,
    ) -> None:
        payload = {
            "event": "http_audit",
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params),
            "request_body": request_body,
            "status": response.status_code,
            "response_body": response_body,
        }
        logger.info("", extra={"http_audit": payload})
