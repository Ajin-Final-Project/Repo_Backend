from typing import Optional
from pydantic import BaseModel
from decimal import Decimal

class inspectionGridRequest(BaseModel):
    start_work_date: Optional[str] = None  # 시작일 (YYYY-MM-DD)
    end_work_date: Optional[str] = None    # 종료일 (YYYY-MM-DD)

    businessPlace: Optional[str] = None    # 사업장
    plant: Optional[str] = None            # 공장
    process: Optional[str] = None          # 공정
    equipment: Optional[str] = None        # 설비

    inspectionType: Optional[str] = None   # 검사구분
    itemNumber: Optional[str] = None       # 품번
    # 프론트엔드에서 '품명'은 자리만 확보중이지만, 추후를 위해 포함해도 무방
    # itemName: Optional[str] = None

    reportDate: Optional[str] = None       # 보고일(단일) - 기본은 기간 필터 사용
    shiftType: Optional[str] = None        # 주야구분
    workSequence: Optional[int] = None     # 작업순번
    workType: Optional[str] = None         # 작업구분
    inspectionSequence: Optional[int] = None  # 검사순번
    inspectionItemName: Optional[str] = None  # 검사항목명 (LIKE)
    inspectionDetails: Optional[str] = None   # 검사내용 (LIKE)
    productionValue: Optional[Decimal] = None # 생산
