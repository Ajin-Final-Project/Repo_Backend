# app/models/downtimeGrid.py
from typing import Optional
from pydantic import BaseModel

class DowntimeGridResquest(BaseModel):
    # 공통 기간
    start_work_date: Optional[str] = None
    end_work_date: Optional[str] = None

    # 필터/컬럼
    plant: Optional[str] = None
    worker: Optional[str] = None
    workplace: Optional[str] = None  # ← press(작업장)값이 여기에 들어온다
    itemCode: Optional[str] = None   # ← 자재번호
    carModel: Optional[str] = None

    downtimeCode: Optional[str] = None
    downtimeName: Optional[str] = None
    downtimeMinutes: Optional[int] = None
    note: Optional[str] = None
