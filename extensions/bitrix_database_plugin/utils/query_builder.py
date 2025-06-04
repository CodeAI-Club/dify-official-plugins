from __future__ import annotations

from typing import Any, List, Tuple

class QueryBuilder:
    """Tiny helper to build parameterized queries."""

    def __init__(self) -> None:
        self._select: List[str] = []
        self._from: str = ''
        self._where: List[str] = []
        self._params: List[Any] = []
        self._order: List[str] = []
        self._limit: int | None = None

    def select(self, *fields: str) -> 'QueryBuilder':
        self._select.extend(fields or ['*'])
        return self

    def from_table(self, table: str) -> 'QueryBuilder':
        self._from = table
        return self

    def where(self, condition: str, params: List[Any]) -> 'QueryBuilder':
        self._where.append(condition)
        self._params.extend(params)
        return self

    def order_by(self, field: str) -> 'QueryBuilder':
        self._order.append(field)
        return self

    def limit(self, value: int) -> 'QueryBuilder':
        self._limit = value
        return self

    def build(self) -> Tuple[str, List[Any]]:
        if not self._select or not self._from:
            raise ValueError('SELECT and FROM required')
        query = [f"SELECT {', '.join(self._select)}", f"FROM {self._from}"]
        if self._where:
            query.append('WHERE ' + ' AND '.join(self._where))
        if self._order:
            query.append('ORDER BY ' + ', '.join(self._order))
        if self._limit is not None:
            query.append(f'LIMIT {self._limit}')
        return ' '.join(query), self._params
