from typing import Optional, List
from pydantic import BaseModel, Field

class moldShotCount(BaseModel):
    plant: Optional[int] = None                       # 플랜트
    equipment_type: Optional[str] = None              # 설비유형
    mold_no: Optional[int] = None                     # 금형번호
    mold_name: Optional[str] = None                   # 금형내역
    measuring_point: Optional[int] = None             # 측정지점
    measuring_position: Optional[str] = None          # 측정위치

    cum_shot_min: Optional[int] = None                # 누적 Shot 수(이상)
    cum_shot_max: Optional[int] = None                # 누적 Shot 수(이하)
    inspection_hit_count: Optional[int] = None        # 점검타발수(정확값 또는 기준)
    maintenance_cycle: Optional[int] = None           # 유지보수주기
    maintenance_cycle_unit: Optional[str] = None      # 유지보수주기단위 (예: '타', '일' 등)
    progress_min: Optional[float] = None              # 진행률(%) (이상)
    progress_max: Optional[float] = None              # 진행률(%) (이하)

    functional_location: Optional[str] = None         # 기능위치
    functional_location_desc: Optional[str] = None    # 기능위치 내역
    planner_group: Optional[str] = None               # 계획자그룹
    maintenance_plan: Optional[str] = None            # 유지보수계획

    startDate: Optional[str] = None                   # 검색 시작일 (YYYY-MM-DD)
    endDate: Optional[str] = None                     # 검색 종료일 (YYYY-MM-DD)

    part_no1: Optional[str] = None
    part_no2: Optional[str] = None
    part_no3: Optional[str] = None
    part_no4: Optional[str] = None
    part_no5: Optional[str] = None
