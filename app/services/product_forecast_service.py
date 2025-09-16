from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.productForecast_daily import ProductForecastDailyRequest
from app.models.productForecast_hourly import ProductForecastHourlyRequest


class ProductForecastService:

    # =========================
    # 1) 일별 예측 데이터
    # =========================
    def get_daily_forecast(self, req: ProductForecastDailyRequest):
        db: Session = next(get_db())
        try:
            where_conditions = []
            params = {}

            # DB 데이터 범위
            DB_START = "2024-01-01"
            DB_END   = "2025-06-30"

            start_date = req.start_work_date or DB_START
            end_date   = req.end_work_date or DB_END

            # 날짜 보정 (DB 범위 밖 방지)
            if start_date < DB_START:
                start_date = DB_START
            if end_date > DB_END:
                end_date = DB_END

            where_conditions.append("`date` BETWEEN :start_date AND :end_date")
            params["start_date"] = start_date
            params["end_date"] = end_date

            if req.sku:
                where_conditions.append("`sku` = :sku")
                params["sku"] = req.sku

            sql = f"""
                SELECT id, date, sku, pred, actual, error, abs_error, pct_error, hourly_avg
                FROM AJIN_newDB.daily_production
                WHERE {' AND '.join(where_conditions)}
                ORDER BY date ASC;
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()


    # =========================
    # 2) 시간별 예측 데이터
    # =========================
    def get_hourly_forecast(self, req: ProductForecastHourlyRequest):
        db: Session = next(get_db())
        try:
            where_conditions = []
            params = {}

            if req.date:
                where_conditions.append("`date` = :date")
                params["date"] = req.date

            if req.sku:
                where_conditions.append("`sku` = :sku")
                params["sku"] = req.sku

            if not where_conditions:
                where_conditions.append("1=1")

            sql = f"""
                SELECT 
                    id, date, slot_start, slot_end, minutes_in_slot, sku,
                    prediction, actual, error, abs_error,
                    pred_match_pct, capacity, uph, uph_achievement_pct,
                    daily_target, cum_actual_today, current_achievement_pct,
                    util_actual, blanking_util, press_util, assembly_util
                FROM AJIN_newDB.hourly_production
                WHERE {' AND '.join(where_conditions)}
                ORDER BY slot_start ASC
            """

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()


product_forecast_service = ProductForecastService()
