from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.inspectionGrid import inspectionGridRequest
from decimal import Decimal

class Inspection_grid_service:

    def get_inspection_list(self, req: inspectionGridRequest):
        db: Session = next(get_db())
        try:
            where_conditions = []
            params = {}

            def has_value(value):
                if value is None:
                    return False
                if isinstance(value, str):
                    # 'string'은 Swagger UI에서 자동으로 입력되는 더미값으로, 실제 값이 아님
                    return value.strip() not in ("", "string")
                if isinstance(value, (int, Decimal)):
                    # 숫자 0도 유효한 값일 수 있으므로 None만 체크
                    return value is not None 
                return True
            
            if has_value(req.start_work_date):
                where_conditions.append("DATE(`보고일`) >= :start_work_date")
                params["start_work_date"] = req.start_work_date
                
            if has_value(req.end_work_date):
                where_conditions.append("DATE(`보고일`) <= :end_work_date")
                params["end_work_date"] = req.end_work_date
                
            if has_value(req.businessPlace):
                where_conditions.append("`사업장` = :businessPlace")
                params["businessPlace"] = req.businessPlace

            if has_value(req.plant):
                where_conditions.append("`공장` = :plant")
                params["plant"] = req.plant

            if has_value(req.process):
                where_conditions.append("`공정` = :process")
                params["process"] = req.process

            if has_value(req.equipment):
                where_conditions.append("`설비` = :equipment")
                params["equipment"] = req.equipment

            if has_value(req.inspectionType):
                where_conditions.append("`검사구분` = :inspectionType")
                params["inspectionType"] = req.inspectionType

            if has_value(req.itemNumber):
                where_conditions.append("`품번` = :itemNumber")
                params["itemNumber"] = req.itemNumber

            # 이 '보고일' 필터는 날짜 범위 필터(start_work_date, end_work_date)가 
            # 있으므로 주석 처리된 상태를 유지하는 것이 좋습니다.
            # if has_value(req.reportDate):
            #     where_conditions.append("DATE(`보고일`) = :reportDate")
            #     params["reportDate"] = req.reportDate

            if has_value(req.shiftType):
                where_conditions.append("`주야구분` = :shiftType")
                params["shiftType"] = req.shiftType

            if has_value(req.workSequence):
                where_conditions.append("`작업순번` = :workSequence")
                params["workSequence"] = req.workSequence

            if has_value(req.workType):
                where_conditions.append("`작업구분` = :workType")
                params["workType"] = req.workType

            if has_value(req.inspectionSequence):
                where_conditions.append("`검사순번` = :inspectionSequence")
                params["inspectionSequence"] = req.inspectionSequence

            if has_value(req.inspectionItemName):
                where_conditions.append("`검사항목명` LIKE :inspectionItemName")
                params["inspectionItemName"] = f"%{req.inspectionItemName.strip()}%"

            if has_value(req.inspectionDetails):
                where_conditions.append("`검사내용` LIKE :inspectionDetails")
                params["inspectionDetails"] = f"%{req.inspectionDetails.strip()}%"

            if has_value(req.productionValue):
                where_conditions.append("`생산` = :productionValue")
                params["productionValue"] = req.productionValue

            # WHERE 조건이 없으면 기본값 설정
            if not where_conditions:
                where_conditions.append("1=1")

            sql = f"SELECT * FROM `AJIN_newDB`.`검사내역` WHERE {' AND '.join(where_conditions)}"

            print(f"Executing SQL: {sql}")
            print(f"With Parameters: {params}")

            result = db.execute(text(sql), params)
            rows = result.mappings().all()

            # --- 이 부분이 새로 추가되거나 수정되어야 합니다. ---
            # 데이터베이스 컬럼명(한글)과 프론트엔드 필드명(영문) 매핑
            mapped_data = []
            for row in rows:
                mapped_row = {
                    "id": row.get("id", None), # 'id' 컬럼이 있다면 사용, 없으면 None
                    "businessPlace": row.get("사업장", ''),
                    "plant": row.get("공장", ''),
                    "process": row.get("공정", ''),
                    "equipment": row.get("설비", ''),
                    "inspectionType": row.get("검사구분", ''),
                    "itemNumber": row.get("품번", ''),
                    "reportDate": row.get("보고일", ''), # '보고일' 컬럼이 데이터베이스에 있다고 가정
                    "shiftType": row.get("주야구분", ''),
                    "workSequence": row.get("작업순번", None),
                    "workType": row.get("작업구분", ''),
                    "inspectionSequence": row.get("검사순번", None),
                    "inspectionItemName": row.get("검사항목명", ''),
                    "inspectionDetails": row.get("검사내용", ''),
                    "productionValue": row.get("생산", None)
                    # 필요한 모든 컬럼을 여기에 매핑
                }
                mapped_data.append(mapped_row)
            
            return mapped_data # 매핑된 데이터 반환

        finally:
            db.close()


inspection_grid_service = Inspection_grid_service()
