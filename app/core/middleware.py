"""Middleware: идентификатор запроса, логирование и простой rate limit."""

import logging
import time
import uuid
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("app.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Проставляет заголовок ``X-Request-ID`` и логирует каждый запрос."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "%s %s -> %s (%.1f ms) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Лимит запросов на IP по скользящему окну в 60 секунд."""

    def __init__(self, app, limit_per_minute: int) -> None:
        super().__init__(app)
        self.limit = limit_per_minute
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if self.limit <= 0:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = self.hits[client_ip]
        while window and now - window[0] > 60:
            window.popleft()

        if len(window) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Слишком много запросов, повторите позже"},
            )

        window.append(now)
        return await call_next(request)
