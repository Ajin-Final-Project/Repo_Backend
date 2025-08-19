# # services/user_grid_service.py
# """
# [회원정보 그리드 서비스]
# - 동적 WHERE 절 생성(값이 있는 필드만 조건으로 추가)
# - SQLAlchemy text + 바인딩 파라미터로 안전하게 실행
# - 조회 테이블: AJIN_newDB.회원정보
# - 노출 컬럼: ID, 이름, 나이, 부서, 직책, 메일, 주소, 전화번호
#   (PW는 보안상 제외)
# """

# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from app.config.database import get_db
# from app.models.userGrid import UserGridRequest


# class UserGridService:
#     @staticmethod
#     def _has_value(value):
#         """
#         프런트 기본값/공백/String 등을 필터링하여
#         실제 유효한 값만 True를 반환
#         """
#         if value is None:
#             return False
#         if isinstance(value, str):
#             s = value.strip().lower()
#             return s != "" and s != "string"
#         if isinstance(value, int):
#             return value != 0  # 0 들어오면 필터로 안봄(스웨거 기본값 안전장치)
#         return True

#     def get_user_list(self, req: UserGridRequest):
#         """
#         회원정보 목록 조회
#         - req의 값이 있는 필드만 WHERE 조건으로 추가
#         - 결과: list[dict]
#         """
#         db: Session = next(get_db())
#         try:
#             where = []
#             params = {}
#             hv = self._has_value

#             # ID (정확 일치)
#             if hv(req.user_id):
#                 where.append("`ID` = :user_id")
#                 params["user_id"] = req.user_id

#             # PW (부분/정확 검색 허용: 기본은 부분)
#             if hv(req.pw):
#                 where.append("`PW` LIKE :pw")  # ✅ 변경: 부분검색
#                 params["pw"] = f"%{req.pw.strip()}%"

#             # 이름 (부분 검색)
#             if hv(req.name):
#                 where.append("`이름` LIKE :name")
#                 params["name"] = f"%{req.name.strip()}%"

#             # # 나이 범위
#             # if hv(req.age_min):
#             #     where.append("`나이` >= :age_min")
#             #     params["age_min"] = req.age_min

#             # if hv(req.age_max):
#             #     where.append("`나이` <= :age_max")
#             #     params["age_max"] = req.age_max

#             # 나이 (정확 일치)
#             if hv(req.age):
#                 where.append("`나이` = :age")  # ✅ 변경: 범위 대신 단일값
#                 params["age"] = req.age          

#             # # 부서/직책 (정확 일치)
#             # if hv(req.dept):
#             #     where.append("`부서` = :dept")
#             #     params["dept"] = req.dept

#             # if hv(req.position):
#             #     where.append("`직책` = :position")
#             #     params["position"] = req.position

#             # 부서 (부분 검색으로 완화)
#             if hv(req.dept):
#                 where.append("`부서` LIKE :dept")
#                 params["dept"] = f"%{req.dept.strip()}%"

#             # 이메일/전화/주소 (부분 검색)
#             if hv(req.email):
#                 where.append("`메일` LIKE :email")
#                 params["email"] = f"%{req.email.strip()}%"

#             if hv(req.phone):
#                 where.append("`전화번호` LIKE :phone")
#                 params["phone"] = f"%{req.phone.strip()}%"

#             if hv(req.address):
#                 where.append("`주소` LIKE :address")
#                 params["address"] = f"%{req.address.strip()}%"

#             # WHERE 조건이 없으면 전체 조회
#             if not where:
#                 where.append("1=1")

#             # 필요한 컬럼만 명시적으로 선택(프런트 그리드 컬럼에 맞춰 alias 제공)
#             sql = f"""
#                 SELECT
#                     `ID`       AS user_id,
#                     `PW`       AS pw,        -- ✅ 추가                    
#                     `이름`      AS name,
#                     `나이`      AS age,
#                     `부서`      AS dept,
#                     `메일`      AS email,
#                     `주소`      AS address,
#                     `전화번호`   AS phone
#                 FROM `AJIN_newDB`.`회원정보`
#                 WHERE {' AND '.join(where)}
#                 ORDER BY `이름` ASC, `ID` ASC
#             """

#             print("[user_grid] SQL:", sql)
#             print("[user_grid] params:", params)

#             rows = db.execute(text(sql), params).mappings().all()
#             return [dict(r) for r in rows]

