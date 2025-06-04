from __future__ import annotations

import logging
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ..utils.database_connector import DatabaseConnector, DatabaseConnectionError
from ..utils.query_builder import QueryBuilder
from ..utils.result_formatter import ResultFormatter

logger = logging.getLogger(__name__)


class GetDoctorByNameTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        name = tool_parameters.get('doctor_name', '')
        if not name:
            yield self.create_text_message('name required')
            return
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
            'e.ID as doctor_id',
            'e.NAME as doctor_name'
        ).from_table('b_iblock_element e').where(
            'e.NAME LIKE %s', [f'%{name}%']
        ).where(
            'e.ACTIVE = %s', ['Y']
        ).order_by('e.NAME').limit(20).build()
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
