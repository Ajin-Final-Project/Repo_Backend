# app/services/inspection_grid_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.inspectionGrid import inspectionGridRequest
from decimal import Decimal
from typing import Dict, List, Any

# 문자열 비교 collation (환경에 맞게 하나로 고정)
COLL = "utf8mb4_general_ci"  # 또는 "utf8mb4_0900_ai_ci"

# 기준 테이블
DB_NAME = "AJIN_newDB"
TABLE_NAME = "생산_검사"
T_INSP = f"`{DB_NAME}`.`{TABLE_NAME}`"

# ------------------------ 동의어 매핑 ------------------------
SYNONYMS = {
    # 공장
    "plant": {
        "본사공장": ["본사공장", "아진산업-경산(본사)", "아진산업-본사(경산)"],
        "아진산업-경산(본사)": ["본사공장", "아진산업-경산(본사)", "아진산업-본사(경산)"],
        "아진산업-본사(경산)": ["본사공장", "아진산업-경산(본사)", "아진산업-본사(경산)"],
    },
    # 설비
    "equipment": {
        "E라인": ["E라인", "1500T", "1500T(E라인)"],
        "1500T": ["E라인", "1500T", "1500T(E라인)"],
        "1500T(E라인)": ["E라인", "1500T", "1500T(E라인)"],
    },
}

def expand_vals(kind: str, val: str) -> List[str]:
    if val is None or str(val).strip() == "":
        return []
    val = str(val).strip()
    return SYNONYMS.get(kind, {}).get(val, [val])

def _col(col_sql: str) -> str:
    return f"{col_sql} COLLATE {COLL}"

def _in_clause(col_sql: str, values: List[str], params: Dict[str, Any], base_name: str) -> str:
    if not values:
        return "1=0"
    if len(values) == 1:
        pname = f"{base_name}_0"
        params[pname] = values[0]
        return f"{_col(col_sql)} = :{pname}"
    placeholders = []
    for idx, v in enumerate(values):
        pname = f"{base_name}_{idx}"
        params[pname] = v
        placeholders.append(f":{pname}")
    return f"{_col(col_sql)} IN ({', '.join(placeholders)})"

# ===== 컬럼 캐시 (i.* 대신 명시적 컬럼 리스트 생성) =====
_ALL_COLS_CACHE: List[str] = []

def _clean_col(col: str) -> str:
    """제로폭/제어문자/앞뒤 공백 제거하여 안전한 별칭 사용"""
    if col is None:
        return ""
    return (
        str(col)
        .replace("\u00A0", "")    # NBSP
        .replace("\u200b", "")    # zero width space
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\ufeff", "")    # BOM
        .strip()
    )

def _load_table_columns(db: Session) -> List[str]:
    """
    INFORMATION_SCHEMA에서 컬럼명을 순서대로 가져와 백틱으로 감싼다.
    가져온 이름은 반드시 정규화(clean)하여 별칭에도 동일 적용한다.
    한 번 읽어온 목록은 프로세스 동안 캐시한다.
    """
    global _ALL_COLS_CACHE
    if _ALL_COLS_CACHE:
        return _ALL_COLS_CACHE

    sql = """
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :tbl
    ORDER BY ORDINAL_POSITION
    """
    rows = db.execute(text(sql), {"db": DB_NAME, "tbl": TABLE_NAME}).fetchall()

    cols: List[str] = []
    for r in rows:
        raw = r[0]
        col = _clean_col(raw)
        # 원본/별칭 모두 동일한 정규화된 이름을 사용
        cols.append(f"i.`{col}` AS `{col}`")

    _ALL_COLS_CACHE = cols
    return _ALL_COLS_CACHE


