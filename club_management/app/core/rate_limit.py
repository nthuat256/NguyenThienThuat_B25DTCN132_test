import time
from collections import defaultdict, deque
from fastapi import Request
from app.core.config import LOGIN_RATE_LIMIT_MAX_ATTEMPTS, LOGIN_RATE_LIMIT_WINDOW_SECONDS
from app.core.exception import TooManyLoginAttemptsException

_attempts: dict[str, deque] = defaultdict(deque)

def rate_limit_login(request: Request) -> None:
    key = f"{request.client.host}:{request.url.path}"
    now = time.monotonic()
    window = _attempts[key]

    while window and now - window[0] > LOGIN_RATE_LIMIT_WINDOW_SECONDS:
        window.popleft()

    if len(window) >= LOGIN_RATE_LIMIT_MAX_ATTEMPTS:
        raise TooManyLoginAttemptsException()

    window.append(now)
