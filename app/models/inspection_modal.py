# from typing import Optional
# from pydantic import BaseModel

# class InspectionModalReq(BaseModel):
#     # 기간(보고일 기준; 시작/끝 아무거나만 있어도 OK)
#     start_date: Optional[str] = None   # YYYY-MM-DD
#     end_date:   Optional[str] = None

#     # 상위 필터(페이지와 동일 키)
#     plant: Optional[str] = None      # 공장
#     process: Optional[str] = None    # 공정
#     equipment: Optional[str] = None  # 설비

#     # 검색어
#     q: Optional[str] = None          # 품번/품명/검사항목명/검사내용
