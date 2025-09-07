# from typing import Optional
# from pydantic import BaseModel
# from decimal import Decimal

# class inspectionGridRequest(BaseModel):
#     # ===== 기존 이름 =====
#     start_work_date: Optional[str] = None  # 시작일 (YYYY-MM-DD)
#     end_work_date: Optional[str] = None    # 종료일 (YYYY-MM-DD)

#     businessPlace: Optional[str] = None    # 사업장
#     plant: Optional[str] = None            # 공장
#     process: Optional[str] = None          # 공정
#     equipment: Optional[str] = None        # 설비

#     inspectionType: Optional[str] = None   # 검사구분
#     itemNumber: Optional[str] = None       # 품번
#     # itemName: Optional[str] = None       # (미사용 시 주석)

#     reportDate: Optional[str] = None       # 보고일(단일)
#     shiftType: Optional[str] = None        # 주야구분
#     workSequence: Optional[int] = None     # 작업순번
#     workType: Optional[str] = None         # 작업구분
#     inspectionSequence: Optional[int] = None  # 검사순번
#     inspectionItemName: Optional[str] = None  # 검사항목명 (LIKE)
#     inspectionDetails: Optional[str] = None   # 검사내용 (LIKE)
#     productionValue: Optional[Decimal] = None # 생산

#     # ===== 차트식 alias(동일 의미) =====
#     start_date: Optional[str] = None
#     end_date: Optional[str] = None

#     factory: Optional[str] = None          # = plant
#     partNo: Optional[str] = None           # = itemNumber
#     item: Optional[str] = None             # = itemName
#     inspType: Optional[str] = None         # = inspectionType


from typing import Optional
from pydantic import BaseModel
from decimal import Decimal

class inspectionGridRequest(BaseModel):
    # ===== 기존 이름 =====
    start_work_date: Optional[str] = None  # 시작일 (YYYY-MM-DD)
    end_work_date: Optional[str] = None    # 종료일 (YYYY-MM-DD)

    businessPlace: Optional[str] = None    # 사업장
    plant: Optional[str] = None            # 공장
    process: Optional[str] = None          # 공정
    equipment: Optional[str] = None        # 설비

    inspectionType: Optional[str] = None   # 검사구분
    itemNumber: Optional[str] = None       # 품번
    # itemName: Optional[str] = None       # (미사용 시 주석)

    reportDate: Optional[str] = None       # 보고일(단일)
    shiftType: Optional[str] = None        # 주야구분
    workSequence: Optional[int] = None     # 작업순번
    workType: Optional[str] = None         # 작업구분
    inspectionSequence: Optional[int] = None  # 검사순번
    inspectionItemName: Optional[str] = None  # 검사항목명 (LIKE)
    inspectionDetails: Optional[str] = None   # 검사내용 (LIKE)
    productionValue: Optional[Decimal] = None # 생산

    # ===== 차트식 alias(동일 의미) =====
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    factory: Optional[str] = None          # = plant
    partNo: Optional[str] = None           # = itemNumber
    item: Optional[str] = None             # = itemName
    inspType: Optional[str] = None         # = inspectionType
