# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from app.config.database import get_db
# from app.models.defectGrid import DefectGridRequest


# class Defect_grid_service:
#     def get_defect_list(self, req: DefectGridRequest):
#         db: Session = next(get_db())
#         try:
#             where_conditions = []
#             params = {}

#             def has_value(value):
#                 if value is None:
#                     return False
#                 if isinstance(value, str):
#                     return value.strip() != "" and value.strip().lower() != "string"
#                 if isinstance(value, int):
#                     return value != 0
#                 return True

#             # 날짜
#             if has_value(req.start_work_date):
#                 where_conditions.append("b.`근무일자` >= :start_work_date")
#                 params["start_work_date"] = req.start_work_date
#             if has_value(req.end_work_date):
#                 where_conditions.append("b.`근무일자` <= :end_work_date")
#                 params["end_work_date"] = req.end_work_date

#             # 텍스트/식별자
#             if has_value(req.workplace):
#                 where_conditions.append("b.`작업장` = :workplace")
#                 params["workplace"] = req.workplace

#             if has_value(req.itemInfo):
#                 # 자재번호 / 자재정보 부분검색 허용
#                 where_conditions.append("(b.`자재번호` LIKE :itemInfo OR b.`자재정보` LIKE :itemInfo)")
#                 params["itemInfo"] = f"%{req.itemInfo.strip()}%"

#             if has_value(req.carModel):
#                 where_conditions.append("b.`차종` = :carModel")
#                 params["carModel"] = req.carModel

#             if has_value(req.orderType):
#                 where_conditions.append("b.`수주유형` = :orderType")
#                 params["orderType"] = req.orderType

#             if has_value(req.defectCode):
#                 where_conditions.append("b.`불량코드` = :defectCode")
#                 params["defectCode"] = req.defectCode

#             if has_value(req.defectType):
#                 where_conditions.append("b.`불량유형` LIKE :defectType")
#                 params["defectType"] = f"%{req.defectType.strip()}%"

#             if has_value(req.remark):
#                 where_conditions.append("b.`비고` LIKE :remark")
#                 params["remark"] = f"%{req.remark.strip()}%"

#             if has_value(req.worker):
#                 where_conditions.append("b.`작업자` = :worker")
#                 params["worker"] = req.worker

#             # 수량
#             if has_value(req.goodItemCount):
#                 where_conditions.append("b.`양품수량` = :goodItemCount")
#                 params["goodItemCount"] = req.goodItemCount
#             if has_value(req.waitItemCount):
#                 where_conditions.append("b.`판정대기` = :waitItemCount")
#                 params["waitItemCount"] = req.waitItemCount
#             if has_value(req.rwkCount):
#                 where_conditions.append("b.`RWK 수량` = :rwkCount")
#                 params["rwkCount"] = req.rwkCount
#             if has_value(req.scrapCount):
#                 where_conditions.append("b.`폐기 수량` = :scrapCount")
#                 params["scrapCount"] = req.scrapCount

#             # WHERE 기본
#             if not where_conditions:
#                 where_conditions.append("1=1")

#             # 생산내역 존재하는 행만 (키: 근무일자, 작업장, 자재번호, 차종)
#             exists_clause = """
#                 EXISTS (
#                     SELECT 1
#                     FROM `AJIN_newDB`.`생산내역` p
#                     WHERE p.`근무일자`  = b.`근무일자`
#                       AND p.`작업장`   = b.`작업장`
#                       AND p.`자재번호` = b.`자재번호`
#                       AND p.`차종`     = b.`차종`
#                 )
#             """

#             # ❗ 품목명 보정: b.품목명이 비면 생산내역의 `자재명`(가장 최근일자) 사용
#             sql = f"""
#                 SELECT
#                   b.*,
#                   COALESCE(
#                     NULLIF(TRIM(b.`품목명`), ''),
#                     (
#                       SELECT NULLIF(TRIM(p.`자재명`), '')
#                       FROM `AJIN_newDB`.`생산내역` p
#                       WHERE p.`자재번호` = b.`자재번호`
#                       ORDER BY p.`근무일자` DESC
#                       LIMIT 1
#                     )
#                   ) AS `품목명_보정`
#                 FROM `AJIN_newDB`.`불량수량 및 유형` b
#                 WHERE {' AND '.join(where_conditions)}
#                   AND {exists_clause}
#                 ORDER BY b.`근무일자` DESC, b.`자재번호`
#             """

