"""
Company 테이블을 위한 SQLAlchemy ORM 모델

이 모듈은 company 테이블의 구조를 정의하는 SQLAlchemy 모델 클래스를 포함합니다.
데이터베이스 테이블과 Python 객체 간의 매핑을 제공합니다.
"""

# SQLAlchemy에서 필요한 기능들을 가져옵니다
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Base 클래스를 가져옵니다 (데이터베이스 테이블 생성을 위한 기본 클래스)
from app.config.database import Base

# ============================================================================
# Company 모델 클래스 정의
# ============================================================================
class Company(Base):
    """
    Company 테이블을 나타내는 SQLAlchemy 모델 클래스
    
    이 클래스는 company 테이블의 구조를 정의하고,
    데이터베이스와의 상호작용을 위한 메서드들을 제공합니다.
    
    테이블 구조:
    - id: 회사 고유 식별자 (기본키)
    - name: 회사명
    - address: 회사 주소
    - phone: 회사 전화번호
    - email: 회사 이메일
    - description: 회사 설명
    - created_at: 생성일시
    - updated_at: 수정일시
    """
    
    # ========================================================================
    # 테이블 메타데이터 설정
    # ========================================================================
    # __tablename__: 데이터베이스에서 사용할 테이블 이름
    __tablename__ = "company"
    
    # ========================================================================
    # 테이블 컬럼 정의
    # ========================================================================
    # id 컬럼: 회사 고유 식별자 (기본키)
    # Integer: 정수형 데이터 타입
    # primary_key=True: 기본키로 설정
    # autoincrement=True: 자동 증가 설정
    company_code = Column(Integer, primary_key=True, autoincrement=True, comment="회사 고유 식별자")
    
    # name 컬럼: 회사명
    # String(100): 최대 100자 문자열
    # nullable=False: NULL 값 허용하지 않음
    # unique=True: 중복 값 허용하지 않음
    company_name = Column(String(100), nullable=False, unique=True, comment="회사명")
    
    # created_at 컬럼: 생성일시
    # DateTime: 날짜와 시간 데이터 타입
    # default=datetime.utcnow: 기본값으로 현재 UTC 시간 설정
    # nullable=False: NULL 값 허용하지 않음
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="생성일시")
    
    # updated_at 컬럼: 수정일시
    # DateTime: 날짜와 시간 데이터 타입
    # default=datetime.utcnow: 기본값으로 현재 UTC 시간 설정
    # onupdate=datetime.utcnow: 업데이트 시 자동으로 현재 시간 설정
    # nullable=False: NULL 값 허용하지 않음
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="수정일시")
    
    # ========================================================================
    # 문자열 표현 메서드
    # ========================================================================
    def __repr__(self):
        """
        Company 객체의 문자열 표현을 반환합니다
        
        Returns:
            str: Company 객체를 나타내는 문자열
        """
        return f"<Company(id={self.company_name}, name='{self.company_code}')>"
    
    # ========================================================================
    # 딕셔너리 변환 메서드
    # ========================================================================
    def to_dict(self):
        """
        Company 객체를 딕셔너리로 변환합니다
        
        Returns:
            dict: Company 객체의 데이터를 담은 딕셔너리
        """
        return {
            "id": self.company_code,
            "name": self.company_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
