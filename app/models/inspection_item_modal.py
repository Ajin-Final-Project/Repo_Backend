from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

class InspectionItemModalReq(BaseModel):
    """
    모달 요청 파라미터
    - startDate/endDate는 work_date 기준
    """
    q: Optional[str] = Field(default=None)

    plant: Optional[str] = None     # 공장 -> i.plant
    worker: Optional[str] = None    # 공정(작업장) -> i.process
    line: Optional[str] = None      # 설비(라인) -> i.equipment

    startDate: Optional[str] = None # YYYY-MM-DD
    endDate: Optional[str] = None   # YYYY-MM-DD

    selectedItemCode: Optional[str] = None
