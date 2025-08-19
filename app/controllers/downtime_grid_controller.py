from fastapi import APIRouter
from typing import List,Optional
from app.services.downtime_grid_service import downtime_grid_service
from app.models.downtimeGrid import DowntimeGridResquest 


router = APIRouter(prefix="/downtime_grid", tags=["downtime"])
service = downtime_grid_service


@router.post("/list")
def get_downtime_list(request: DowntimeGridResquest):
    try:
        print(request)
        data = service.get_downtime_list(request)
        # print('data============', data)
        return {
            "message": "비가동시간 및 현황 테이블 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"비가동시간 및 현황 테이블 조회 중 오류 발생: {str(e)}")
        return {
            "message": "비가동시간 및 현황 테이블 조회 실패",
            "error": str(e)
        }