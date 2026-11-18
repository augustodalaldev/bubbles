import zlib
from collections.abc import Iterator
from contextlib import contextmanager

from django.db import connection


def _key(name: str) -> int:
    # crc32 is always < 2**32, so it fits PostgreSQL's bigint advisory-lock key.
    return zlib.crc32(name.encode())


@contextmanager
def advisory_lock(name: str, *, wait: bool = True) -> Iterator[bool]:
    """Cross-process mutual exclusion for periodic jobs (PostgreSQL session advisory lock).

    With `wait=True` it blocks until the lock is free and always yields True.
    With `wait=False` it yields False immediately when another process holds the lock.
    The lock is session-level, so it survives the short transactions used inside the job and
    is released when the block exits (or when the connection dies).
    """
    key = _key(name)
    with connection.cursor() as cursor:
        if wait:
            cursor.execute("SELECT pg_advisory_lock(%s)", [key])
            acquired = True
        else:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [key])
            acquired = bool(cursor.fetchone()[0])
    try:
        yield acquired
    finally:
        if acquired:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [key])
