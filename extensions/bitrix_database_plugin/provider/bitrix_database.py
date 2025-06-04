from __future__ import annotations

import logging
from typing import Any, Generator

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from ..utils.database_connector import DatabaseConnector, DatabaseConnectionError

logger = logging.getLogger(__name__)


class BitrixDatabaseProvider(ToolProvider):
    """Provider for Bitrix database tools."""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        required = [
            'database_host', 'database_port', 'database_name',
            'database_user', 'database_password'
        ]
        missing = [key for key in required if not credentials.get(key)]
        if missing:
            raise ToolProviderCredentialValidationError(
                f"Missing required fields: {', '.join(missing)}")

        try:
            connector = DatabaseConnector(
                host=credentials['database_host'],
                port=int(credentials['database_port']),
                database=credentials['database_name'],
                user=credentials['database_user'],
                password=credentials['database_password'],
                use_ssl=credentials.get('use_ssl', False),
            )
            with connector.get_connection():
                pass
        except DatabaseConnectionError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc
        finally:
            connector.close()
