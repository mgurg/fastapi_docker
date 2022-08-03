import functools
import time
import tracemalloc
from functools import wraps
from time import perf_counter, strftime


def trycatch(func):
    """Wraps the decorated function in a try-catch. If function fails print out the exception."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except Exception as e:
            print(f"Exception in {func.__name__}: {e}")

    return wrapper


def performance_check(func):
    """Measure performance of a function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = time.perf_counter()
        res = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(
            f"\nFunction:             {func.__name__} ({func.__doc__})"
            f"\nMemory usage:         {current / 10**6:.6f} MB"
            f"\nPeak memory usage:    {peak / 10**6:.6f} MB"
            f"\nDuration:             {duration:.6f} sec"
            f"\n{'-'*40}"
        )
        return res

    return wrapper


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = perf_counter()
        value = func(*args, **kwargs)
        toc = perf_counter()
        elapsed_time = toc - tic
        print(
            f"\n{func.__name__!r} finished at {strftime('%l:%M%p %Z on %b %d, %Y') } in {elapsed_time:0.4f} seconds\n"
        )
        return value

    return wrapper_timer
