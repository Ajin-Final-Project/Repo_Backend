from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.defectGrid import DefectGridRequest

class Defect_grid_service:

    def get_defect_list(self, req: DefectGridRequest):
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

            # 날짜
            if has_value(req.start_work_date):
                where_conditions.append("`근무일자` >= :start_work_date")
                params["start_work_date"] = req.start_work_date

            if has_value(req.end_work_date):
                where_conditions.append("`근무일자` <= :end_work_date")
                params["end_work_date"] = req.end_work_date

            # 텍스트/식별자
            if has_value(req.workplace):
                where_conditions.append("`작업장` = :workplace")
                params["workplace"] = req.workplace

            if has_value(req.itemInfo):
                # 부분 검색 가능하도록 LIKE
                where_conditions.append("`자재정보` LIKE :itemInfo")
                params["itemInfo"] = f"%{req.itemInfo.strip()}%"

            if has_value(req.carModel):
                where_conditions.append("`차종` = :carModel")
                params["carModel"] = req.carModel

            if has_value(req.orderType):
                where_conditions.append("`수주유형` = :orderType")
                params["orderType"] = req.orderType

            if has_value(req.defectCode):
                where_conditions.append("`불량코드` = :defectCode")
                params["defectCode"] = req.defectCode

            if has_value(req.defectType):
                where_conditions.append("`불량유형` LIKE :defectType")
                params["defectType"] = f"%{req.defectType.strip()}%"

            if has_value(req.remark):
                where_conditions.append("`비고` LIKE :remark")
                params["remark"] = f"%{req.remark.strip()}%"

            if has_value(req.worker):
                where_conditions.append("`작업자` = :worker")
                params["worker"] = req.worker

            # 수량
            if has_value(req.goodItemCount):
                where_conditions.append("`양품수량` = :goodItemCount")
                params["goodItemCount"] = req.goodItemCount

            if has_value(req.waitItemCount):
                where_conditions.append("`판정대기` = :waitItemCount")
                params["waitItemCount"] = req.waitItemCount

            if has_value(req.rwkCount):
                where_conditions.append("`RWK 수량` = :rwkCount")
                params["rwkCount"] = req.rwkCount

            if has_value(req.scrapCount):
                where_conditions.append("`폐기 수량` = :scrapCount")
                params["scrapCount"] = req.scrapCount

            # WHERE 기본
            if not where_conditions:
                where_conditions.append("1=1")

            # 최종 SQL
            sql = f"""
                SELECT *
                FROM `AJIN_newDB`.`불량수량 및 유형`
                WHERE {' AND '.join(where_conditions)}
            """

            print(f"[DefectGrid] SQL: {sql}")
            print(f"[DefectGrid] PARAMS: {params}")

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()

defect_grid_service = Defect_grid_service()
