from fastapi import APIRouter
from app.services.bottleneck_overview_service import bottleneck_overview_service
from app.models.bottleneckOverview import BottleneckOverviewRequest

router = APIRouter(prefix="/bottleneck", tags=["Bottleneck"])

@router.post("/overview")
def get_bottleneck_overview(req: BottleneckOverviewRequest):
    try:
        data = bottleneck_overview_service.get_bottleneck_data(req)
        return {
            "message": "병목 정보 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        return {
            "message": "병목 정보 조회 실패",
            "error": str(e)
        }
