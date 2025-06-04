from __future__ import annotations

from typing import Any, List, Dict


class ResultFormatter:
    def format_results(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            'success': True,
            'row_count': len(rows),
            'data': rows,
        }
