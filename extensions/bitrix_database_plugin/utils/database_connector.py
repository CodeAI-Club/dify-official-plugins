from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, Optional

import pymysql

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    pass


class DatabaseConnector:
    """Simple connector with context-managed connections."""

    def __init__(self, host: str, port: int, database: str, user: str, password: str,
                 use_ssl: bool = False, timeout: int = 30):
        self.params = dict(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=timeout,
            read_timeout=timeout,
            write_timeout=timeout,
            charset='utf8mb4',
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )
        if use_ssl:
            self.params['ssl'] = {'ssl': True}

    @contextmanager
    def get_connection(self) -> Generator[pymysql.connections.Connection, None, None]:
        try:
            conn = pymysql.connect(**self.params)
        except Exception as exc:
            raise DatabaseConnectionError(str(exc)) from exc
        try:
            yield conn
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def close(self) -> None:
        pass
