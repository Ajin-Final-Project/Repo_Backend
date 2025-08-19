# controllers/user_grid_controller.py
"""
[사용자(사원) 그리드 컨트롤러]
- URL prefix: /user_grid
- 역할: 프런트에서 올라오는 조회 요청을 받아 서비스에 위임하고 JSON으로 응답
"""

from fastapi import APIRouter
from app.services.user_grid_service import user_grid_service
from app.models.userGrid import UserGridRequest

# /user_grid 하위 엔드포인트를 묶는 라우터
router = APIRouter(prefix="/user_grid", tags=["admin"])

# 서비스 인스턴스(싱글턴처럼 재사용)
service = user_grid_service


@router.post("/list")
def get_user_grid_list(request: UserGridRequest):
    """
    POST /user_grid/list
    - Body(JSON)로 전달된 필터(부서/직책/나이/이메일 등)를 받아 회원정보 목록 조회
    - 성공: { message, count, data }
    - 실패: { message, error }
    """
    try:
        print("[user_grid] request:", request)
        data = service.get_user_list(request)
        return {
            "message": "회원정보 조회 성공",
            "count": len(data),
            "data": data,
        }
    except Exception as e:
        print(f"[user_grid] 조회 중 오류: {str(e)}")
        return {
            "message": "회원정보 조회 실패",
            "error": str(e),
        }
