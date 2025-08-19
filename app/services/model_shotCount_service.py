from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.moldShotCount import moldShotCount

class Mold_shotCount_service:

    def get_moldShotCount_list(self, req: moldShotCount):
        db: Session = next(get_db())
        try:
                where = []
                params = {}

                def has_value(v):
                    if v is None: return False
                    if isinstance(v, str):
                        s = v.strip()
                        return s != "" and s.lower() != "string"
                    return True

                # === 정확 일치 ===
                if req.plant is not None:
                    where.append("`플랜트` = :plant")
                    params["plant"] = req.plant

                if has_value(req.equipment_type):
                    where.append("`설비유형` = :equipment_type")
                    params["equipment_type"] = req.equipment_type.strip()

                if req.mold_no is not None:
                    where.append("`금형번호` = :mold_no")
                    params["mold_no"] = req.mold_no

                if req.measuring_point is not None:
                    where.append("`측정지점` = :measuring_point")
                    params["measuring_point"] = req.measuring_point

                if req.inspection_hit_count is not None:
                    where.append("`점검타발수` = :inspection_hit_count")
                    params["inspection_hit_count"] = req.inspection_hit_count

                if req.maintenance_cycle is not None:
                    where.append("`유지보수주기` = :maintenance_cycle")
                    params["maintenance_cycle"] = req.maintenance_cycle

                if has_value(req.maintenance_cycle_unit):
                    where.append("`유지보수주기단위` = :maintenance_cycle_unit")
                    params["maintenance_cycle_unit"] = req.maintenance_cycle_unit.strip()

                if has_value(req.functional_location):
                    where.append("`기능위치` = :functional_location")
                    params["functional_location"] = req.functional_location.strip()

                if has_value(req.planner_group):
                    where.append("`계획자그룹` = :planner_group")
                    params["planner_group"] = req.planner_group.strip()

                # === 부분 일치 ===
                if has_value(req.mold_name):
                    where.append("`금형내역` LIKE :mold_name")
                    params["mold_name"] = f"%{req.mold_name.strip()}%"

                if has_value(req.measuring_position):
                    where.append("`측정위치` LIKE :measuring_position")
                    params["measuring_position"] = f"%{req.measuring_position.strip()}%"

                if has_value(req.functional_location_desc):
                    where.append("`기능위치 내역` LIKE :functional_location_desc")
                    params["functional_location_desc"] = f"%{req.functional_location_desc.strip()}%"

                if has_value(req.maintenance_plan):
                    where.append("`유지보수계획` LIKE :maintenance_plan")
                    params["maintenance_plan"] = f"%{req.maintenance_plan.strip()}%"

                # === 수치 범위 ===
                if req.cum_shot_min is not None:
                    where.append("`누적 Shot 수` >= :cum_shot_min")
                    params["cum_shot_min"] = req.cum_shot_min
                if req.cum_shot_max is not None:
                    where.append("`누적 Shot 수` <= :cum_shot_max")
                    params["cum_shot_max"] = req.cum_shot_max

                if req.progress_min is not None:
                    where.append("`진행률(%)` >= :progress_min")
                    params["progress_min"] = req.progress_min
                if req.progress_max is not None:
                    where.append("`진행률(%)` <= :progress_max")
                    params["progress_max"] = req.progress_max

                # === 날짜 범위(생산실적처리 최종일) ===
                if has_value(req.startDate) and has_value(req.endDate):
                    where.append("`생산실적처리 최종일` BETWEEN :startDate AND :endDate")
                    params["startDate"] = req.startDate
                    params["endDate"] = req.endDate
                elif has_value(req.startDate):
                    where.append("`생산실적처리 최종일` >= :startDate")
                    params["startDate"] = req.startDate
                elif has_value(req.endDate):
                    where.append("`생산실적처리 최종일` <= :endDate")
                    params["endDate"] = req.endDate

                # === 개별 품번(정확 일치, 제공한 것만 AND) ===
                if has_value(req.part_no1):
                    where.append("`타발처리 품번1` = :part_no1")
                    params["part_no1"] = req.part_no1.strip()
                if has_value(req.part_no2):
                    where.append("`타발처리 품번2` = :part_no2")
                    params["part_no2"] = req.part_no2.strip()
                if has_value(req.part_no3):
                    where.append("`타발처리 품번3` = :part_no3")
                    params["part_no3"] = req.part_no3.strip()
                if has_value(req.part_no4):
                    where.append("`타발처리 품번4` = :part_no4")
                    params["part_no4"] = req.part_no4.strip()
                if has_value(req.part_no5):
                    where.append("`타발처리 품번5` = :part_no5")
                    params["part_no5"] = req.part_no5.strip()

                if not where:
                    where.append("1=1")

                sql = f"""
                    SELECT *
                    FROM `AJIN_newDB`.`금형타발수관리`
                    WHERE {' AND '.join(where)}
                """

                print("SQL:", sql)
                print("Params:", params)

                rows = db.execute(text(sql), params).mappings().all()
                return [dict(r) for r in rows]
        finally:
            db.close()

mold_shotCount_service = Mold_shotCount_service()
