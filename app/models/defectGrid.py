from typing import Optional
from pydantic import BaseModel

class DefectGridRequest(BaseModel):
    # 날짜 필터
    start_work_date: Optional[str] = None   # 시작일(YYYY-MM-DD)
    end_work_date: Optional[str] = None     # 종료일(YYYY-MM-DD)

    # 텍스트/식별자 필터
    workplace: Optional[str] = None         # 작업장
    itemInfo: Optional[str] = None          # 자재정보 (자재번호+자재명 등 텍스트)
    carModel: Optional[str] = None          # 차종
    orderType: Optional[str] = None         # 수주유형
    defectCode: Optional[str] = None        # 불량코드
    defectType: Optional[str] = None        # 불량유형
    remark: Optional[str] = None            # 비고 (부분 검색)
    worker: Optional[str] = None            # 작업자

    # 수량 필터
    goodItemCount: Optional[int] = None     # 양품수량
    waitItemCount: Optional[int] = None     # 판정대기
    rwkCount: Optional[int] = None          # RWK 수량
    scrapCount: Optional[int] = None        # 폐기 수량
