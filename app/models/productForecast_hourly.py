from typing import Optional
from pydantic import BaseModel, validator

class ProductForecastHourlyRequest(BaseModel):

    @validator('*', pre=True)
    def blank_to_none(cls, v):
        return None if v == '' else v

    id: Optional[int] = None
    date: Optional[str] = None                 # 날짜
    slot_start: Optional[str] = None           # 구간 시작 시간
    slot_end: Optional[str] = None             # 구간 종료 시간
    minutes_in_slot: Optional[int] = None      # 구간 분 단위
    sku: Optional[str] = None                  # SKU 코드
    prediction: Optional[int] = None           # 예측 생산량
    actual: Optional[int] = None               # 실제 생산량
    error: Optional[int] = None                # 오차
    abs_error: Optional[int] = None            # 절대 오차
    pred_match_pct: Optional[float] = None     # 예측 일치율(%)
    capacity: Optional[int] = None             # 설비 Capacity
    uph: Optional[int] = None                  # Unit per Hour
    uph_achievement_pct: Optional[float] = None # UPH 달성률(%)
    daily_target: Optional[int] = None         # 일일 목표
    cum_actual_today: Optional[int] = None     # 당일 누적 생산량
    current_achievement_pct: Optional[float] = None # 현재 달성률(%)
    util_actual: Optional[float] = None        # 실제 가동률
    blanking_util: Optional[float] = None      # 블랭킹 설비 가동률
    press_util: Optional[float] = None         # 프레스 설비 가동률
    assembly_util: Optional[float] = None      # 조립 셀 가동률
