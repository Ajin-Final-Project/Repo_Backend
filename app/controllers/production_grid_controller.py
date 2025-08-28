from fastapi import APIRouter
from typing import List,Optional
from app.services.production_grid_service import production_grid_service
from app.models.productionGrid import ProductionGridResquest 


router = APIRouter(prefix="/production_grid", tags=["production"])
service = production_grid_service



@router.post("/list")
def get_production_list(request: ProductionGridResquest):
    try:
        print(request)
        data = service.get_production_list(request)
    
        return {
            "message": "ProcessLine 테이블 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"ProcessLine 테이블 조회 중 오류 발생: {str(e)}")
        return {
            "message": "ProcessLine 테이블 조회 실패",
            "error": str(e)
        }




