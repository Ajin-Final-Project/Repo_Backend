from fastapi import APIRouter
from typing import List,Optional
from app.services.production_chart_service import production_chart_service
from app.models.productionGrid import ProductionGridResquest, UPHProductionRequest 


router = APIRouter(prefix="/production_chart", tags=["production"])
service = production_chart_service


@router.post("/pie")
def get_production_pie_chart(request: ProductionGridResquest):
    try:
        data = service.get_production_pie_chart(request)
        
        return {
            "message": "production 테이블 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"Production 테이블 조회 중 오류 발생: {str(e)}")
        return {
            "message": "production 테이블 조회 실패",
            "error": str(e)
        }

@router.post("/bar")
def get_production_bar_chart(request: ProductionGridResquest):
    try:

        print(request)
        data = service.get_production_bar_chart(request)
      

        return {
            "message": "production 테이블 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"Production 테이블 조회 중 오류 발생: {str(e)}")
        return {
            "message": "production 테이블 조회 실패",
            "error": str(e)
        }

@router.get("/item_list")
def get_item_list():
    try:
        data = service.get_itemList()
        
        return {
            "message": "production item list 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"Production item list 조회 중 오류 발생: {str(e)}")
        return {
            "message": "production 테이블 조회 실패",
            "error": str(e)
        }


@router.post("/live-chart")
def get_live_chart(request: ProductionGridResquest):
    try:
        data = service.get_live_chart(request)
        return {
            "message": "productionGrid live list 조회 성공",
            "count" : len(data),
            "data": data
        }
    except Exception as e:
         print(f"Production item list 조회 중 오류 발생: {str(e)}")
         return{
            "message": "production live 조회 실패",
            "error": str(e)
         }

@router.post("/uph-production")
def get_uph_production_data(request: UPHProductionRequest):
    try:
   
        data = service.get_uph_production_data(request)
        return {
            "message": "UPH 생산 데이터 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"UPH 생산 데이터 조회 중 오류 발생: {str(e)}")
        return {
            "message": "UPH 생산 데이터 조회 실패",
            "error": str(e)
        }





