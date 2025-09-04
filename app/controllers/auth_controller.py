# app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
import os, jwt
from app.config.database import SessionLocal
from app.models.member import Member

# ▷ 비밀번호가 해시가 아니고 평문이라면 True (나중에 꼭 해시로 전환 권장)
USE_PLAIN_PASSWORDS = True

JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_ALG = "HS256"

router = APIRouter(prefix="/auth", tags=["auth"])

# ── DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── JWT 발급
def sign_token(payload: dict) -> str:
    import time
    payload = {**payload, "iat": int(time.time()), "exp": int(time.time()) + 60*60*24*7}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

@router.post("/login")
def login(body: dict, db: Session = Depends(get_db)):
    """
    body: { "email": "아이디 또는 메일", "password": "PW" }
    프론트는 email/password로 보냅니다. email은 ID/메일 둘 다 허용.
    """
    email_or_id = (body.get("email") or "").strip()
    password = body.get("password") or ""

    if not email_or_id or not password:
        raise HTTPException(status_code=400, detail="아이디와 비밀번호를 입력하세요.")

    # ID 또는 메일로 조회
    user: Optional[Member] = (
        db.query(Member)
          .filter((Member.ID == email_or_id) | (Member.메일 == email_or_id))
          .first()
    )

    # 계정없음/비번불일치 동일 메시지
    if not user or (USE_PLAIN_PASSWORDS and user.PW != password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    if not USE_PLAIN_PASSWORDS:
        from passlib.context import CryptContext
        pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
        if not pwd_ctx.verify(password, user.PW):
            raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    token = sign_token({
        "sub": user.ID,
        "email": user.메일 or "",
        "name": user.이름,
        # "role": user.부서 or "user",
         # ⬇️ 수정: 기존 user.부서 → user.권한 or user.직급
        # "role": user.직급 or "직원",
    })

    return {
        "token": token,
        "user": {"id": user.ID,
                 "email": user.메일,
                 "name": user.이름,
                 "role": user.부서
                #   ⬇️ 수정: 기존 user.부서 → user.권한 or user.직급
                # "role": user.직급
                 }
    }

@router.get("/me")
def me(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="No token")

    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    # ✅ SQLAlchemy 안전한 get 사용 (1.4+/2.0)
    try:
        user = db.get(Member, user_id)  # type: ignore[attr-defined]
    except Exception:
        # 일부 구버전에선 Session.get이 없을 수 있어 fallback
        user = db.query(Member).get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": user.ID, 
            "email": user.메일, 
            "name": user.이름, 
            "role": user.부서
              # ⬇️ 수정: 기존 user.부서 → user.권한 or user.직급
            # "role": user.직급
            }
