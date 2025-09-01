from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.moldShotCount import moldShotCount

class Mold_shot_check_service:

    def get_moldShotCheck_list(self, req: moldShotCount):
        db: Session = next(get_db())
        try:
            where_conditions = []
            params = {}

            def has_value(v):
                if v is None: return False
                if isinstance(v, str):
                    s = v.strip()
                    return s != "" and s.lower() != "string"
                return True

            # === 생산내역 필터링 조건 ===
            if has_value(req.plant):
                where_conditions.append("prod.플랜트 = :plant")
                params["plant"] = req.plant.strip()
            
            if has_value(req.responsible_person):
                where_conditions.append("prod.책임자 = :responsible_person")
                params["responsible_person"] = req.responsible_person.strip()
            
            if has_value(req.work_center):
                where_conditions.append("prod.작업장 = :work_center")
                params["work_center"] = req.work_center.strip()
            
            if has_value(req.material_no):
                where_conditions.append("prod.자재번호 LIKE :material_no")
                params["material_no"] = f"%{req.material_no.strip()}%"
            
            if has_value(req.material_name):
                where_conditions.append("prod.자재명 LIKE :material_name")
                params["material_name"] = f"%{req.material_name.strip()}%"

            # === 금형세척주기 검색 조건 ===
            if has_value(req.equipment_detail):
                where_conditions.append("wash.설비내역 LIKE :equipment_detail")
                params["equipment_detail"] = f"%{req.equipment_detail.strip()}%"
            
            if has_value(req.order_type):
                where_conditions.append("wash.오더유형 = :order_type")
                params["order_type"] = req.order_type.strip()
            
            if has_value(req.action_content):
                where_conditions.append("wash.조치내용 LIKE :action_content")
                params["action_content"] = f"%{req.action_content.strip()}%"
            
            if has_value(req.basic_start_date):
                where_conditions.append("wash.기본시작일 >= :basic_start_date")
                params["basic_start_date"] = req.basic_start_date.strip()
            
            if has_value(req.basic_end_date):
                where_conditions.append("wash.기본종료일 <= :basic_end_date")
                params["basic_end_date"] = req.basic_end_date.strip()

            # === 금형타발수관리 검색 조건 ===
            if has_value(req.mold_no):
                where_conditions.append("shot.금형번호 = :mold_no")
                params["mold_no"] = req.mold_no.strip()
            
            if has_value(req.measuring_point):
                where_conditions.append("shot.측정지점 = :measuring_point")
                params["measuring_point"] = req.measuring_point.strip()
            
            if has_value(req.measuring_position):
                where_conditions.append("shot.측정위치 LIKE :measuring_position")
                params["measuring_position"] = f"%{req.measuring_position.strip()}%"
            
            if req.cum_shot_min is not None:
                where_conditions.append("shot.`누적 Shot 수` >= :cum_shot_min")
                params["cum_shot_min"] = req.cum_shot_min
            
            if req.cum_shot_max is not None:
                where_conditions.append("shot.`누적 Shot 수` <= :cum_shot_max")
                params["cum_shot_max"] = req.cum_shot_max
            
            if req.inspection_hit_count is not None:
                where_conditions.append("shot.점검타발수 = :inspection_hit_count")
                params["inspection_hit_count"] = req.inspection_hit_count
            
            if req.maintenance_cycle is not None:
                where_conditions.append("shot.유지보수주기 = :maintenance_cycle")
                params["maintenance_cycle"] = req.maintenance_cycle
            
            if req.progress_min is not None:
                where_conditions.append("shot.`진행률(%)` >= :progress_min")
                params["progress_min"] = req.progress_min
            
            if req.progress_max is not None:
                where_conditions.append("shot.`진행률(%)` <= :progress_max")
                params["progress_max"] = req.progress_max

            # === 날짜 범위 검색 ===
            if has_value(req.start_date) and has_value(req.end_date):
                where_conditions.append("wash.기본시작일 BETWEEN :start_date AND :end_date")
                params["start_date"] = req.start_date.strip()
                params["end_date"] = req.end_date.strip()
            elif has_value(req.start_date):
                where_conditions.append("wash.기본시작일 >= :start_date")
                params["start_date"] = req.start_date.strip()
            elif has_value(req.end_date):
                where_conditions.append("wash.기본시작일 <= :end_date")
                params["end_date"] = req.end_date.strip()

            # WHERE 절 구성
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

            sql = f"""
                WITH prod_filt AS (
                    SELECT DISTINCT
                           플랜트, 책임자, 작업장, 자재번호, 자재명
                    FROM AJIN_newDB.생산내역
                    WHERE 플랜트 = '아진산업-경산(본사)'
                      AND 책임자 = '프레스'
                      AND 작업장 = '1500T'
                      AND 자재번호 IS NOT NULL AND TRIM(자재번호) <> ''
                      AND 자재명   IS NOT NULL AND TRIM(자재명)   <> ''
                )
                SELECT 
                    prod.플랜트,
                    prod.책임자,
                    prod.자재번호,
                    prod.자재명,
                    wash.설비내역,
                    wash.오더유형,
                    wash.조치내용,
                    wash.기본시작일,
                    wash.기본종료일,
                    shot.플랜트 AS shot_플랜트,
                    shot.금형번호,
                    shot.측정지점,
                    shot.측정위치,
                    shot.`누적 Shot 수` AS 누적_Shot_수,
                    shot.점검타발수 * 0.8 AS 점검타발수_80,
                    shot.점검타발수 * 0.9 AS 점검타발수_90,
                    shot.점검타발수,
                    shot.유지보수주기,
                    shot.`진행률(%)` AS 진행율_pct
                FROM AJIN_newDB.금형세척주기 AS wash
                JOIN AJIN_newDB.금형타발수관리 AS shot
                  ON wash.설비내역 = shot.금형내역
                JOIN prod_filt AS prod
                  ON wash.설비내역 LIKE CONCAT('%', prod.자재번호, '%')
                WHERE {where_clause}
            """

            print("SQL:", sql)
            print("Params:", params)

            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

mold_shot_check_service = Mold_shot_check_service()
