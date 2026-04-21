import time
from collections import defaultdict, deque

_WINDOW_SEC = 60
_MAX_IN_WINDOW = 5
_hits: dict[int, deque[float]] = defaultdict(deque)


def is_rate_limited(chat_id: int) -> bool:
    now = time.time()
    dq = _hits[chat_id]
    while dq and now - dq[0] > _WINDOW_SEC:
        dq.popleft()
    if len(dq) >= _MAX_IN_WINDOW:
        return True
    dq.append(now)
    return False
