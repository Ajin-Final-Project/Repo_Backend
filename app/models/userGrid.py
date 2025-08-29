# models/userGrid.py
"""
[회원정보 그리드 요청 모델]
- 프런트에서 넘어오는 검색/필터 파라미터 정의 (모두 Optional)
- 테이블: AJIN_newDB.회원정보
- 새 테이블 반영: 본부/직급/권한 추가
"""

from typing import Optional
from pydantic import BaseModel


class UserGridRequest(BaseModel):
    user_id: Optional[str] = None          # ID (정확 일치)
    name: Optional[str] = None             # 이름 (부분 검색)
    age_min: Optional[int] = None          # 나이 최소
    age_max: Optional[int] = None          # 나이 최대
    age: Optional[int] = None              # 단일 나이(정확 일치) ← (변경)
    dept: Optional[str] = None             # 부서 (정확 일치)
    position: Optional[str] = None         # 직책 (정확 일치), (호환) 기존 position 입력 → 서비스에서 rank로 병합
    email: Optional[str] = None            # 메일 (부분 검색)
    phone: Optional[str] = None            # 전화번호 (부분 검색)
    address: Optional[str] = None          # 주소 (부분 검색)
    # pw: Optional[str] = None             # PW (정확 일치/부분 검색 모두 가능하게 서비스에서 처리)
                                           # 보안: PW 필드 제거, 보안상 PW는 조회/필터에서 제외(원하면 별도 권한 구간에서 처리)
    # 새 테이블 컬럼 반영
    hq: Optional[str] = None               # 본부 (부분 검색)   ← (원본에는 없음)
    dept: Optional[str] = None             # 부서 (부분 검색)
    rank: Optional[str] = None             # 직급 (부분/정확은 서비스에서 처리)
    role: Optional[str] = None             # 권한 (ENUM: 시스템관리자/임원/관리자/직원/열람전용)
