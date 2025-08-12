# AJIN Smart-Factory 조회 API

MariaDB에서 팩토리 정보를 SELECT문으로 조회하는 간단한 FastAPI 애플리케이션입니다.

## 프로젝트 구조

```
AJIN-SMART-FACTORY/
├── app/
│   ├── config/
│   │   └── database.py      # 데이터베이스 설정
│   │
│   ├── models/
│   │    └── model.py        # 모델
│   │
    ├── services/
│   │    └── service.py        # 서비스
│   │
│   └── controllers/
│       └── controller.py  #
├── main.py                     # FastAPI 애플리케이션 진입점
├── requirements.txt            # Python 의존성
└── README.md
```

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
(에러뜨면 python -X utf8 -m pip install -r requirements.txt 요고 실행!)
```
