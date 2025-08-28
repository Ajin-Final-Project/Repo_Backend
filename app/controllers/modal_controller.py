from fastapi import APIRouter
from typing import List,Optional
from app.services.modal_service import Modal_service
from pydantic import BaseModel

router = APIRouter(prefix="/modal", tags=["modal"])
service = Modal_service()

class ItemListReq(BaseModel):
    item: Optional[str] = None
    plant: Optional[str] = None
    worker: Optional[str] = None
    line: Optional[str] = None

    
@router.post("/item_list")
def get_item_list(req :ItemListReq):
    try:
        data = service.get_item_list(req.item, req.plant, req.worker, req.line)
        return {
            "message": "품목 테이블 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"품목 테이블 조회 중 오류 발생: {str(e)}")
        return {
            "message": "품목 테이블 조회 실패",
            "error": str(e)
        }





