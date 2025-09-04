from typing import List,Optional
from pydantic import BaseModel,validator

class ProductionGridResquest(BaseModel):

    @validator('*', pre=True)
    def blank_to_none(cls, v):
        return None if v == '' else v


    start_work_date: Optional[str] = None # 시작일
    end_work_date: Optional[str] = None   # 끝나는일
    productionNumber: Optional[str] = None # 실적번호
    plant: Optional[str] = None            # 플랜트
    worker: Optional[str] = None           # 책임자
    line: Optional[str] = None        # 작업장
    itemCode: Optional[str] = None         # 품목코드
    itemName: Optional[str] = None         # 품목이름
    carModel: Optional[str] = None         # 차종
    lot: Optional[str] = None              # lot
    sheetInputCoil: Optional[str] = None   # 시트투입코일
    runtime: Optional[str] = None          # 가동시간
    goodItemCount: Optional[int] = None    # 양품수량
    waitItemCount: Optional[int] = None    # 판정대기
    badItemCount: Optional[int] = None     # 불량수량
    productionItemNumber: Optional[int] = None  # 생산수량
    processBadItemCount: Optional[int] = None  # 공정불량
    componentDeliveryCount: Optional[int] = None # 구성품출고
    constructor: Optional[str] = None      # 생성자
    createDate: Optional[str] = None       # 생성일
    workplace: Optional[str] = None

class UPHProductionRequest(BaseModel):
    @validator('*', pre=True)
    def blank_to_none(cls, v):
        return None if v == '' else v
    
    start_date: Optional[str] = None  # 시작일
    end_date: Optional[str] = None    # 종료일
    itemCd: Optional[str] = None      # 자재번호