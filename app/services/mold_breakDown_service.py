from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.mold_BreakDown import MoldBreakdownRequest

class Mold_breakDown_service:

    def get_moldBreakDown_list(self, req: MoldBreakdownRequest):
        db: Session = next(get_db())
        try:
            where = []
            params = {}

            def has_value(v):
                if v is None:
                    return False
                if isinstance(v, str):
                    s = v.strip()
                    return s != "" and s.lower() != "string"
                return True

            # === 정확 일치(=) ===
            if has_value(req.status):
                where.append("`상태` = :status")
                params["status"] = req.status.strip()

            if has_value(req.document):
                where.append("`문서` = :document")
                params["document"] = req.document.strip()

            if has_value(req.function_location):
                where.append("`기능위치` = :function_location")
                params["function_location"] = req.function_location.strip()

            if req.equipment is not None:
                where.append("`설비` = :equipment")
                params["equipment"] = req.equipment

            if has_value(req.order_type):
                where.append("`오더유형` = :order_type")
                params["order_type"] = req.order_type.strip()

            if has_value(req.order_type_detail):
                where.append("`오더유형내역` = :order_type_detail")
                params["order_type_detail"] = req.order_type_detail.strip()

            if req.order_no is not None:
                where.append("`오더번호` = :order_no")
                params["order_no"] = req.order_no

            if req.notification_no is not None:
                where.append("`통지번호` = :notification_no")
                params["notification_no"] = req.notification_no

            # === 부분 일치(LIKE) ===
            if has_value(req.function_location_detail):
                where.append("`기능위치내역` LIKE :function_location_detail")
                params["function_location_detail"] = f"%{req.function_location_detail.strip()}%"

            if has_value(req.equipment_detail):
                where.append("`설비내역` LIKE :equipment_detail")
                params["equipment_detail"] = f"%{req.equipment_detail.strip()}%"

            if has_value(req.order_detail):
                where.append("`오더내역` LIKE :order_detail")
                params["order_detail"] = f"%{req.order_detail.strip()}%"

            if has_value(req.failure):
                where.append("`고장` LIKE :failure")
                params["failure"] = f"%{req.failure.strip()}%"

            # === 날짜 범위 ===
            # 주어진 모델은 start_date/end_date만 제공하므로
            # 기본적으로 '기본시작일/기본종료일' 중 하나라도 구간과 겹치면 조회(Overlap)하도록 처리
            if has_value(req.start_date) and has_value(req.end_date):
                where.append("""
                    (
                        (`기본시작일` BETWEEN :start_date AND :end_date)
                        OR
                        (`기본종료일` BETWEEN :start_date AND :end_date)
                        OR
                        (`기본시작일` <= :start_date AND `기본종료일` >= :end_date)
                    )
                """)
                params["start_date"] = req.start_date
                params["end_date"] = req.end_date
            elif has_value(req.start_date):
                # 시작일만 있으면 기본종료일이 이후인 건들 포함 (혹은 기본시작일 >= start_date 로 단순화 가능)
                where.append("`기본종료일` >= :start_date")
                params["start_date"] = req.start_date
            elif has_value(req.end_date):
                # 종료일만 있으면 기본시작일이 이전인 건들 포함
                where.append("`기본시작일` <= :end_date")
                params["end_date"] = req.end_date

            if not where:
                where.append("1=1")

            sql = f"""
                SELECT *
                FROM `AJIN_newDB`.`금형고장내역`
                WHERE {' AND '.join(where)}
            """

            print("SQL:", sql)
            print("Params:", params)

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

mold_breakDown_service = Mold_breakDown_service()
