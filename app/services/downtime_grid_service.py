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

            # 각 필드별로 값이 있으면 WHERE 조건에 추가
            if has_value(req.start_work_date):
                where_conditions.append("`근무일자` >= :start_work_date")
                params["start_work_date"] = req.start_work_date
            
            if has_value(req.end_work_date):
                where_conditions.append("`근무일자` <= :end_work_date")
                params["end_work_date"] = req.end_work_date

            if has_value(req.plant):
                where_conditions.append("`플랜트` <= :plant")
                params["plant"] = req.plant

            if has_value(req.worker):
                where_conditions.append("`책임자` <= :worker")
                params["worker"] = req.worker

            if has_value(req.workplace):
                where_conditions.append("`작업장` <= :workplace")
                params["workplace"] = req.workplace

            if has_value(req.itemCode):
                where_conditions.append("`자재번호` <= :itemCode")
                params["itemCode"] = req.itemCode
#
            if has_value(req.carModel):
                where_conditions.append("`차종` <= :carModel")
                params["carModel"] = req.carModel

            if has_value(req.downtimeCode):
                where_conditions.append("`비가동코드` <= :downtimeCode")
                params["downtimeCode"] = req.downtimeCode

            if has_value(req.downtimeName):
                where_conditions.append("`비가동명` <= :downtimeName")
                params["downtimeName"] = req.downtimeName
#
            if has_value(req.downtimeMinutes):
                where_conditions.append("`비가동(분)` <= :downtimeMinutes")
                params["downtimeMinutes"] = req.downtimeMinutes
            
            if has_value(req.note):
                where_conditions.append("`비고` <= :note")
                params["note"] = req.note


            # WHERE 조건이 없으면 기본값 설정
            if not where_conditions:
                where_conditions.append("1=1")

            # SQL 쿼리 생성
            sql = f"SELECT * FROM `AJIN_newDB`.`비가동시간 및 현황` WHERE {' AND '.join(where_conditions)}"
            
            print(f"SQL: {sql}")
            print(f"파라미터: {params}")
            
            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()

downtime_grid_service = Downtime_grid_service()
