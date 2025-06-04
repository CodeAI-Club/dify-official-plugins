import json
from typing import Mapping

from sqlalchemy import create_engine, text
from werkzeug import Request, Response
from dify_plugin import Endpoint

QUERIES = {
    "departments": """
        SELECT s.ID as department_id, s.NAME as department_name, s.CODE as department_code,
               s.ACTIVE, s.SORT, s.DESCRIPTION, ps.NAME as parent_department
        FROM b_iblock_section s
        LEFT JOIN b_iblock_section ps ON s.IBLOCK_SECTION_ID = ps.ID
        WHERE s.IBLOCK_ID IN (2, 6, 33) AND s.ACTIVE = 'Y'
        ORDER BY s.SORT, s.NAME;
    """,
    "doctor_by_name": """
        SELECT e.ID as doctor_id, e.NAME as doctor_name, e.ACTIVE, e.PREVIEW_TEXT as description,
               e.DETAIL_TEXT as full_description, s.NAME as department_name, s.ID as department_id,
               ib.NAME as branch_name
        FROM b_iblock_element e
        LEFT JOIN b_iblock_section_element se ON e.ID = se.IBLOCK_ELEMENT_ID
        LEFT JOIN b_iblock_section s ON se.IBLOCK_SECTION_ID = s.ID
        LEFT JOIN b_iblock ib ON e.IBLOCK_ID = ib.ID
        WHERE e.ACTIVE = 'Y' AND e.NAME LIKE :doctor_name
        ORDER BY e.NAME;
    """,
    "doctors_in_department": """
        SELECT e.ID as doctor_id, e.NAME as doctor_name, e.ACTIVE, e.PREVIEW_TEXT as description,
               e.SORT, s.NAME as department_name, s.ID as department_id
        FROM b_iblock_element e
        INNER JOIN b_iblock_section_element se ON e.ID = se.IBLOCK_ELEMENT_ID
        INNER JOIN b_iblock_section s ON se.IBLOCK_SECTION_ID = s.ID
        WHERE s.ID = :department_id AND e.ACTIVE = 'Y' AND s.ACTIVE = 'Y'
        ORDER BY e.SORT, e.NAME;
    """,
}

class BtrixQueryEndpoint(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        body = r.get_json() or {}
        action = body.get("action")
        params = body.get("params", {})
        db_url = settings.get("database_url")
        if not db_url:
            return Response("Database URL not configured", status=400)
        if action not in QUERIES:
            return Response("Invalid action", status=400)
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text(QUERIES[action]), params).mappings().all()
            data = [dict(row) for row in result]
            return Response(json.dumps(data), status=200, content_type="application/json")
        except Exception as e:
            return Response(f"Error: {e}", status=500, content_type="text/plain")
