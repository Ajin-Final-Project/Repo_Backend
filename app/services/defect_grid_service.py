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

            # 기존: `근무일자` → b.`근무일자`(모두 b. 접두사 추가)
            # 날짜
            if has_value(req.start_work_date):
                where_conditions.append("b.`근무일자` >= :start_work_date")
                params["start_work_date"] = req.start_work_date

            if has_value(req.end_work_date):
                where_conditions.append("b.`근무일자` <= :end_work_date")
                params["end_work_date"] = req.end_work_date

            # 텍스트/식별자
            if has_value(req.workplace):
                where_conditions.append("b.`작업장` = :workplace")
                params["workplace"] = req.workplace

            if has_value(req.itemInfo):
                # 부분 검색 가능하도록 LIKE
                where_conditions.append("b.`자재정보` LIKE :itemInfo")
                params["itemInfo"] = f"%{req.itemInfo.strip()}%"

            if has_value(req.carModel):
                where_conditions.append("b.`차종` = :carModel")
                params["carModel"] = req.carModel

            if has_value(req.orderType):
                where_conditions.append("b.`수주유형` = :orderType")
                params["orderType"] = req.orderType

            if has_value(req.defectCode):
                where_conditions.append("b.`불량코드` = :defectCode")
                params["defectCode"] = req.defectCode

            if has_value(req.defectType):
                where_conditions.append("b.`불량유형` LIKE :defectType")
                params["defectType"] = f"%{req.defectType.strip()}%"

            if has_value(req.remark):
                where_conditions.append("b.`비고` LIKE :remark")
                params["remark"] = f"%{req.remark.strip()}%"

            if has_value(req.worker):
                where_conditions.append("b.`작업자` = :worker")
                params["worker"] = req.worker

            # 수량
            if has_value(req.goodItemCount):
                where_conditions.append("b.`양품수량` = :goodItemCount")
                params["goodItemCount"] = req.goodItemCount

            if has_value(req.waitItemCount):
                where_conditions.append("b.`판정대기` = :waitItemCount")
                params["waitItemCount"] = req.waitItemCount

            if has_value(req.rwkCount):
                where_conditions.append("b.`RWK 수량` = :rwkCount")
                params["rwkCount"] = req.rwkCount

            if has_value(req.scrapCount):
                where_conditions.append("b.`폐기 수량` = :scrapCount")
                params["scrapCount"] = req.scrapCount

            # WHERE 기본
            if not where_conditions:
                where_conditions.append("1=1")

            # 최종 SQL
            # sql = f"""
            #     SELECT *
            #     FROM `AJIN_newDB`.`불량수량 및 유형`
            #     WHERE {' AND '.join(where_conditions)}
            # """

            # 최종 SQL
            # 1) 불량수량 및 유형(b) ↔ 생산내역(p) INNER JOIN
            # 2) 조인 키 = 근무일자, 작업장, 자재번호, 차종
            # 3) "생산내역에 존재하는 불량 데이터만" 결과에 포함
            # sql = f"""
            #     SELECT DISTINCT b.*
            #     FROM `AJIN_newDB`.`불량수량 및 유형` b
            #     INNER JOIN `AJIN_newDB`.`생산내역` p
            #     ON b.`근무일자`  = p.`근무일자`
            #     AND b.`작업장`   = p.`작업장`
            #     AND b.`자재번호` = p.`자재번호`
            #     AND b.`차종`     = p.`차종`
            #     WHERE {' AND '.join(where_conditions)}
            # """

            # INNER JOIN → EXISTS 로 변경한 부분
            exists_clause = """
                EXISTS (
                    SELECT 1
                    FROM `AJIN_newDB`.`생산내역` p
                    WHERE p.`근무일자`  = b.`근무일자`
                      AND p.`작업장`   = b.`작업장`
                      AND p.`자재번호` = b.`자재번호`
                      AND p.`차종`     = b.`차종`
                )
            """

            # 최종 SQL: JOIN이 사라지고, WHERE 절에 EXISTS 조건 추가
            sql = f"""
                SELECT b.*
                FROM `AJIN_newDB`.`불량수량 및 유형` b
                WHERE {' AND '.join(where_conditions)}
                  AND {exists_clause}
                ORDER BY b.`근무일자` DESC, b.`자재번호`
            """

            print(f"[DefectGrid] SQL: {sql}")
            print(f"[DefectGrid] PARAMS: {params}")

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()

defect_grid_service = Defect_grid_service()


