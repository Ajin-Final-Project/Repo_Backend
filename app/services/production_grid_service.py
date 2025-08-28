from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.productionGrid import ProductionGridResquest

class Production_grid_service:

    def get_production_list(self, req: ProductionGridResquest):
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

            if has_value(req.productionNumber):
                where_conditions.append("`실적번호` = :productionNumber")
                params["productionNumber"] = req.productionNumber

            if has_value(req.plant):
                where_conditions.append("`플랜트` = :plant")
                params["plant"] = req.plant

            if has_value(req.worker):
                where_conditions.append("`책임자` = :worker")
                params["worker"] = req.worker

            if has_value(req.line):
                where_conditions.append("`작업장` = :line")
                params["line"] = req.line

            if has_value(req.itemCode):
                where_conditions.append("`자재번호` = :itemCode")
                params["itemCode"] = req.itemCode

            if has_value(req.itemName):
                where_conditions.append("`자재명` LIKE :itemName")
                params["itemName"] = f"%{req.itemName.strip()}%"

            if has_value(req.carModel):
                where_conditions.append("`차종` = :carModel")
                params["carModel"] = req.carModel

            if has_value(req.lot):
                where_conditions.append("`투입LOT` = :lot")
                params["lot"] = req.lot

            if has_value(req.sheetInputCoil):
                where_conditions.append("`시트투입코일` = :sheetInputCoil")
                params["sheetInputCoil"] = req.sheetInputCoil

            if has_value(req.runtime):
                where_conditions.append("`가동시간` = :runtime")
                params["runtime"] = req.runtime

            if has_value(req.goodItemCount):
                where_conditions.append("`양품수량` = :goodItemCount")
                params["goodItemCount"] = req.goodItemCount

            if has_value(req.waitItemCount):
                where_conditions.append("`판정대기` = :waitItemCount")
                params["waitItemCount"] = req.waitItemCount

            if has_value(req.badItemCount):
                where_conditions.append("`완성품불량` = :badItemCount")
                params["badItemCount"] = req.badItemCount

            if has_value(req.productionItemNumber):
                where_conditions.append("`생산수량` = :productionItemNumber")
                params["productionItemNumber"] = req.productionItemNumber

            if has_value(req.processBadItemNumber):
                where_conditions.append("`공정불량` = :processBadItemNumber")
                params["processBadItemNumber"] = req.processBadItemNumber

            if has_value(req.componentDeliveryCount):
                where_conditions.append("`구성품출고` = :componentDeliveryCount")
                params["componentDeliveryCount"] = req.componentDeliveryCount

            if has_value(req.constructor):
                where_conditions.append("`생성자` = :constructor")
                params["constructor"] = req.constructor

            if has_value(req.createDate):
                where_conditions.append("DATE(`생성일`) = :createDate")
                params["createDate"] = req.createDate

            # WHERE 조건이 없으면 기본값 설정
            if not where_conditions:
                where_conditions.append("1=1")

            # SQL 쿼리 생성
            sql = f"SELECT * FROM `AJIN_newDB`.`생산내역` WHERE {' AND '.join(where_conditions)}"
            
            print(f"SQL: {sql}")
            print(f"파라미터: {params}")
            
            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()

production_grid_service = Production_grid_service()
