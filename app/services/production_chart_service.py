from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.productionGrid import ProductionGridResquest

class Production_chart_service:


    def get_production_pie_chart(self, req: ProductionGridResquest):
        db: Session = next(get_db())
        try:
            # 공통 바인드 파라미터
            params = {
                "workplace": req.workplace,
                "start_work_date": req.start_work_date,  # 'YYYY-MM-DD' 문자열 또는 date 객체
                "end_work_date": req.end_work_date      # 동일
            }

            # 1) 생산수량/출고수량 및 비율
            sql_1 = text("""
                SELECT 작업장,
                       SUM(COALESCE(생산수량, 0))   AS sum_production_count,
                       SUM(COALESCE(구성품출고, 0)) AS sum_outbound_count,
                       SUM(COALESCE(생산수량, 0)) / NULLIF(SUM(COALESCE(구성품출고, 0)), 0) AS product_rate
                FROM AJIN_newDB.생산내역
                WHERE 작업장 = :workplace
                  AND 근무일자 BETWEEN :start_work_date AND :end_work_date
                GROUP BY 작업장
            """)


            pie1_data = db.execute(sql_1, params).mappings().all()
            pie1 = [dict(r) for r in pie1_data]

            # 2) 양품/생산 비율 (별칭 재사용 대신 집계식으로 직접 계산)
            sql_2 = text("""
                SELECT 작업장,
                       SUM(COALESCE(양품수량, 0))   AS sum_complete_count,
                       SUM(COALESCE(생산수량, 0))   AS sum_production_count,
                       SUM(COALESCE(양품수량, 0)) / NULLIF(SUM(COALESCE(생산수량, 0)), 0) AS 생산비율
                FROM AJIN_newDB.생산내역
                WHERE 작업장 = :workplace
                  AND 근무일자 BETWEEN :start_work_date AND :end_work_date
                GROUP BY 작업장
            """)

            pie2_data = db.execute(sql_2, params).mappings().all()
            pie2 = [dict(r) for r in pie2_data]

            # 3) 양품수량 / 가동시간 합계
            sql_3 = text("""
                SELECT 작업장,
                       SUM(COALESCE(양품수량, 0)) AS sum_complete_count,
                       SUM(COALESCE(가동시간, 0)) AS sum_runtime
                FROM AJIN_newDB.생산내역
                WHERE 작업장 = :workplace
                  AND 근무일자 BETWEEN :start_work_date AND :end_work_date
                GROUP BY 작업장
            """)

            pie3_data = db.execute(sql_3, params).mappings().all()
            pie3 = [dict(r) for r in pie3_data]

            return {
                "pie1": pie1,
                "pie2": pie2,
                "pie3": pie3,
            }
        finally:
            db.close()

    def get_production_bar_chart(self, req: ProductionGridResquest):
        db: Session = next(get_db())
        try:
            params = {
                "itemName": req.itemName,
                "start_work_date": req.start_work_date,  # 'YYYY-MM-DD' 문자열 또는 date 객체
                "end_work_date": req.end_work_date,      # 동일
            }
            
            print("리퀘스트확인:", req.end_work_date)
            sql = text("""
                    SELECT 
                        m.년도,
                        m.월,
                        m.월별_양품수량,
                        t.총_가동시간,
                        t.총_생산수량,
                        t.총_공정불량
                    FROM (
                        SELECT 
                            YEAR(근무일자) AS 년도,
                            MONTH(근무일자) AS 월,
                            SUM(COALESCE(양품수량, 0)) AS 월별_양품수량
                        FROM AJIN_newDB.생산내역
                        WHERE 자재명 = :itemName
                        AND 근무일자 BETWEEN :start_work_date AND :end_work_date
                        GROUP BY YEAR(근무일자), MONTH(근무일자)
                    ) m
                    CROSS JOIN (
                        SELECT 
                            SUM(COALESCE(가동시간, 0)) AS 총_가동시간,
                            SUM(COALESCE(생산수량, 0)) AS 총_생산수량,
                            SUM(COALESCE(공정불량, 0)) AS 총_공정불량
                        FROM AJIN_newDB.생산내역
                        WHERE 자재명 = :itemName
                        AND 근무일자 BETWEEN :start_work_date AND :end_work_date
                    ) t
                    ORDER BY m.년도, m.월;
            """)

            print(params)
            print(sql)
            data = db.execute(sql, params).mappings().all()
            return [dict(r) for r in data]

        finally:
            db.close()
            
    
    def get_itemList(self):
        db: Session = next(get_db())
        try:
            sql = text("""
                SELECT DISTINCT 자재명
                FROM AJIN_newDB.생산내역
                ORDER BY 자재명;
            """)
            data = db.execute(sql).mappings().all()  
            return data  
        finally:
            db.close()

    def get_live_chart(self, req: ProductionGridResquest):
        db: Session = next(get_db())
        try:
           sql = text("""
                SELECT 근무일자, sum(생산수량) FROM 생산내역 GROUP BY 근무일자 
            """)
           data = db.execute(sql).mappings().all()
           return data  
        finally:
           db.close() 

production_chart_service = Production_chart_service()
