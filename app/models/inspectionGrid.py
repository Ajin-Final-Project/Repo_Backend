from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal

class inspectionGridRequest(BaseModel):
    start_work_date: Optional[str] = None # 시작일
    end_work_date: Optional[str] = None   # 끝나는일
    businessPlace: Optional[str] = None       # 사업장
    plant: Optional[str] = None               # 공장
    process: Optional[str] = None             # 공정
    equipment: Optional[str] = None           # 설비
    inspectionType: Optional[str] = None      # 검사구분
    itemNumber: Optional[str] = None          # 품번
    reportDate: Optional[str] = None          # 보고일
    shiftType: Optional[str] = None           # 주야구분
    workSequence: Optional[int] = None        # 작업순번
    workType: Optional[str] = None            # 작업구분
    inspectionSequence: Optional[int] = None  # 검사순번
    inspectionItemName: Optional[str] = None  # 검사항목명
    inspectionDetails: Optional[str] = None   # 검사내용
    productionValue: Optional[Decimal] = None # 생산 (decimal 타입은 float보다 Decimal 사용 권장)
