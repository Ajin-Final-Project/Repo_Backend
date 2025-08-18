"""
member(회원정보) 테이블을 위한 SQLAlchemy ORM 모델

이 모듈은 member 테이블의 구조를 정의하는 SQLAlchemy 모델 클래스를 포함합니다.
데이터베이스 테이블과 Python 객체 간의 매핑을 제공합니다.
"""

# app/models/member.py
from sqlalchemy import Column, String, Integer
from app.config.database import Base

class Member(Base):
    __tablename__ = "회원정보"  # ← 실제 테이블명

    # 실제 컬럼명과 타입을 그대로 매핑
    ID = Column(String(30), primary_key=True)   # PK
    PW = Column(String(45), nullable=False)
    이름 = Column(String(20), nullable=False)
    나이 = Column(Integer)
    부서 = Column(String(45))
    메일 = Column(String(45))
    주소 = Column(String(45))
    전화번호 = Column(Integer)
