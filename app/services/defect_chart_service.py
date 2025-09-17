# app/services/defect_chart_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from app.config.database import get_db

class DefectChartService:

    TABLE = "`AJIN_newDB`.`불량수량 및 유형`"

    # ─────────────────────────────────────────────
    # 내부: WHERE 빌더
    # ─────────────────────────────────────────────
    def _build_where(self, req):
        where_conditions = []
        params = {}

        def has_value(value):
            if value is None:
                return False
            if isinstance(value, str):
                return value.strip() != "" and value.strip().lower() != "string"
            if isinstance(value, int):
                return True
            return True

        # 날짜
        if has_value(getattr(req, "start_date", None)):
            where_conditions.append("`근무일자` >= :start_date")
            params["start_date"] = req.start_date
        if has_value(getattr(req, "end_date", None)):
            where_conditions.append("`근무일자` <= :end_date")
            params["end_date"] = req.end_date

        # 필터 (불량 테이블 스키마 기준)
        if has_value(getattr(req, "workplace", None)):
            where_conditions.append("`작업장` = :workplace")
            params["workplace"] = req.workplace
        if has_value(getattr(req, "carModel", None)):
            where_conditions.append("`차종` = :carModel")
            params["carModel"] = req.carModel
        if has_value(getattr(req, "orderType", None)):
            where_conditions.append("`수주유형` = :orderType")
            params["orderType"] = req.orderType
        if has_value(getattr(req, "defectCode", None)):
            where_conditions.append("`불량코드` = :defectCode")
            params["defectCode"] = req.defectCode
        if has_value(getattr(req, "defectType", None)):
            where_conditions.append("`불량유형` LIKE :defectType")
            params["defectType"] = f"%{str(req.defectType).strip()}%"
        if has_value(getattr(req, "worker", None)):
            where_conditions.append("`작업자` = :worker")
            params["worker"] = req.worker

        # ▼ 추가: 품번/품명
        if has_value(getattr(req, "itemCode", None)):
            where_conditions.append("`자재번호` = :itemCode")
            params["itemCode"] = req.itemCode
        if has_value(getattr(req, "itemName", None)):
            where_conditions.append("`자재명` LIKE :itemName")
            params["itemName"] = f"%{str(req.itemName).strip()}%"

        if not where_conditions:
            where_conditions.append("1=1")

        return " AND ".join(where_conditions), params

    # ─────────────────────────────────────────────
    # 자재번호/자재명 목록 (모달용)
    # ─────────────────────────────────────────────
    def get_item_codes(self, workplace: Optional[str], start_date: Optional[str], end_date: Optional[str], defectType: Optional[str] = None) -> List[Dict[str, Any]]:
        db: Session = next(get_db())
        try:
            where = ["1=1"]
            params: Dict[str, Any] = {}
            if workplace:
                where.append("`작업장` = :workplace")
                params["workplace"] = workplace
            if start_date:
                where.append("`근무일자` >= :start_date")
                params["start_date"] = start_date
            if end_date:
                where.append("`근무일자` <= :end_date")
                params["end_date"] = end_date
            if defectType:
                where.append("`불량유형` LIKE :defectType")
                params["defectType"] = f"%{str(defectType).strip()}%"

            sql = f"""
                SELECT DISTINCT
                    TRIM(`자재번호`) AS itemCode,
                    TRIM(`자재명`)   AS itemName
                FROM {self.TABLE}
                WHERE {' AND '.join(where)}
                ORDER BY itemCode
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # KPI 집계
    # ─────────────────────────────────────────────
    def get_kpis(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT
                    COALESCE(SUM(`양품수량`), 0)  AS good,
                    COALESCE(SUM(`판정대기`), 0)  AS wait_cnt,
                    COALESCE(SUM(`RWK 수량`), 0)  AS rwk_cnt,
                    COALESCE(SUM(`폐기 수량`), 0) AS scrap_cnt
                FROM {self.TABLE}
                WHERE {where_sql}
            """
            row = db.execute(text(sql), params).mappings().first() or {}
            good = int(row.get("good", 0) or 0)
            wait_cnt = int(row.get("wait_cnt", 0) or 0)
            rwk_cnt = int(row.get("rwk_cnt", 0) or 0)
            scrap_cnt = int(row.get("scrap_cnt", 0) or 0)

            defect = wait_cnt + rwk_cnt + scrap_cnt
            throughput = good + defect

            def rate(n, d): return round((n / d) * 100, 2) if d else 0.0

            return {
                "good": good,
                "defect": defect,
                "wait": wait_cnt,
                "rwk": rwk_cnt,
                "scrap": scrap_cnt,
                "throughput": throughput,
                "defectRate": rate(defect, throughput),
                "scrapRate": rate(scrap_cnt, throughput),
                "rwkRate": rate(rwk_cnt, throughput),
            }
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # 불량유형 파레토 (Top N)
    # ─────────────────────────────────────────────
    def get_by_type(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 10) or 10
            sql = f"""
                SELECT
                    `불량유형` AS type,
                    COALESCE(SUM(`판정대기`),0) + COALESCE(SUM(`RWK 수량`),0) + COALESCE(SUM(`폐기 수량`),0) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `불량유형`
                ORDER BY qty DESC
                LIMIT :top_n
            """
            params2 = {**params, "top_n": int(top_n)}
            rows = db.execute(text(sql), params2).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # 일자별 추이
    # ─────────────────────────────────────────────
    def get_trend(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT
                    DATE(`근무일자`) AS d,
                    COALESCE(SUM(`양품수량`),0)  AS good,
                    COALESCE(SUM(`판정대기`),0)  AS wait_cnt,
                    COALESCE(SUM(`RWK 수량`),0)  AS rwk_cnt,
                    COALESCE(SUM(`폐기 수량`),0) AS scrap_cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`근무일자`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            result = []
            for r in rows:
                good = int(r["good"] or 0)
                wait_cnt = int(r["wait_cnt"] or 0)
                rwk_cnt = int(r["rwk_cnt"] or 0)
                scrap_cnt = int(r["scrap_cnt"] or 0)
                defect = wait_cnt + rwk_cnt + scrap_cnt
                throughput = good + defect
                rate = round((defect / throughput) * 100, 2) if throughput else 0.0
                result.append({
                    "date": str(r["d"]),
                    "good": good,
                    "defect": defect,
                    "wait": wait_cnt,
                    "rwk": rwk_cnt,
                    "scrap": scrap_cnt,
                    "defectRate": rate
                })
            return result
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # 처분별 누적 추이 (stacked)
    # ─────────────────────────────────────────────
    def get_stacked(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT
                    DATE(`근무일자`) AS d,
                    COALESCE(SUM(`판정대기`),0)  AS wait_cnt,
                    COALESCE(SUM(`RWK 수량`),0)  AS rwk_cnt,
                    COALESCE(SUM(`폐기 수량`),0) AS scrap_cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`근무일자`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [
                {
                    "date": str(r["d"]),
                    "wait": int(r["wait_cnt"] or 0),
                    "rwk": int(r["rwk_cnt"] or 0),
                    "scrap": int(r["scrap_cnt"] or 0),
                }
                for r in rows
            ]
        finally:
            db.close()

defect_chart_service = DefectChartService()
