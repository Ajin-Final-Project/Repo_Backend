from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, validator


class MoldBreakdownRequest(BaseModel):
    status: Optional[str] = None
    document: Optional[str] = None
    function_location: Optional[str] = None
    function_location_detail: Optional[str] = None
    equipment: Optional[int] = None
    equipment_detail: Optional[str] = None
    order_type: Optional[str] = None
    order_type_detail: Optional[str] = None
    order_no: Optional[int] = None
    order_detail: Optional[str] = None
    notification_no: Optional[int] = None
    failure: Optional[str] = None

    start_date: Optional[str] = None
    end_date: Optional[str] = None

    plant: Optional[str] = None
    worker: Optional[str] = None
    line : Optional[str] = None
    itemCd: Optional[str] = None
    ym : Optional[str] = None
    mold_code: Optional[str] = None

    @validator('equipment', 'order_no', 'notification_no', pre=True)
    def zero_or_empty_to_none(cls, v):
        # "" / "0" / 0 모두 None 처리
        if v in (None, "", "0", 0):
            return None
        return int(v)