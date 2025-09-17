from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.defect_modal import DefectModalReq
from app.services.defect_modal_service import (
    list_defects, option_values, list_all_options
)

router = APIRouter(prefix="/defect_modal", tags=["defect"])

@router.post("/list")
def list_defects_api(req: DefectModalReq, db: Session = Depends(get_db)):
    try:
        return {"message": "불량 내역 조회 성공", "data": list_defects(db, req)}
    except Exception as e:
        raise HTTPException(500, str(e))

# ---- 옵션(필터 값) ----
@router.post("/options/all")
def options_all(req: DefectModalReq, db: Session = Depends(get_db)):
    try:
        return {"message": "불량 옵션 전체 조회 성공", "data": list_all_options(db, req)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/options/factories")
def options_factories(req: DefectModalReq, db: Session = Depends(get_db)):
    return {"message": "공장 옵션", "data": option_values(db, req, "factory")}

@router.post("/options/processes")
def options_processes(req: DefectModalReq, db: Session = Depends(get_db)):
    return {"message": "공정 옵션", "data": option_values(db, req, "process")}

@router.post("/options/equipments")
def options_equipments(req: DefectModalReq, db: Session = Depends(get_db)):
    return {"message": "설비 옵션", "data": option_values(db, req, "equipment")}

@router.post("/options/partNos")
def options_partnos(req: DefectModalReq, db: Session = Depends(get_db)):
    return {"message": "품번 옵션", "data": option_values(db, req, "partNo")}

@router.post("/options/items")
def options_items(req: DefectModalReq, db: Session = Depends(get_db)):
    return {"message": "품명 옵션", "data": option_values(db, req, "item")}

@router.post("/options/defect_types")
def options_defect_types(req: DefectModalReq, db: Session = Depends(get_db)):
    return {"message": "불량유형 옵션", "data": option_values(db, req, "defectType")}

@router.post("/options/work_types")
def options_work_types(req: DefectModalReq, db: Session = Depends(get_db)):
    return {"message": "작업구분 옵션", "data": option_values(db, req, "workType")}

@router.post("/options/insp_types")
def options_insp_types(req: DefectModalReq, db: Session = Depends(get_db)):
    return {"message": "검사구분 옵션", "data": option_values(db, req, "inspType")}
