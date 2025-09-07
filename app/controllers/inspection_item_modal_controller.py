from fastapi import APIRouter
from app.models.inspection_item_modal import InspectionItemModalReq
from app.services.inspection_item_modal_service import inspection_item_modal_service

# 검사시스템 전용 모달 엔드포인트
router = APIRouter(prefix="/inspection_modal", tags=["inspection_modal"])

@router.post("/item_list")
def list_items(req: InspectionItemModalReq):
    """
    생산_검사에서 자재번호/자재명 전체(중복 제거) 조회
    - q(품번/품명 LIKE), 공장/공정/설비, work_date 기간(startDate~endDate) 필터 지원
    """
    data = inspection_item_modal_service.list_items(req)
    return {
        "message": "검사(생산_검사) 품번/품명 조회 성공",
        "count": len(data),
        "data": data,
    }
