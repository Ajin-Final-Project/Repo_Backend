from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.mold_BreakDown import MoldBreakdownRequest
import re
from datetime import date

class Mold_chart_service:


    def get_mold_workCount_chart(self, req: MoldBreakdownRequest):
        db: Session = next(get_db())
        try:
            params = {
                "start_date": req.start_date,
                "end_date": req.end_date
            }
            
            sql = text("""
              SELECT
                  t.mm AS `월`,
                  SUM(`1200T 작업횟수`)     AS sum_1200T,
                  SUM(`1500T 작업횟수`)     AS sum_1500T,
                  SUM(`1000T 작업횟수`)     AS sum_1000T,
                  SUM(`1000T PRO 작업횟수`) AS sum_1000T_PRO
              FROM (
                  SELECT
                      CAST(RIGHT(`월`, 2) AS UNSIGNED) AS mm,
                      `1200T 작업횟수`,
                      `1500T 작업횟수`,
                      `1000T 작업횟수`,
                      `1000T PRO 작업횟수`
                  FROM `금형 설비별 타수 및 가동시간`
              ) AS t
              WHERE
                  (
                      MONTH(:start_date) <= MONTH(:end_date)
                      AND t.mm BETWEEN MONTH(:start_date) AND MONTH(:end_date)
                  )
                  OR
                  (
                      MONTH(:start_date) > MONTH(:end_date)     -- 예: 11 ~ 02
                      AND (t.mm >= MONTH(:start_date) OR t.mm <= MONTH(:end_date))
                  )
              GROUP BY t.mm
              ORDER BY t.mm;
            """)

            print(f"SQL: {sql}")
            print(f"파라미터: {params}")
            
            data = db.execute(sql, params).mappings().all()
            return [dict(r) for r in data]

        finally:
            db.close()

    def get_runtime_chart(self, req: MoldBreakdownRequest):
      db: Session = next(get_db())
      try:


          params = {
            "start_m" : int(req.start_date[5:7]),
            "end_m"   : int(req.end_date[5:7])

          }
          
          sql = text("""
            SELECT
                c.`월`,
                c.`설비`,
                c.`작업횟수`,
                h.`가동시간`
              FROM (
                SELECT `월`, '1200T' AS `설비`, `1200T 작업횟수` AS `작업횟수`
                FROM `금형 설비별 타수 및 가동시간`
                WHERE (
                  (CAST(:start_m AS UNSIGNED) <= CAST(:end_m AS UNSIGNED) AND `월` BETWEEN CAST(:start_m AS UNSIGNED) AND CAST(:end_m AS UNSIGNED))
                  OR
                  (CAST(:start_m AS UNSIGNED) >  CAST(:end_m AS UNSIGNED) AND (`월` >= CAST(:start_m AS UNSIGNED) OR `월` <= CAST(:end_m AS UNSIGNED)))
                )
                UNION ALL
                SELECT `월`, '1500T', `1500T 작업횟수`
                FROM `금형 설비별 타수 및 가동시간`
                WHERE (
                  (CAST(:start_m AS UNSIGNED) <= CAST(:end_m AS UNSIGNED) AND `월` BETWEEN CAST(:start_m AS UNSIGNED) AND CAST(:end_m AS UNSIGNED))
                  OR
                  (CAST(:start_m AS UNSIGNED) >  CAST(:end_m AS UNSIGNED) AND (`월` >= CAST(:start_m AS UNSIGNED) OR `월` <= CAST(:end_m AS UNSIGNED)))
                )
                UNION ALL
                SELECT `월`, '1000T', `1000T 작업횟수`
                FROM `금형 설비별 타수 및 가동시간`
                WHERE (
                  (CAST(:start_m AS UNSIGNED) <= CAST(:end_m AS UNSIGNED) AND `월` BETWEEN CAST(:start_m AS UNSIGNED) AND CAST(:end_m AS UNSIGNED))
                  OR
                  (CAST(:start_m AS UNSIGNED) >  CAST(:end_m AS UNSIGNED) AND (`월` >= CAST(:start_m AS UNSIGNED) OR `월` <= CAST(:end_m AS UNSIGNED)))
                )
                UNION ALL
                SELECT `월`, '1000T PRO', `1000T PRO 작업횟수`
                FROM `금형 설비별 타수 및 가동시간`
                WHERE (
                  (CAST(:start_m AS UNSIGNED) <= CAST(:end_m AS UNSIGNED) AND `월` BETWEEN CAST(:start_m AS UNSIGNED) AND CAST(:end_m AS UNSIGNED))
                  OR
                  (CAST(:start_m AS UNSIGNED) >  CAST(:end_m AS UNSIGNED) AND (`월` >= CAST(:start_m AS UNSIGNED) OR `월` <= CAST(:end_m AS UNSIGNED)))
                )
              ) AS c
              JOIN (
                SELECT `월`, '1200T' AS `설비`, `1200T 총가동시간` AS `가동시간`
                FROM `금형 설비별 타수 및 가동시간`
                WHERE (
                  (CAST(:start_m AS UNSIGNED) <= CAST(:end_m AS UNSIGNED) AND `월` BETWEEN CAST(:start_m AS UNSIGNED) AND CAST(:end_m AS UNSIGNED))
                  OR
                  (CAST(:start_m AS UNSIGNED) >  CAST(:end_m AS UNSIGNED) AND (`월` >= CAST(:start_m AS UNSIGNED) OR `월` <= CAST(:end_m AS UNSIGNED)))
                )
                UNION ALL
                SELECT `월`, '1500T', `1500T 총가동시간`
                FROM `금형 설비별 타수 및 가동시간`
                WHERE (
                  (CAST(:start_m AS UNSIGNED) <= CAST(:end_m AS UNSIGNED) AND `월` BETWEEN CAST(:start_m AS UNSIGNED) AND CAST(:end_m AS UNSIGNED))
                  OR
                  (CAST(:start_m AS UNSIGNED) >  CAST(:end_m AS UNSIGNED) AND (`월` >= CAST(:start_m AS UNSIGNED) OR `월` <= CAST(:end_m AS UNSIGNED)))
                )
                UNION ALL
                SELECT `월`, '1000T', `1000T 총가동시간`
                FROM `금형 설비별 타수 및 가동시간`
                WHERE (
                  (CAST(:start_m AS UNSIGNED) <= CAST(:end_m AS UNSIGNED) AND `월` BETWEEN CAST(:start_m AS UNSIGNED) AND CAST(:end_m AS UNSIGNED))
                  OR
                  (CAST(:start_m AS UNSIGNED) >  CAST(:end_m AS UNSIGNED) AND (`월` >= CAST(:start_m AS UNSIGNED) OR `월` <= CAST(:end_m AS UNSIGNED)))
                )
                UNION ALL
                SELECT `월`, '1000T PRO', `1000T PRO 총가동시간`
                FROM `금형 설비별 타수 및 가동시간`
                WHERE (
                  (CAST(:start_m AS UNSIGNED) <= CAST(:end_m AS UNSIGNED) AND `월` BETWEEN CAST(:start_m AS UNSIGNED) AND CAST(:end_m AS UNSIGNED))
                  OR
                  (CAST(:start_m AS UNSIGNED) >  CAST(:end_m AS UNSIGNED) AND (`월` >= CAST(:start_m AS UNSIGNED) OR `월` <= CAST(:end_m AS UNSIGNED)))
                )
              ) AS h
                ON c.`월` = h.`월` AND c.`설비` = h.`설비`
              ORDER BY c.`월`, c.`설비`;
          """)
          print(sql)
          print(f"SQL 파라미터: {params}")
          rows = db.execute(sql, params).mappings().all()
          return [dict(r) for r in rows]

      except Exception as e:
          # 500 숨기지 말고 원인 노출
          raise HTTPException(status_code=400, detail=f"쿼리 실패: {e}")
      finally:
          db.close()

    def get_summerize_data(self, req: MoldBreakdownRequest):
        db: Session = next(get_db())
        try:
            params = {
                "equipment": req.equipment_detail,
                "start_m":  int(req.start_date[5:7]),
                "end_m":  int(req.end_date[5:7])
            }

            
            sql = text("""
                WITH cnt AS (
                  SELECT `월`, '1200T' AS 설비, `1200T 작업횟수` AS 작업횟수 FROM `금형 설비별 타수 및 가동시간`
                  UNION ALL SELECT `월`, '1500T', `1500T 작업횟수` FROM `금형 설비별 타수 및 가동시간`
                  UNION ALL SELECT `월`, '1000T', `1000T 작업횟수` FROM `금형 설비별 타수 및 가동시간`
                  UNION ALL SELECT `월`, '1000T PRO', `1000T PRO 작업횟수` FROM `금형 설비별 타수 및 가동시간`
                ),
                hrs AS (
                  SELECT `월`, '1200T' AS 설비, `1200T 총가동시간` AS 가동시간 FROM `금형 설비별 타수 및 가동시간`
                  UNION ALL SELECT `월`, '1500T', `1500T 총가동시간` FROM `금형 설비별 타수 및 가동시간`
                  UNION ALL SELECT `월`, '1000T', `1000T 총가동시간` FROM `금형 설비별 타수 및 가동시간`
                  UNION ALL SELECT `월`, '1000T PRO', `1000T PRO 총가동시간` FROM `금형 설비별 타수 및 가동시간`
                ),
                filtered AS (
                  SELECT c.`월`, c.`설비`, c.`작업횟수`, h.`가동시간`
                  FROM cnt c
                  JOIN hrs h ON c.`월` = h.`월` AND c.`설비` = h.`설비`
                  WHERE c.`설비` = :equipment
                    AND (
                      (:start_m <= :end_m AND c.`월` BETWEEN :start_m AND :end_m)
                      OR (:start_m > :end_m AND (c.`월` >= :start_m OR c.`월` <= :end_m))
                    )
                )
                SELECT
                  AVG(`작업횟수`)  AS avg_작업횟수,
                  AVG(`가동시간`)  AS avg_가동시간,
                  SUM(`작업횟수`)  AS sum_작업횟수,
                  SUM(`가동시간`)  AS sum_가동시간
                FROM filtered;

            """)

            print(f"SQL: {sql}")
            print(f"파라미터: {params}")
            
            data = db.execute(sql, params).mappings().all()
            return [dict(r) for r in data]
        
        finally:
            db.close()
   
    def get_mold_breakDown_chart(self, req: MoldBreakdownRequest):
        db: Session = next(get_db())
        try:
            params = {
                "equipment": req.equipment_detail,
                "start_date": req.start_date,
                "end_date": req.end_date
            }

            sql = text("""
                  WITH RECURSIVE months AS (
                    SELECT DATE_FORMAT(:start_date, '%Y-%m-01') AS ymd
                    UNION ALL
                    SELECT DATE_FORMAT(DATE_ADD(ymd, INTERVAL 1 MONTH), '%Y-%m-01')
                    FROM months
                    WHERE ymd < DATE_FORMAT(:end_date, '%Y-%m-01')
                  )
                  SELECT
                    DATE_FORMAT(m.ymd, '%Y-%m') AS ym,
                    COALESCE(COUNT(g.오더번호), 0) AS 고장건수
                  FROM months m
                  LEFT JOIN 금형고장내역 g
                    ON DATE_FORMAT(g.기본시작일, '%Y-%m') = DATE_FORMAT(m.ymd, '%Y-%m')
                  AND g.오더유형내역 = '고장점검(BM)'
                  AND g.기본시작일 >= :start_date
                  AND g.기본시작일 <= :end_date
                  AND (:equipment IS NULL OR g.설비내역 = :equipment)
                  GROUP BY ym
                  ORDER BY ym;
            """)

            print(f"SQL: {sql}")
            print(f"파라미터: {params}")
            
            data = db.execute(sql, params).mappings().all()
            return [dict(r) for r in data]
        
        finally:
            db.close()

    def get_mold_breakDown_pie_top10(self, req: MoldBreakdownRequest):
        db: Session = next(get_db())
        try:
          params = {
                "start_date": req.start_date,  # '2024-01-01'
                "end_date":   req.end_date,    # '2024-01-31'  (해당 날짜 포함)
            }

          sql = text("""
              WITH top10 AS (
                  SELECT 
                      설비내역,
                      COUNT(*) AS 설비횟수
                  FROM 금형고장내역
                  WHERE 오더유형내역 = '고장점검(BM)'
                    AND 기본시작일 >= :start_date
                    AND 기본시작일 <  DATE_ADD(:end_date, INTERVAL 1 DAY)  -- end_date 포함
                  GROUP BY 설비내역
                  ORDER BY 설비횟수 DESC
                  LIMIT 10
                ),
                total AS (
                  SELECT SUM(설비횟수) AS top10_sum FROM top10
                )
                SELECT 
                    t.설비내역,
                    t.설비횟수,
                    ROUND(100.0 * t.설비횟수 / total.top10_sum, 2) AS 비율퍼센트
                FROM top10 t
                CROSS JOIN total
                ORDER BY t.설비횟수 DESC;
            """)

          print(f"SQL: {sql}")
          print(f"파라미터: {params}")
            
          data = db.execute(sql, params).mappings().all()
          return [dict(r) for r in data]
        
        finally:
            db.close()

mold_chart_service = Mold_chart_service()
