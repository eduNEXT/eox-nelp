"""eox-nelp Metrics file.

decorators:
    cache_method: Cache the result of the inner method.
"""
from django.conf import settings
from django.core.cache import cache


def cache_method(func):
    """
    Cache the function result to improve the response time.

    Args:
        func<function>: Target function to be cached.

    Return:
        <funtion>: Wrapper function.
    """
    def wrapper(*args, **kwargs):
        key = f"{func.__name__}.{'-'.join(map(str, args))}.STATS_CACHE_KEY"
        result = cache.get(key)

        if result:
            return result

        result = func(*args, **kwargs)

        cache.set(
            key,
            result,
            timeout=getattr(settings, "STATS_SETTINGS", {}).get("STATS_TIMEOUT", 3600),
        )

        return result

    return wrapper
