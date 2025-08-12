from fastapi import APIRouter
from pydantic import BaseModel
from typing import List,Optional
from app.services.process_line_service import process_line_service  # 인스턴스


router = APIRouter(prefix="/process_line", tags=["process_line"])
service = process_line_service


class ProcessLineRequest(BaseModel):
    company_code: Optional[int] = None
    company_code_list: Optional[List[int]] = None
    
@router.post("/list")
def get_process_line(request: ProcessLineRequest):
    try:
        data = service.get_process_line(request.company_code)
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

@router.post("/parameter_list_data")
def get_process_line_list(request:ProcessLineRequest):
    try:
        data = service.get_process_line_list(request.company_code_list)
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