class Inspection_grid_service:
    @staticmethod
    def _has_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() not in ("", "string")
        if isinstance(value, (int, Decimal, float)):
            return True
        return True

    # ======================== 메인 목록 ========================
    def get_inspection_list(self, req: inspectionGridRequest):
        """
        `생산_검사` 단일 테이블에서 직접 조회.
        - 모든 컬럼을 명시적으로 선택(Information_Schema 기반)해 맵핑 누락 방지.
        - WHERE 절은 실제 존재하는 컬럼만 사용 (plant, process, equipment, work_date, 자재번호 등)
        """
        db: Session = next(get_db())
        try:
            hv = self._has_value
            where_sql: List[str] = []
            params: Dict[str, Any] = {}

            # ===== 차트식/그리드식 alias 매핑 =====
            start_date = getattr(req, "start_work_date", None) or getattr(req, "start_date", None)
            end_date   = getattr(req, "end_work_date", None)   or getattr(req, "end_date", None)

            plant_req   = getattr(req, "plant", None) or getattr(req, "factory", None)
            process_req = getattr(req, "process", None)
            equip_req   = getattr(req, "equipment", None)
            item_no_req = getattr(req, "itemNumber", None) or getattr(req, "partNo", None)

            # ===== 실제 사용 컬럼(WHERE에서 쓰는 것들) =====
            c_plant       = "i.`plant`"
            c_process     = "i.`process`"
            c_equipment   = "i.`equipment`"
            c_item_no     = "i.`자재번호`"
            c_report_date = "i.`work_date`"

            # ===== 기간 ===== (값이 있을 때만 필터)
            if hv(start_date):
                where_sql.append(f"DATE({c_report_date}) >= :sd")
                params["sd"] = start_date
            if hv(end_date):
                where_sql.append(f"DATE({c_report_date}) <= :ed")
                params["ed"] = end_date

            # ===== 상위 필터 =====
            if hv(plant_req):
                plant_vals = expand_vals("plant", plant_req)
                where_sql.append(_in_clause(c_plant, plant_vals, params, "plant_vals"))
            if hv(process_req):
                params["process"] = process_req
                where_sql.append(f"{_col(c_process)} = :process")
            if hv(equip_req):
                equip_vals = expand_vals("equipment", equip_req)
                where_sql.append(_in_clause(c_equipment, equip_vals, params, "equip_vals"))
            if hv(item_no_req):
                params["itemNumber"] = item_no_req
                where_sql.append(f"{_col(c_item_no)} = :itemNumber")

            if not where_sql:
                where_sql.append("1=1")  # 전체 데이터

            # ===== 명시적 컬럼 리스트 =====
            select_cols = ", ".join(_load_table_columns(db))

            sql = f"""
            SELECT
              {select_cols}
            FROM {T_INSP} i
            WHERE {" AND ".join(where_sql)}
            ORDER BY COALESCE(i.`work_date`, '1900-01-01') DESC, i.`id` DESC
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    # ======================== 옵션: 전부 생산_검사에서 DISTINCT ========================
    def _distinct_from_insp(self, col_expr: str, req: inspectionGridRequest) -> List[str]:
        db: Session = next(get_db())
        try:
            hv = self._has_value
            where: List[str] = []
            params: Dict[str, Any] = {}

            start_date = getattr(req, "start_work_date", None) or getattr(req, "start_date", None)
            end_date   = getattr(req, "end_work_date", None)   or getattr(req, "end_date", None)
            plant_req   = getattr(req, "plant", None) or getattr(req, "factory", None)
            process_req = getattr(req, "process", None)
            equip_req   = getattr(req, "equipment", None)

            c_plant       = "i.`plant`"
            c_process     = "i.`process`"
            c_equipment   = "i.`equipment`"
            c_report_date = "i.`work_date`"

            if hv(start_date):
                where.append(f"DATE({c_report_date}) >= :sd")
                params["sd"] = start_date
            if hv(end_date):
                where.append(f"DATE({c_report_date}) <= :ed")
                params["ed"] = end_date

            if hv(plant_req):
                plant_vals = expand_vals("plant", plant_req)
                where.append(_in_clause(c_plant, plant_vals, params, "plant_vals"))
            if hv(process_req):
                params["process"] = process_req
                where.append(f"{_col(c_process)} = :process")
            if hv(equip_req):
                equip_vals = expand_vals("equipment", equip_req)
                where.append(_in_clause(c_equipment, equip_vals, params, "equip_vals"))

            if not where:
                where.append("1=1")

            sql = f"""
            SELECT DISTINCT {col_expr} AS val
            FROM {T_INSP} i
            WHERE {" AND ".join(where)}
            ORDER BY val
            """
            rows = db.execute(text(sql), params).fetchall()
            return [r[0] for r in rows if r[0] is not None and str(r[0]).strip() != ""]
        finally:
            db.close()

    # ----- 옵션 API들 -----
    def get_distinct_plants(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_from_insp("i.`plant`", req)

    def get_distinct_processes(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_from_insp("i.`process`", req)

    def get_distinct_equipments(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_from_insp("i.`equipment`", req)

    def get_distinct_part_nos(self, req: inspectionGridRequest) -> List[str]:
        # 품번 컬럼 없음 → 자재번호 사용
        return self._distinct_from_insp("i.`자재번호`", req)

    def get_distinct_part_names(self, req: inspectionGridRequest) -> List[str]:
        # 품명 컬럼 없음 → 자재명 사용
        return self._distinct_from_insp("i.`자재명`", req)


inspection_grid_service = Inspection_grid_service()
