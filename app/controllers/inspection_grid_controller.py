from fastapi import APIRouter
from typing import List
from app.services.inspection_grid_service import inspection_grid_service
from app.models.inspectionGrid import inspectionGridRequest

router = APIRouter(prefix="/inspection_grid", tags=["inspection"])
service = inspection_grid_service


@router.post("/list")
def get_inspection_list(request: inspectionGridRequest):
    """
    검사 내역 목록 조회
    """
    try:
        data = service.get_inspection_list(request)
        return {
            "message": "검사내역 테이블 조회 성공",
            "count": len(data),
            "data": data,
        }
    except Exception as e:
        print(f"검사내역 테이블 조회 중 오류 발생: {str(e)}")
        return {
            "message": "검사내역 테이블 조회 실패",
            "error": str(e),
            "data": [],
        }


# ------------------------ 옵션 APIs (드롭다운) ------------------------

@router.post("/options/plants")
def get_plants_options(request: inspectionGridRequest):
    """ 공장 드롭다운 옵션 """
    try:
        items: List[str] = service.get_distinct_plants(request)
        return {"message": "공장 옵션 조회 성공", "count": len(items), "data": items}
    except Exception as e:
        print(f"공장 옵션 조회 오류: {str(e)}")
        return {"message": "공장 옵션 조회 실패", "error": str(e), "data": []}


@router.post("/options/processes")
def get_processes_options(request: inspectionGridRequest):
    """ 공정 드롭다운 옵션 """
    try:
        items: List[str] = service.get_distinct_processes(request)
        return {"message": "공정 옵션 조회 성공", "count": len(items), "data": items}
    except Exception as e:
        print(f"공정 옵션 조회 오류: {str(e)}")
        return {"message": "공정 옵션 조회 실패", "error": str(e), "data": []}


@router.post("/options/equipments")
def get_equipments_options(request: inspectionGridRequest):
    """ 설비 드롭다운 옵션 """
    try:
        items: List[str] = service.get_distinct_equipments(request)
        return {"message": "설비 옵션 조회 성공", "count": len(items), "data": items}
    except Exception as e:
        print(f"설비 옵션 조회 오류: {str(e)}")
        return {"message": "설비 옵션 조회 실패", "error": str(e), "data": []}


@router.post("/options/partNos")
def get_partnos_options(request: inspectionGridRequest):
    """ 품번 드롭다운 옵션 """
    try:
        items: List[str] = service.get_distinct_part_nos(request)
        return {"message": "품번 옵션 조회 성공", "count": len(items), "data": items}
    except Exception as e:
        print(f"품번 옵션 조회 오류: {str(e)}")
        return {"message": "품번 옵션 조회 실패", "error": str(e), "data": []}


@router.post("/options/partNames")
def get_partnames_options(request: inspectionGridRequest):
    """
    품명 드롭다운 옵션 (현재 프론트는 '자리만 확보' — 전송/검색 미사용)
    """
    try:
        items: List[str] = service.get_distinct_part_names(request)
        return {"message": "품명 옵션 조회 성공", "count": len(items), "data": items}
    except Exception as e:
        print(f"품명 옵션 조회 오류: {str(e)}")
        return {"message": "품명 옵션 조회 실패", "error": str(e), "data": []}
