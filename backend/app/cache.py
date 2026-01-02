from time import time

CACHE = {}
CACHE_TTL = 60  # seconds

def invalidate_task_cache(org_id: int):
    """Invalidate all task cache entries for a specific organization."""
    keys = [k for k in CACHE if k.startswith(f"tasks:{org_id}:")]
    for k in keys:
        del CACHE[k]
