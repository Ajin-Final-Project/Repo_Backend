# models/userGrid.py
"""
[회원정보 그리드 요청 모델]
- 프런트에서 넘어오는 검색/필터 파라미터 정의 (모두 Optional)
- 실제 컬럼명과 매핑은 서비스의 SQL에서 alias로 처리
- 테이블: AJIN_newDB.회원정보
"""

from typing import Optional
from pydantic import BaseModel


class UserGridRequest(BaseModel):
    user_id: Optional[str] = None          # ID (정확 일치)
    name: Optional[str] = None             # 이름 (부분 검색)
    # age_min: Optional[int] = None          # 나이 최소
    # age_max: Optional[int] = None          # 나이 최대
    age: Optional[int] = None       # ✅ 단일 나이(정확 일치) ← (변경)
    dept: Optional[str] = None             # 부서 (정확 일치)
    position: Optional[str] = None         # 직책 (정확 일치)
    email: Optional[str] = None            # 메일 (부분 검색)
    phone: Optional[str] = None            # 전화번호 (부분 검색)
    address: Optional[str] = None          # 주소 (부분 검색)
    pw: Optional[str] = None        # ✅ PW (정확 일치/부분 검색 모두 가능하게 서비스에서 처리)
                                    # 보안상 PW는 조회/필터에서 제외(원하면 별도 권한 구간에서 처리)
