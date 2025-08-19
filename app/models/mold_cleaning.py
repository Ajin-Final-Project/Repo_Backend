from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

class MoldCleaningCycleRequest(BaseModel):
    equipment_detail: Optional[str] = None   # 설비내역
    order_type: Optional[str] = None         # 오더유형
    order_type_detail: Optional[str] = None  # 오더유형내역
    order_detail: Optional[str] = None       # 오더내역
    action_detail: Optional[str] = None      # 조치내용

    startDate: Optional[str] = None  # 검색 시작일
    endDate: Optional[str] = None    # 검색 종료일