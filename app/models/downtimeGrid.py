# app/models/downtimeGrid.py
from typing import Optional
from pydantic import BaseModel,validator

class DowntimeGridResquest(BaseModel):

    @validator('*', pre=True)
    def blank_to_none(cls, v):
        return None if v == '' else v

    # 공통 기간
    start_work_date: Optional[str] = None # 시작일
    end_work_date: Optional[str] = None # 종료일

    # 필터/컬럼
    plant: Optional[str] = None # 플랜트
    worker: Optional[str] = None # 작업자
    workplace: Optional[str] = None  # ← press(작업장)값이 여기에 들어온다
    itemCode: Optional[str] = None   # ← 자재번호
    carModel: Optional[str] = None # 차종

    downtimeCode: Optional[str] = None # 비가동코드
    downtimeName: Optional[str] = None # 비가동명
    downtimeMinutes: Optional[int] = None # 비가동(분)
    note: Optional[str] = None

    shift: Optional[str] = None        # 주간구분
    productName: Optional[str] = None  # 품명
    itemType: Optional[str] = None     # 품목구분
    categoryMain: Optional[str] = None # 대분류
    categorySub: Optional[str] = None  # 소분류