from typing import Optional
from pydantic import BaseModel, validator

class ProductForecastDailyRequest(BaseModel):

    @validator('*', pre=True)
    def blank_to_none(cls, v):
        return None if v == '' else v

    id: Optional[int] = None
    date: Optional[str] = None             # 단일 날짜 (기존 호환용)
    start_work_date: Optional[str] = None  # ✅ 조회 시작일 (YYYY-MM-DD)
    end_work_date: Optional[str] = None    # ✅ 조회 종료일 (YYYY-MM-DD)

    sku: Optional[str] = None              # SKU 코드
    pred: Optional[float] = None           # 예측 생산량
    actual: Optional[int] = None           # 실제 생산량
    error: Optional[float] = None          # 오차
    abs_error: Optional[float] = None      # 절대 오차
    pct_error: Optional[float] = None      # 예측 오차 %
    hourly_avg: Optional[float] = None     # 시간당 평균
