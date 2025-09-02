from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.bottleneckOverview import BottleneckOverviewRequest


class BottleneckOverviewService:

    # =========================
    # 병목 개요 조회
    # =========================
    def get_bottleneck_data(self, req: BottleneckOverviewRequest):
        db: Session = next(get_db())
        try:
            where_conditions = []
            params = {}

            # ✅ 기간 조회
            if getattr(req, "Time_Start", None) and getattr(req, "Time_End", None):
                where_conditions.append("DATE(`Time_Now`) BETWEEN DATE(:Time_Start) AND DATE(:Time_End)")
                params["Time_Start"] = req.Time_Start
                params["Time_End"] = req.Time_End

            # ✅ 단일 날짜 조회
            elif req.Time_Now:
                where_conditions.append("DATE(`Time_Now`) = DATE(:Time_Now)")
                params["Time_Now"] = req.Time_Now

            # ✅ 조건 없으면 전체 조회
            else:
                where_conditions.append("1=1")

            sql = f"""
                SELECT *
                FROM AJIN_newDB.bottleneck_overview
                WHERE {' AND '.join(where_conditions)}
                ORDER BY Time_Now DESC
                LIMIT 40
            """

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()


bottleneck_overview_service = BottleneckOverviewService()
