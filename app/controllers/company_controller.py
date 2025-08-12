"""
Company 테이블 조회 라우터 - API 요청/응답 처리 모듈

이 모듈은 Company 테이블과 관련된 모든 HTTP API 엔드포인트를 정의합니다.
FastAPI의 APIRouter를 사용하여 라우팅을 관리하고, 서비스 계층을 호출하여
실제 비즈니스 로직을 처리합니다.

주요 기능:
- GET /company/list: company 테이블의 모든 데이터 조회
- 서비스 계층 호출 및 결과 처리
- Company 모델 객체를 딕셔너리로 변환하여 응답
- API 응답 형식 정의 및 에러 처리
"""

# 필요한 라이브러리들을 가져옵니다
from fastapi import APIRouter  # FastAPI 라우터 생성용
from app.services.company_service import company_service  # Company 서비스 인스턴스

# ============================================================================
# API 라우터 생성 및 설정
# ============================================================================
# APIRouter 인스턴스를 생성합니다
# prefix="/company": 모든 엔드포인트의 기본 경로를 /company로 설정
# tags=["company"]: Swagger UI에서 company 그룹으로 분류
router = APIRouter(prefix="/company", tags=["company"])

# ============================================================================
# Company 데이터 조회 엔드포인트
# ============================================================================
@router.get("/list")  # GET /company/list 엔드포인트 정의
def get_company_list():
    """
    company 테이블의 모든 데이터를 조회하는 API 엔드포인트
    파라미터 따로 없음
    
    
    Returns:
        dict: API 응답을 담은 딕셔너리
            - message: 조회 성공/실패 메시지
            - count: 조회된 데이터 개수
            - data: 조회된 company 데이터 리스트 (딕셔너리 형태)
            - error: 오류 발생 시 오류 메시지 (실패한 경우만)
            
    Raises:
        Exception: 서비스 계층에서 발생한 모든 예외를 잡아서 처리
    """
    try:
        # ================================================================
        # 서비스 계층 호출
        # ================================================================
        # company_service.get_all_companies()를 호출하여
        # 데이터베이스에서 company 테이블의 모든 데이터를 조회합니다
        # 이 호출은 서비스 계층에서 ORM을 사용하여 Company 모델 객체 리스트를 반환합니다
        companies = company_service.get_all_companies()
        
        # ================================================================
        # Company 모델 객체를 딕셔너리로 변환
        # ================================================================
        # Company 모델 객체의 to_dict() 메서드를 사용하여 딕셔너리로 변환합니다
        # 이는 API 응답에서 JSON 직렬화가 가능하도록 하기 위함입니다
        # company_dicts = []
        # for company in companies:
        #     company_dicts.append(company.to_dict())

        # 성공 응답 반환
        # ================================================================
        # API 호출이 성공했을 때 반환할 응답을 구성합니다
        return {
            "message": "Company 테이블 조회 성공",  # 성공 메시지
            "count": len(companies),              # 조회된 데이터 개수
            "data": companies                 # 딕셔너리로 변환된 데이터
        }
        
    except Exception as e:
        # ================================================================
        # 예외 처리 및 오류 응답
        # ================================================================
        # 서비스 계층에서 발생한 모든 예외를 잡아서 처리합니다
        # 오류 정보를 콘솔에 출력합니다 (디버깅용)
        print(f"Company 테이블 조회 중 오류 발생: {str(e)}")
        
        # 오류가 발생했을 때 반환할 응답을 구성합니다
        return {
            "message": "Company 테이블 조회 실패",  # 실패 메시지
            "error": str(e)                       # 오류 상세 내용
        }
