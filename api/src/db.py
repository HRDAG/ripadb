"""Database connection pool for the API."""

import os
from contextlib import contextmanager

import psycopg
from psycopg_pool import ConnectionPool

DATABASE_URL = os.environ.get("DATABASE_URL", "dbname=ripadb")

pool: ConnectionPool | None = None


def init_pool():
    global pool
    pool = ConnectionPool(DATABASE_URL, min_size=2, max_size=10)


def close_pool():
    global pool
    if pool:
        pool.close()
        pool = None


@contextmanager
def get_conn():
    with pool.connection() as conn:
        yield conn
