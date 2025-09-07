from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.inspection_modal import InspectionModalReq

# 동의어
PLANT_ALIAS = {
    "본사공장": ["본사공장", "아진산업-경산(본사)"],
    "아진산업-경산(본사)": ["본사공장", "아진산업-경산(본사)"],
}
EQUIP_ALIAS = {"1500T": ["1500T", "E라인"], "E라인": ["E라인", "1500T"]}

def _expand_alias(key: str, mapper):
    return mapper.get(key, [key]) if key else []

def _add_in(col: str, values: List[str], prefix: str, params: Dict) -> str:
    if not values:
        return "1=0"
    phs = []
    for i, v in enumerate(values):
        k = f"{prefix}{i}"
        params[k] = v
        phs.append(f":{k}")
    return f"{col} IN ({', '.join(phs)})"

class InspectionModalService:
    T_INSP = "`AJIN_newDB`.`검사내역`"
    T_PROD = "`AJIN_newDB`.`생산내역`"

    def list_items(self, req: InspectionModalReq):
        """검사내역을 기준으로, 상위필터/기간/검색어를 반영한 품번/품명 목록."""
        db: Session = next(get_db())
        try:
            where, p = [], {}

            # 기간(보고일)
            if req.start_date:
                where.append("i.`보고일` >= :sd"); p["sd"] = req.start_date
            if req.end_date:
                where.append("i.`보고일` < DATE_ADD(:ed, INTERVAL 1 DAY)"); p["ed"] = req.end_date

            # 공장/공정/설비
            if req.plant:
                where.append(_add_in("i.`공장`", _expand_alias(req.plant, PLANT_ALIAS), "pl_", p))
            if req.process:
                where.append("i.`공정` = :proc"); p["proc"] = req.process
            if req.equipment:
                where.append(_add_in("i.`설비`", _expand_alias(req.equipment, EQUIP_ALIAS), "eq_", p))

            # 검색어 (품번/품명)
            if req.q and req.q.strip():
                p["q"] = f"%{req.q.strip()}%"
                where.append("(i.`품번` LIKE :q OR s.`자재명` LIKE :q)")

            if not where:
                where.append("1=1")
            wsql = " AND ".join(where)

            sql = f"""
                SELECT DISTINCT
                    i.`품번`                 AS 품목번호,
                    COALESCE(s.`자재명`, '') AS 품목명
                FROM {self.T_INSP} i
                LEFT JOIN {self.T_PROD} s
                  ON  CAST(s.`자재번호` AS CHAR CHARACTER SET utf8mb4) COLLATE utf8mb4_general_ci
                   = CAST(i.`품번`     AS CHAR CHARACTER SET utf8mb4) COLLATE utf8mb4_general_ci
                 AND DATE(s.`근무일자`) = DATE(i.`보고일`)
                 AND (
                        (s.`플랜트` COLLATE utf8mb4_general_ci = i.`공장` COLLATE utf8mb4_general_ci)
                     OR (s.`플랜트` IN ('본사공장','아진산업-경산(본사)') AND i.`공장` IN ('본사공장','아진산업-경산(본사)'))
                     )
                 AND (
                        (s.`작업장` COLLATE utf8mb4_general_ci = i.`설비` COLLATE utf8mb4_general_ci)
                     OR (s.`작업장` IN ('1500T','E라인') AND i.`설비` IN ('1500T','E라인'))
                     )
                WHERE {wsql}
                ORDER BY i.`품번`
                LIMIT 300
            """
            return [dict(r) for r in db.execute(text(sql), p).mappings().all()]
        finally:
            db.close()

inspection_modal_service = InspectionModalService()
