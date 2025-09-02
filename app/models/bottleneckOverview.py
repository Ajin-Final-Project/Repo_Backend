from typing import Optional
from pydantic import BaseModel, validator

class BottleneckOverviewRequest(BaseModel):

    @validator('*', pre=True)
    def blank_to_none(cls, v):
        return None if v == '' else v

    id: Optional[int] = None
    Time_Now: Optional[str] = None

    # 주요 Queue 데이터
    Blanking_SKU1_Queue: Optional[float] = None
    Blanking_SKU2_Queue: Optional[float] = None
    Blanking_SKU3_Queue: Optional[float] = None
    Blanking_SKU4_Queue: Optional[float] = None
    Press1_Queue: Optional[float] = None
    Press2_Queue: Optional[float] = None
    Press3_Queue: Optional[float] = None
    Press4_Queue: Optional[float] = None
    Cell1_Queue: Optional[float] = None
    Cell2_Queue: Optional[float] = None
    Cell3_Queue: Optional[float] = None
    Cell4_Queue: Optional[float] = None

    # Cell 별 SKU 생산량
    c_Cell1_SKU1: Optional[int] = None
    c_Cell1_SKU2: Optional[int] = None
    c_Cell1_SKU3: Optional[int] = None
    c_Cell1_SKU4: Optional[int] = None
    c_Cell2_SKU1: Optional[int] = None
    c_Cell2_SKU2: Optional[int] = None
    c_Cell2_SKU3: Optional[int] = None
    c_Cell2_SKU4: Optional[int] = None
    c_Cell3_SKU1: Optional[int] = None
    c_Cell3_SKU2: Optional[int] = None
    c_Cell3_SKU3: Optional[int] = None
    c_Cell3_SKU4: Optional[int] = None
    c_Cell4_SKU1: Optional[int] = None
    c_Cell4_SKU2: Optional[int] = None
    c_Cell4_SKU3: Optional[int] = None
    c_Cell4_SKU4: Optional[int] = None

    # Forklift Queue
    Forklift_Blanking_Queue: Optional[float] = None
    Forklift_Press_Queue: Optional[float] = None
    Forklift_Assembly_Queue: Optional[float] = None

    c_TotalProducts: Optional[int] = None
    Bottleneck_actual: Optional[str] = None

    # 퍼센트(%) 컬럼
    Blanking_SKU1_Queue_Percent: Optional[float] = None
    Blanking_SKU2_Queue_Percent: Optional[float] = None
    Blanking_SKU3_Queue_Percent: Optional[float] = None
    Blanking_SKU4_Queue_Percent: Optional[float] = None
    Press1_Queue_Percent: Optional[float] = None
    Press2_Queue_Percent: Optional[float] = None
    Press3_Queue_Percent: Optional[float] = None
    Press4_Queue_Percent: Optional[float] = None
    Cell1_Queue_Percent: Optional[float] = None
    Cell2_Queue_Percent: Optional[float] = None
    Cell3_Queue_Percent: Optional[float] = None
    Cell4_Queue_Percent: Optional[float] = None
    Forklift_Blanking_Queue_Percent: Optional[float] = None
    Forklift_Press_Queue_Percent: Optional[float] = None
    Forklift_Assembly_Queue_Percent: Optional[float] = None

    # 추가 필드 (예측 결과)
    Cell_SKU1_Queue: Optional[float] = None
    Cell_SKU2_Queue: Optional[float] = None
    Cell_SKU3_Queue: Optional[float] = None
    Cell_SKU4_Queue: Optional[float] = None

    Bottleneck_pred: Optional[str] = None
    Bottleneck_actual_SKU1: Optional[str] = None
    Bottleneck_actual_SKU2: Optional[str] = None
    Bottleneck_actual_SKU3: Optional[str] = None
    Bottleneck_actual_SKU4: Optional[str] = None
    Bottleneck_pred_SKU1: Optional[str] = None
    Bottleneck_pred_SKU2: Optional[str] = None
    Bottleneck_pred_SKU3: Optional[str] = None
    Bottleneck_pred_SKU4: Optional[str] = None
    Bottleneck_actual_Blanking: Optional[str] = None
    Bottleneck_actual_Press: Optional[str] = None
    Bottleneck_actual_Cell: Optional[str] = None
    Bottleneck_pred_Blanking: Optional[str] = None
    Bottleneck_pred_Press: Optional[str] = None
    Bottleneck_pred_Cell: Optional[str] = None
