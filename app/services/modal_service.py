from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.mold_BreakDown import MoldBreakdownRequest
from sqlalchemy.sql import text
from sqlalchemy.orm import Session

class Modal_service:

    def get_item_list(self, item: str | None ,plant: str|None, worker: str|None, line: str| None):
        db: Session = next(get_db())
        try:
            params = {}
            # 서브쿼리(별칭 없음)용 / 바깥쿼리(별칭 t)용 where 분리
            inner_where_sql = ""
            outer_where_sql = ""
            
            if plant and worker and line :
                params["line"] = line
                params["plant"] = plant
                params["worker"] = worker


                inner_where_sql +=  "AND 플랜트 = :plant AND 책임자 = :worker AND 작업장 = :line"
                outer_where_sql += "AND 플랜트 = :plant AND 책임자 = :worker AND 작업장 = :line"

                
            if item:
                params["item"] = f"%{item}%"
                inner_where_sql += " AND (자재번호 LIKE :item OR 자재명 LIKE :item)"
                outer_where_sql += " AND (t.자재번호 LIKE :item OR t.자재명 LIKE :item)"

            sql_str = f"""
                SELECT t.자재번호, t.자재명, t.실적번호
                FROM AJIN_newDB.생산내역 AS t
                JOIN (
                    SELECT
                        자재번호,
                        MAX(CAST(실적번호 AS UNSIGNED)) AS 최신실적번호
                    FROM AJIN_newDB.생산내역
                    WHERE 1=1
                        {inner_where_sql}
                        AND 자재번호 <> '미등록(93)'
                    GROUP BY 자재번호
                ) AS x
                ON x.자재번호 = t.자재번호
                AND x.최신실적번호 = CAST(t.실적번호 AS UNSIGNED)
                WHERE 1=1
                    {outer_where_sql}
                    AND t.자재번호 <> '미등록(93)'
                ORDER BY CAST(t.실적번호 AS UNSIGNED) DESC , t.자재번호 ASC;
            """

            print(sql_str, params)  # 디버그용
            rows = db.execute(text(sql_str), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()

modal_service = Modal_service()
