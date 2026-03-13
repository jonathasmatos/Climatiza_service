import json
import time
import uuid
import sys
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        cid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.correlation_id = cid
        start = time.time()
        response: Response | None = None
        result = "OK"
        try:
            response = await call_next(request)
            result = "OK" if 200 <= response.status_code < 400 else "ERRO"
        except Exception:
            result = "ERRO"
            raise
        finally:
            log = {
                "endpoint": request.url.path,
                "metodo": request.method,
                "correlation_id": cid,
                "resultado": result,
                "status_code": response.status_code if response else 500,
                "duracao_ms": int((time.time() - start) * 1000),
            }
            sys.stdout.write(json.dumps(log, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        if response is not None:
            response.headers["X-Request-ID"] = cid
            if request.url.path.startswith("/auth"):
                response.headers["Cache-Control"] = "no-store"
                response.headers["Pragma"] = "no-cache"
        return response
