from typing import List, Optional
from pydantic import BaseModel

class DowntimeGridResquest(BaseModel):
    # 검색 공통
    start_work_date: Optional[str] = None   # 시작일 (근무일자 from)
    end_work_date: Optional[str] = None     # 끝나는일 (근무일자 to)

    # 기본 컬럼 매핑
    plant: Optional[str] = None             # 플랜트 (varchar(50))
    worker: Optional[str] = None            # 책임자 (varchar(50))
    workplace: Optional[str] = None         # 작업장 (varchar(50))
    itemCode: Optional[str] = None          # 자재번호 (varchar(50))
    carModel: Optional[str] = None          # 차종 (varchar(50))

    downtimeCode: Optional[str] = None      # 비가동코드 (varchar(50))
    downtimeName: Optional[str] = None      # 비가동명 (varchar(100))
    downtimeMinutes: Optional[int] = None   # 비가동(분) (int)
    note: Optional[str] = None              # 비고 (text)