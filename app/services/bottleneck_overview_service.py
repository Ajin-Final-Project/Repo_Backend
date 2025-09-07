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
                SELECT   
                    Time_Now, Bottleneck_actual, Bottleneck_pred, c_TotalProducts,
                    Blanking_SKU1_Queue, Blanking_SKU2_Queue, Blanking_SKU3_Queue, Blanking_SKU4_Queue,
                    Press1_Queue, Press2_Queue, Press3_Queue, Press4_Queue,
                    Cell1_Queue, Cell2_Queue, Cell3_Queue, Cell4_Queue,
                    Forklift_Blanking_Queue, Forklift_Press_Queue, Forklift_Assembly_Queue,
                    Cell_SKU1_Queue, Cell_SKU2_Queue, Cell_SKU3_Queue, Cell_SKU4_Queue,
                    Bottleneck_actual_SKU1, Bottleneck_actual_SKU2, Bottleneck_actual_SKU3, Bottleneck_actual_SKU4,
                    Bottleneck_pred_SKU1, Bottleneck_pred_SKU2, Bottleneck_pred_SKU3, Bottleneck_pred_SKU4,
                    Bottleneck_actual_Blanking, Bottleneck_actual_Press, Bottleneck_actual_Cell,
                    Bottleneck_pred_Blanking, Bottleneck_pred_Press, Bottleneck_pred_Cell,
                    c_Cell1_SKU1, c_Cell1_SKU2, c_Cell1_SKU3, c_Cell1_SKU4,
                    c_Cell2_SKU1, c_Cell2_SKU2, c_Cell2_SKU3, c_Cell2_SKU4,
                    c_Cell3_SKU1, c_Cell3_SKU2, c_Cell3_SKU3, c_Cell3_SKU4,
                    c_Cell4_SKU1, c_Cell4_SKU2, c_Cell4_SKU3, c_Cell4_SKU4
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
