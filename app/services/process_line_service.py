from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db


class ProcessLineService:

    def get_process_line(self, company_code: int):
        db: Session = next(get_db())
        try:
            sql = text("SELECT * FROM company WHERE company_code = :company_code")
            result = db.execute(sql, {"company_code": company_code}).fetchall()
            print(result)
            
            rows = [dict(row._mapping) for row in result]
            # rows = [
            #     {'company_code': 1000, 'company_name': '아진산업', 'created_at': datetime(...), 'updated_at': datetime(...)},
            #     {'company_code': 1001, 'company_name': '현대자동차', 'created_at': datetime(...), 'updated_at': datetime(...)}
            # ]
            return rows
        finally:
            db.close()
    
    def get_process_line_list(self, company_code_list: list[int]):
        db: Session = next(get_db())
        try:
            sql = text("SELECT * FROM company WHERE company_code IN :codes")
            result = db.execute(sql, {"codes": tuple(company_code_list)}).fetchall()

            rows = [dict(row._mapping) for row in result]
            return rows
        finally:
            db.close()



process_line_service = ProcessLineService()