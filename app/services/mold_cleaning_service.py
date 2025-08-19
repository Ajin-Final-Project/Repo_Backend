from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.mold_cleaning import MoldCleaningCycleRequest

class Mold_cleaning_service:

    def get_moldCleaning_list(self, req: MoldCleaningCycleRequest):
        db: Session = next(get_db())
        try:
            where_conditions = []
            params = {}

            def has_value(value):
                if value is None:
                    return False
                if isinstance(value, str):
                    s = value.strip()
                    return s != "" and s.lower() != "string"
                return True

            # ===== 문자열 조건 =====
            if has_value(req.equipment_detail):
                where_conditions.append("`설비내역` LIKE :equipment_detail")
                params["equipment_detail"] = f"%{req.equipment_detail.strip()}%"

            if has_value(req.order_type):
                where_conditions.append("`오더유형` LIKE :order_type")
                params["order_type"] = f"%{req.order_type.strip()}%"

            if has_value(req.order_type_detail):
                where_conditions.append("`오더유형내역` LIKE :order_type_detail")
                params["order_type_detail"] = f"%{req.order_type_detail.strip()}%"

            if has_value(req.order_detail):
                where_conditions.append("`오더내역` LIKE :order_detail")
                params["order_detail"] = f"%{req.order_detail.strip()}%"

            if has_value(req.action_detail):
                where_conditions.append("`조치내용` LIKE :action_detail")
                params["action_detail"] = f"%{req.action_detail.strip()}%"

            # ===== 날짜 범위 조건 =====
            if has_value(req.startDate) and has_value(req.endDate):
                where_conditions.append("`기본시작일` >= :startDate AND `기본종료일` <= :endDate")
                params["startDate"] = req.startDate
                params["endDate"] = req.endDate
            elif has_value(req.startDate):  # 시작일만 있을 경우
                where_conditions.append("`기본시작일` >= :startDate")
                params["startDate"] = req.startDate
            elif has_value(req.endDate):    # 종료일만 있을 경우
                where_conditions.append("`기본종료일` <= :endDate")
                params["endDate"] = req.endDate

            # WHERE 조건 없을 때 전체 조회
            if not where_conditions:
                where_conditions.append("1=1")

            sql = f"""
                SELECT *
                FROM `AJIN_newDB`.`금형세척주기`
                WHERE {' AND '.join(where_conditions)}
            """

            print("SQL:", sql)
            print("Params:", params)

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()

mold_cleaning_service = Mold_cleaning_service()
