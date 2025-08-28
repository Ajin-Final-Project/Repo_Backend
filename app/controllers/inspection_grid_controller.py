from fastapi import APIRouter
from typing import List,Optional
from app.services.inspection_grid_service import inspection_grid_service
from app.models.inspectionGrid import inspectionGridRequest


router = APIRouter(prefix="/inspection_grid", tags=["inspection"])
service = inspection_grid_service



@router.post("/list")
def get_inspection_list(request: inspectionGridRequest):
    try:
        print(request)
        data = service.get_inspection_list(request)

        return {
            "message": "검사내역 테이블 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"검사내역 테이블 조회 중 오류 발생: {str(e)}")
        return {
            "message": "검사내역 테이블 조회 실패",
            "error": str(e)
        }




