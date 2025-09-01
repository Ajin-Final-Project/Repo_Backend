from typing import Optional, List
from pydantic import BaseModel, Field

class moldShotCount(BaseModel):
    # 생산내역 필터링 조건
    plant: Optional[str] = None                       # 플랜트
    responsible_person: Optional[str] = None          # 책임자
    work_center: Optional[str] = None                 # 작업장
    material_no: Optional[str] = None                 # 자재번호
    material_name: Optional[str] = None               # 자재명
    
    # 금형세척주기 검색 조건
    equipment_detail: Optional[str] = None            # 설비내역
    order_type: Optional[str] = None                  # 오더유형
    action_content: Optional[str] = None              # 조치내용
    basic_start_date: Optional[str] = None            # 기본시작일
    basic_end_date: Optional[str] = None              # 기본종료일
    
    # 금형타발수관리 검색 조건
    mold_no: Optional[str] = None                     # 금형번호
    measuring_point: Optional[str] = None             # 측정지점
    measuring_position: Optional[str] = None          # 측정위치
    cum_shot_min: Optional[int] = None                # 누적 Shot 수(이상)
    cum_shot_max: Optional[int] = None                # 누적 Shot 수(이하)
    inspection_hit_count: Optional[int] = None        # 점검타발수
    maintenance_cycle: Optional[int] = None           # 유지보수주기
    progress_min: Optional[float] = None              # 진행률(%) (이상)
    progress_max: Optional[float] = None              # 진행률(%) (이하)
    
    # 날짜 범위 검색
    start_date: Optional[str] = None                  # 검색 시작일 (YYYY-MM-DD)
    end_date: Optional[str] = None                    # 검색 종료일 (YYYY-MM-DD)