#             print(f"[DefectGrid] SQL: {sql}")
#             print(f"[DefectGrid] PARAMS: {params}")

#             rows = db.execute(text(sql), params).mappings().all()
#             return [dict(r) for r in rows]

#         finally:
#             db.close()


# defect_grid_service = Defect_grid_service()





# app/services/defect_grid_service.py
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
                where_conditions.append("b.`근무일자` >= :start_work_date")
                params["start_work_date"] = req.start_work_date
            if has_value(req.end_work_date):
                where_conditions.append("b.`근무일자` <= :end_work_date")
                params["end_work_date"] = req.end_work_date

            # 텍스트/식별자
            if has_value(req.workplace):
                # 생산_불량에는 생산/불량 양쪽 작업장이 있으므로 COALESCE로 필터
                where_conditions.append(
                    "(COALESCE(NULLIF(TRIM(b.`불량_작업장`),''), NULLIF(TRIM(b.`생산_작업장`),'')) = :workplace)"
                )
                params["workplace"] = req.workplace

            if has_value(req.itemInfo):
                # 자재번호/자재명(=생산_자재명)/불량측 품목명 부분검색
                where_conditions.append(
                    "("
                    "b.`자재번호` LIKE :itemInfo OR "
                    "b.`생산_자재명` LIKE :itemInfo OR "
                    "b.`불량_품목명` LIKE :itemInfo"
                    ")"
                )
                params["itemInfo"] = f"%{req.itemInfo.strip()}%"

            if has_value(req.carModel):
                where_conditions.append("b.`생산_차종` = :carModel")
                params["carModel"] = req.carModel

            # 수주유형은 생산_불량에 없을 수 있어 기본적으로 제외(테이블에 있으면 주석 해제)
            # if has_value(req.orderType):
            #     where_conditions.append("b.`수주유형` = :orderType")
            #     params["orderType"] = req.orderType

            if has_value(req.defectCode):
                where_conditions.append("b.`불량_코드` = :defectCode")
                params["defectCode"] = req.defectCode

            if has_value(req.defectType):
                where_conditions.append("b.`불량_유형` LIKE :defectType")
                params["defectType"] = f"%{req.defectType.strip()}%"

            if has_value(req.remark):
                where_conditions.append("b.`불량_비고` LIKE :remark")
                params["remark"] = f"%{req.remark.strip()}%"

            if has_value(req.worker):
                where_conditions.append("b.`불량_작업자` = :worker")
                params["worker"] = req.worker

            # 수량 필터 (불량측 수량 기준)
            if has_value(req.goodItemCount):
                where_conditions.append("b.`불량_양품수량` = :goodItemCount")
                params["goodItemCount"] = req.goodItemCount
            if has_value(req.waitItemCount):
                where_conditions.append("b.`불량_판정대기` = :waitItemCount")
                params["waitItemCount"] = req.waitItemCount
            if has_value(req.rwkCount):
                where_conditions.append("b.`불량_RWK수량` = :rwkCount")
                params["rwkCount"] = req.rwkCount
            if has_value(req.scrapCount):
                where_conditions.append("b.`불량_폐기수량` = :scrapCount")
                params["scrapCount"] = req.scrapCount

            if not where_conditions:
                where_conditions.append("1=1")

            # ✅ DB 컬럼을 있는 그대로 반환
            sql = f"""
                SELECT
                  b.*
                FROM `AJIN_newDB`.`생산_불량` b
                WHERE {' AND '.join(where_conditions)}
                ORDER BY b.`근무일자` DESC, b.`자재번호`;
            """

            print(f"[DefectGrid] SQL: {sql}")
            print(f"[DefectGrid] PARAMS: {params}")

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()


defect_grid_service = Defect_grid_service()
