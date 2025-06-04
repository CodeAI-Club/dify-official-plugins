from __future__ import annotations

import logging
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ..utils.database_connector import DatabaseConnector, DatabaseConnectionError
from ..utils.query_builder import QueryBuilder
from ..utils.result_formatter import ResultFormatter

logger = logging.getLogger(__name__)


class GetDepartmentsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        credentials = self.runtime.credentials
        connector = DatabaseConnector(
            host=credentials['database_host'],
            port=int(credentials['database_port']),
            database=credentials['database_name'],
            user=credentials['database_user'],
            password=credentials['database_password'],
            use_ssl=credentials.get('use_ssl', False),
        )
        builder = QueryBuilder()
        sql, params = builder.select(
            's.ID as department_id',
            's.NAME as department_name'
        ).from_table('b_iblock_section s').where(
            's.ACTIVE = %s', ['Y']
        ).order_by('s.SORT').build()
        try:
            with connector.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()
            formatter = ResultFormatter()
            yield self.create_json_message(formatter.format_results(rows))
        except DatabaseConnectionError as exc:
            yield self.create_text_message(str(exc))
        finally:
            connector.close()
