# from fastapi import APIRouter
# from app.models.inspection_modal import InspectionModalReq
# from app.services.inspection_modal_service import inspection_modal_service

# # 하위호환: 프론트에서 호출하는 경로
# router = APIRouter(prefix="/modal", tags=["compat"])

# @router.post("/item_list")
# def list_items(req: InspectionModalReq):
#     try:
#         data = inspection_modal_service.list_items(req)
#         return {"message": "품번/품명 목록 조회 성공", "count": len(data), "data": data}
#     except Exception as e:
#         return {"message": "품번/품명 목록 조회 실패", "error": str(e), "data": []}
