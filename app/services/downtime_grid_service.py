from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.downtimeGrid import DowntimeGridResquest

class Downtime_grid_service:

    def get_downtime_list(self, req: DowntimeGridResquest):
        db: Session = next(get_db())
        try:
            where_conditions = []
            params = {}

            def has_value(value):
                if value is None:
                    return False
                if isinstance(value, str):
                    return value.strip() != "" and value.strip().lower() != "string"
                if isinstance(value, int):
                    return value != 0
                return True

            # --- B(비가동) 테이블 기준 WHERE 조건 ---
            if has_value(req.start_work_date):
                where_conditions.append("B.`근무일자` >= :start_work_date")
                params["start_work_date"] = req.start_work_date

            if has_value(req.end_work_date):
                where_conditions.append("B.`근무일자` <= :end_work_date")
                params["end_work_date"] = req.end_work_date

            if has_value(req.plant):
                where_conditions.append("B.`플랜트` = :plant")
                params["plant"] = req.plant

            if has_value(req.worker):
                where_conditions.append("B.`책임자` = :worker")
                params["worker"] = req.worker

            if has_value(req.workplace):
                where_conditions.append("B.`작업장` = :workplace")
                params["workplace"] = req.workplace

            if has_value(req.itemCode):
                where_conditions.append("B.`자재번호` = :itemCode")
                params["itemCode"] = req.itemCode

            if has_value(req.carModel):
                where_conditions.append("B.`차종` = :carModel")
                params["carModel"] = req.carModel

            if has_value(req.downtimeCode):
                where_conditions.append("B.`비가동코드` = :downtimeCode")
                params["downtimeCode"] = req.downtimeCode

            if has_value(req.downtimeName):
                where_conditions.append("B.`비가동명` = :downtimeName")
                params["downtimeName"] = req.downtimeName

            if has_value(req.downtimeMinutes):
                where_conditions.append("B.`비가동(분)` <= :downtimeMinutes")
                params["downtimeMinutes"] = req.downtimeMinutes

            if has_value(req.note):
                where_conditions.append("B.`비고` = :note")
                params["note"] = req.note

            if has_value(req.shift):
                where_conditions.append("B.`주야구분` = :shift")
                params["shift"] = req.shift

            # ✅ 품명(productName) 필터는 A.자재명 기준
            if has_value(req.productName):
                where_conditions.append("A.`자재명` = :productName")
                params["productName"] = req.productName

            if has_value(req.itemType):
                where_conditions.append("B.`품목구분` = :itemType")
                params["itemType"] = req.itemType

            if has_value(req.categoryMain):
                where_conditions.append("B.`대분류` = :categoryMain")
                params["categoryMain"] = req.categoryMain

            if has_value(req.categorySub):
                where_conditions.append("B.`소분류` = :categorySub")
                params["categorySub"] = req.categorySub

            if not where_conditions:
                where_conditions.append("1=1")

            # --- LEFT JOIN + 서브쿼리 (자재번호별 자재명 하나만 매핑) ---
            sql = f"""
                SELECT
                    B.*,
                    A.`자재명`
                FROM `AJIN_newDB`.`비가동시간 및 현황` AS B
                LEFT JOIN (
                    SELECT 자재번호, MAX(자재명) AS 자재명
                    FROM AJIN_newDB.`생산내역`
                    GROUP BY 자재번호
                ) AS A
                ON A.`자재번호` = B.`자재번호`
                WHERE {' AND '.join(where_conditions)}
            """

            print(f"SQL: {sql}")
            print(f"파라미터: {params}")

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()

downtime_grid_service = Downtime_grid_service()