# from __future__ import annotations
# from typing import Dict, List
# from sqlalchemy import text
# from sqlalchemy.orm import Session

# from app.config.database import get_db
# from app.models.inspection_item_modal import InspectionItemModalReq


# class InspectionItemModalService:
#     """
#     검사 품목(자재번호/자재명) 모달 조회
#     - 생산_검사(i)만 사용
#     - 필터: i.plant / i.process / i.equipment / i.work_date
#     """
#     T_INSP = "`AJIN_newDB`.`생산_검사`"

#     def list_items(self, req: InspectionItemModalReq) -> List[Dict]:
#         db: Session = next(get_db())
#         try:
#             p: Dict = {}
#             where_i = ["1=1"]

#             # 기간 (i.work_date)
#             sd = (getattr(req, "startDate", None) or "").strip() or None
#             ed = (getattr(req, "endDate", None) or "").strip() or None
#             if sd and ed:
#                 p["sd"] = sd
#                 p["ed"] = ed
#                 where_i.append("DATE(i.`work_date`) BETWEEN :sd AND :ed")

#             # 검색어
#             q = (getattr(req, "q", None) or "").strip()
#             if q:
#                 p["q"] = f"%{q}%"
#                 where_i.append("(i.`자재번호` LIKE :q OR i.`자재명` LIKE :q)")

#             # 공장/공정/설비 (요청 파라미터명을 테이블 컬럼으로 매핑)
#             plant = (getattr(req, "plant", None) or "").strip()
#             worker = (getattr(req, "worker", None) or "").strip()      # -> process
#             line   = (getattr(req, "line", None)   or "").strip()      # -> equipment

#             # 수정 (부분일치)
#             if plant:
#                 p["plant"] = f"%{plant}%"
#                 where_i.append("i.`plant` LIKE :plant")
#             if worker:
#                 p["process"] = f"%{worker}%"
#                 where_i.append("i.`process` LIKE :process")
#             if line:
#                 p["equipment"] = f"%{line}%"
#                 where_i.append("i.`equipment` LIKE :equipment")

#             w_insp = " AND ".join(where_i)

#             # LIMIT: 검색어 있으면 500, 없으면 300
#             limit = 500 if q else 300

#             sql = f"""
#                 SELECT DISTINCT
#                     CAST(i.`자재번호` AS CHAR CHARACTER SET utf8mb4) AS `품목번호`,
#                     COALESCE(i.`자재명`, '') AS `품목명`
#                 FROM {self.T_INSP} i
#                 WHERE {w_insp}
#                   AND i.`자재번호` IS NOT NULL AND i.`자재번호` <> ''
#                 ORDER BY `품목번호` ASC
#                 LIMIT {limit}
#             """

#             rows = db.execute(text(sql), p).mappings().all()
#             return [{"품목번호": r["품목번호"], "품목명": r["품목명"]} for r in rows]
#         finally:
#             db.close()


# inspection_item_modal_service = InspectionItemModalService()


from __future__ import annotations
from typing import Dict, List
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.inspection_item_modal import InspectionItemModalReq


class InspectionItemModalService:
    """
    검사 품목(자재번호/자재명) 모달 조회
    - 생산_검사(i)만 사용
    - 필터: i.plant / i.process / i.equipment / i.work_date
    """
    T_INSP = "`AJIN_newDB`.`생산_검사`"

    def list_items(self, req: InspectionItemModalReq) -> List[Dict]:
        db: Session = next(get_db())
        try:
            p: Dict = {}
            where_i = ["1=1"]

            # 기간 (i.work_date)
            sd = (getattr(req, "startDate", None) or "").strip() or None
            ed = (getattr(req, "endDate", None) or "").strip() or None
            if sd and ed:
                p["sd"] = sd
                p["ed"] = ed
                where_i.append("DATE(i.`work_date`) BETWEEN :sd AND :ed")

            # 검색어
            q = (getattr(req, "q", None) or "").strip()
            if q:
                p["q"] = f"%{q}%"
                where_i.append("(i.`자재번호` LIKE :q OR i.`자재명` LIKE :q)")

            # 공장/공정/설비 (요청 파라미터명을 테이블 컬럼으로 매핑)
            plant = (getattr(req, "plant", None) or "").strip()
            worker = (getattr(req, "worker", None) or "").strip()      # -> process
            line   = (getattr(req, "line", None)   or "").strip()      # -> equipment

            # 공백/부분일치 허용 (REPLACE로 공백 무시)
            if plant:
                p["plant"] = f"%{plant.replace(' ', '')}%"
                where_i.append("REPLACE(i.`plant`,' ','') LIKE :plant")
            if worker:
                p["process"] = f"%{worker.replace(' ', '')}%"
                where_i.append("REPLACE(i.`process`,' ','') LIKE :process")
            if line:
                p["equipment"] = f"%{line.replace(' ', '')}%"
                where_i.append("REPLACE(i.`equipment`,' ','') LIKE :equipment")

            w_insp = " AND ".join(where_i)

            # LIMIT: 검색어 있으면 500, 없으면 300
            limit = 500 if q else 300

            sql = f"""
                SELECT DISTINCT
                    CAST(i.`자재번호` AS CHAR CHARACTER SET utf8mb4) AS `품목번호`,
                    COALESCE(i.`자재명`, '') AS `품목명`
                FROM {self.T_INSP} i
                WHERE {w_insp}
                  AND i.`자재번호` IS NOT NULL AND i.`자재번호` <> ''
                ORDER BY `품목번호` ASC
                LIMIT {limit}
            """

            rows = db.execute(text(sql), p).mappings().all()
            return [{"품목번호": r["품목번호"], "품목명": r["품목명"]} for r in rows]
        finally:
            db.close()


inspection_item_modal_service = InspectionItemModalService()
