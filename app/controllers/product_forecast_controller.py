from fastapi import APIRouter
from app.services.product_forecast_service import product_forecast_service
from app.models.productForecast_daily import ProductForecastDailyRequest
from app.models.productForecast_hourly import ProductForecastHourlyRequest

router = APIRouter(prefix="/forecast", tags=["Forecast"])

@router.post("/daily")
def get_daily_forecast(req: ProductForecastDailyRequest):
    try:
        data = product_forecast_service.get_daily_forecast(req)
        return {
            "message": "일별 생산량 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        return {
            "message": "일별 생산량 조회 실패",
            "error": str(e)
        }

@router.post("/hourly")
def get_hourly_forecast(req: ProductForecastHourlyRequest):
    try:
        data = product_forecast_service.get_hourly_forecast(req)
        return {
            "message": "시간별 생산량 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        return {
            "message": "시간별 생산량 조회 실패",
            "error": str(e)
        }