#         finally:
#             db.close()


# # 외부에서 import 하여 쓰는 싱글턴 스타일 인스턴스
# user_grid_service = UserGridService()


# services/user_grid_service.py
"""
[회원정보 그리드 서비스 - alias 제거 버전]
- 응답 JSON의 키를 DB 원본 한글 컬럼명 그대로 사용합니다.
  예) {"ID": "...", "PW": "...", "이름": "...", "나이": 29, "부서": "...", "메일": "...", "주소": "...", "전화번호": "..."}
- 동적 WHERE 절(값 있는 것만 조건 추가) + 바인딩 파라미터로 안전하게 실행
- 조회 테이블: AJIN_newDB.회원정보

⚠ 보안 주의:
- 현재 PW를 평문 그대로 내려줍니다. 운영/배포 환경에서는 반드시 마스킹 또는 해시 저장을 적용하세요.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.userGrid import UserGridRequest


class UserGridService:
    @staticmethod
    def _has_value(value):
        """
        [유효값 판정]
        - None → False
        - 문자열: 공백/기본 'string' → False
        - 정수: 0은 Swagger 기본값으로 자주 들어오므로 필터 제외 → False
        - 그 외 → True
        """
        if value is None:
            return False
        if isinstance(value, str):
            s = value.strip().lower()
            return s != "" and s != "string"
        if isinstance(value, int):
            return value != 0
        return True

    def get_user_list(self, req: UserGridRequest):
        """
        [회원정보 목록 조회]
        - req에 값이 있는 필드만 WHERE 조건으로 반영
        - SELECT 시 alias(AS ...)를 사용하지 않음 → 응답 키가 한글 컬럼명 그대로
        - 반환: list[dict]
        """
        db: Session = next(get_db())
        try:
            where = []
            params = {}
            hv = self._has_value

            # ── 필터 구성 (값 있을 때만 WHERE에 추가)
            # ID (정확 일치)
            if hv(req.user_id):
                where.append("`ID` = :user_id")
                params["user_id"] = req.user_id

            # PW (부분 검색)  ※ 운영 시 평문 노출 지양
            if hv(req.pw):
                where.append("`PW` LIKE :pw")
                params["pw"] = f"%{req.pw.strip()}%"

            # 이름 (부분 검색)
            if hv(req.name):
                where.append("`이름` LIKE :name")
                params["name"] = f"%{req.name.strip()}%"

            # 나이 (정확 일치)  ← 범위(age_min/age_max) 대신 단일값만 사용
            if hv(req.age):
                where.append("`나이` = :age")
                params["age"] = req.age

            # 부서 (정확 일치) — 생산내역 서비스 스타일에 맞춤
            # 부분 검색 원하면 아래 두 줄을 주석 처리하고 LIKE 버전으로 교체하세요.
            if hv(req.dept):
                where.append("`부서` = :dept")
                params["dept"] = req.dept
                # where.append("`부서` LIKE :dept")
                # params["dept"] = f"%{req.dept.strip()}%"

            # 이메일/전화/주소 (부분 검색)
            if hv(req.email):
                where.append("`메일` LIKE :email")
                params["email"] = f"%{req.email.strip()}%"

            if hv(req.phone):
                where.append("`전화번호` LIKE :phone")
                params["phone"] = f"%{req.phone.strip()}%"

            if hv(req.address):
                where.append("`주소` LIKE :address")
                params["address"] = f"%{req.address.strip()}%"

            # WHERE 조건이 하나도 없으면 전체 조회
            if not where:
                where.append("1=1")

            # ── SELECT: alias 제거(원본 한글 컬럼명 그대로 응답)
            sql = f"""
                SELECT
                    `ID`,
                    `PW`,
                    `이름`,
                    `나이`,
                    `부서`,
                    `메일`,
                    `주소`,
                    `전화번호`
                FROM `AJIN_newDB`.`회원정보`
                WHERE {' AND '.join(where)}
            """
            # 생산내역 서비스 스타일에 맞춰 ORDER BY 없음.
            # 정렬이 필요하면 아래 주석을 해제하세요.
            # sql += " ORDER BY `이름` ASC, `ID` ASC"

            print("[user_grid(no-alias)] SQL:", sql)
            print("[user_grid(no-alias)] params:", params)

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        finally:
            db.close()


# 외부에서 import 하여 쓰는 싱글턴 스타일 인스턴스
user_grid_service = UserGridService()
