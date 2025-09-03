from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.mold_BreakDown import MoldBreakdownRequest
from fastapi import HTTPException
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
                "plant": req.plant,
                "worker": req.worker,
                "line": req.line,
                "itemCd": req.itemCd,
                "start_date": req.start_date,
                "end_date": req.end_date
            }
            print(params)
            sql = text("""
                  WITH prod_filt AS (
                    SELECT DISTINCT 플랜트, 책임자, 작업장, 자재번호, 자재명
                    FROM AJIN_newDB.생산내역
                    WHERE 플랜트 = :plant
                      AND 책임자 = :worker
                      AND 작업장 = :line
                      AND 자재번호 = :itemCd
                  )
                  SELECT
                    DATE_FORMAT(b.기본종료일, '%Y-%m') AS ym,   -- 월 단위
                    COUNT(*) AS order_cnt                        -- 오더내역 건수
                    -- 필요 시: COUNT(DISTINCT b.오더번호) AS order_cnt_distinct
                  FROM AJIN_newDB.금형고장내역 AS b
                  JOIN prod_filt AS p
                    ON b.설비내역 LIKE CONCAT('%', p.자재번호, '%')
                  WHERE b.오더유형내역 = '고장점검(BM)'
                    AND b.기본종료일 IS NOT NULL
                    AND b.기본종료일 between :start_date and :end_date
                  GROUP BY ym
                  ORDER BY ym;
            """)

            print(f"SQL: {sql}")
            print(f"파라미터: {params}")
            
            data = db.execute(sql, params).mappings().all()
            print("_"*100)
            print(data)
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

    def get_distinct_equipment_list(self):
        """
        금형고장내역 테이블에서 distinct 설비내역 목록 조회
        """
        db: Session = next(get_db())
        try:
            sql = text("""
                SELECT DISTINCT(설비내역) 
                FROM 금형고장내역 
                WHERE 설비내역 IS NOT NULL 
                ORDER BY 설비내역;
            """)
            
            print(f"SQL: {sql}")
            
            data = db.execute(sql).mappings().all()
            return [dict(r) for r in data]
        
        finally:
            db.close()

    def get_breakDown_detail(self,req: MoldBreakdownRequest):
        db: Session = next(get_db())
        try:
           
            params = {
                "plant": req.plant,
                "worker": req.worker,
                "line": req.line,
                "itemCd": req.itemCd,
                "ym": req.ym,
                "start_date": req.start_date,
                "end_date": req.end_date
            }
            
            sql = text("""
                  WITH prod_filt AS (
                    SELECT DISTINCT 플랜트, 책임자, 작업장, 자재번호, 자재명
                    FROM AJIN_newDB.생산내역
                    WHERE 플랜트 = :plant
                      AND 책임자 = :worker
                      AND 작업장 = :line
                      AND 자재번호 = :itemCd
                  )
                  SELECT
                    DATE_FORMAT(b.기본종료일, '%Y-%m') AS ym, 
                    b.*
                  FROM AJIN_newDB.금형고장내역 AS b
                  JOIN prod_filt AS p
                    ON b.설비내역 LIKE CONCAT('%', p.자재번호, '%')
                  WHERE b.오더유형내역 = '고장점검(BM)'
                    AND b.기본종료일 IS NOT NULL
                    AND b.기본종료일 BETWEEN :start_date AND :end_date
                    AND DATE_FORMAT(b.기본종료일, '%Y-%m') = :ym
                  ORDER BY b.기본종료일 ASC, b.오더번호 ASC;
            """)

            print(f"SQL: {sql}")
            print(f"파라미터: {params}")
            
            data = db.execute(sql, params).mappings().all()
            print("_"*100)
            print(data)
            return [dict(r) for r in data]
        
        finally:
            db.close()

    def get_mold_cleaning_ranked_data(self, req: MoldBreakdownRequest):
        """
        금형세척주기와 금형타발수관리 테이블을 조인하여 설비별 최신 데이터 조회
        """
        db: Session = next(get_db())
        try:
            params = {
                "plant": req.plant,
                "worker": req.worker,
                "line": req.line,
                "itemCd": req.itemCd
            }
            
            sql = text("""
                WITH prod_filt AS (
                  SELECT DISTINCT 플랜트, 책임자, 작업장, 자재번호, 자재명
                  FROM AJIN_newDB.생산내역
                  WHERE 플랜트 = :plant
                    AND 책임자 = :worker
                    AND 작업장 = :line
                    AND 자재번호 IS NOT NULL AND 자재번호 = :itemCd
                    AND 자재명 IS NOT NULL AND TRIM(자재명) <> ''
                ),
                ranked AS (
                  SELECT
                      prod.플랜트, prod.책임자, prod.자재번호, prod.자재명,
                      wash.설비내역, wash.기본시작일, wash.기본종료일,
                      shot.금형번호,
                      ROW_NUMBER() OVER (
                        PARTITION BY wash.설비내역
                        ORDER BY COALESCE(wash.기본종료일, wash.기본시작일) DESC,
                                 wash.기본시작일 DESC,
                                 shot.금형번호 DESC
                      ) AS rn
                  FROM AJIN_newDB.금형세척주기 AS wash
                  JOIN AJIN_newDB.금형타발수관리 AS shot
                    ON wash.설비내역 = shot.금형내역
                  JOIN prod_filt AS prod
                    ON wash.설비내역 LIKE CONCAT('%', prod.자재번호, '%')
                )
                SELECT *
                FROM ranked
                WHERE rn = 1;
            """)

            print(f"SQL: {sql}")
            print(f"파라미터: {params}")
            
            data = db.execute(sql, params).mappings().all()
            print("_"*100)
            print(data)
            return [dict(r) for r in data]
        
        finally:
            db.close()

    def get_mold_shot_analysis(self, mold_code: str):
        """
        금형타발수관리 테이블에서 특정 금형번호의 점검 분석 데이터 조회
        """
        # mold_code가 None이거나 빈 값인 경우 빈 결과 반환
        if not mold_code or mold_code.strip() == "":
            print(f"mold_code가 비어있음: {mold_code}")
            return []
            
        db: Session = next(get_db())
        try:
            params = {
                "moldCode": mold_code.strip()
            }
            
            sql = text("""
                SELECT
                  `진행률(%)`,
                  ROUND(`누적 Shot 수` / NULLIF(`유지보수주기`, 0), 2) AS `총 점검수`,
                  ROUND(`점검타발수` / NULLIF(`유지보수주기` * 0.8, 0) * 100, 2) AS `80프로대비비율(%)`,
                  CASE
                    WHEN (`유지보수주기` * 0.8) - `점검타발수` > 0
                      THEN CONCAT('+', ROUND((`유지보수주기` * 0.8) - `점검타발수`, 2))
                    WHEN (`유지보수주기` * 0.8) - `점검타발수` = 0
                      THEN '0.00'
                    ELSE
                      ROUND((`유지보수주기` * 0.8) - `점검타발수`, 2)
                  END AS `80프로대비수치`,
                  ROUND(`점검타발수` / NULLIF(`유지보수주기` * 0.9, 0) * 100, 2) AS `90프로대비비율(%)`,
                  CASE
                    WHEN (`유지보수주기` * 0.9) - `점검타발수` > 0
                      THEN CONCAT('+', ROUND((`유지보수주기` * 0.9) - `점검타발수`, 2))
                    WHEN (`유지보수주기` * 0.9) - `점검타발수` = 0
                      THEN '0.00'
                    ELSE
                      ROUND((`유지보수주기` * 0.9) - `점검타발수`, 2)
                  END AS `90프로대비수치`
                FROM AJIN_newDB.`금형타발수관리` 
                WHERE 금형타발수관리.금형번호 = :moldCode;
            """)

            print(f"SQL: {sql}")
            print(f"파라미터: {params}")
            
            data = db.execute(sql, params).mappings().all()
            print("_"*100)
            print(f"조회된 데이터 개수: {len(data)}")
            print(data)
            
            # 데이터가 없는 경우 로그 출력
            if not data:
                print(f"금형번호 '{mold_code}'에 대한 데이터를 찾을 수 없습니다.")
            
            return [dict(r) for r in data]
        
        finally:
            db.close()

mold_chart_service = Mold_chart_service()
