from fastapi import APIRouter
from app.services.defect_grid_service import defect_grid_service
from app.models.defectGrid import DefectGridRequest

router = APIRouter(prefix="/defect_grid", tags=["defect"])

@router.post("/list")
def get_defect_list(request: DefectGridRequest):
    try:
        print("[DefectGrid] request:", request)
        data = defect_grid_service.get_defect_list(request)
        return {
            "message": "불량공정(생산_불량) 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"[DefectGrid] 조회 오류: {str(e)}")
        return {
            "message": "불량공정(생산_불량) 조회 실패",
            "error": str(e)
        }
