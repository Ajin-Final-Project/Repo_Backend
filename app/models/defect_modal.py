# app/models/defect_modal.py
from typing import Optional
from pydantic import BaseModel

class DefectModalReq(BaseModel):
    # 날짜
    startDate: Optional[str] = None   # YYYY-MM-DD
    endDate:   Optional[str] = None

    # 필터
    factory:   Optional[str] = None
    process:   Optional[str] = None
    equipment: Optional[str] = None
    partNo:    Optional[str] = None
    item:      Optional[str] = None

    # 페이지(선택)
    limit:  Optional[int] = 500
    offset: Optional[int] = 0
