from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.inspectionGrid import inspectionGridRequest
from decimal import Decimal
from typing import Dict, List, Tuple, Any


TABLE = "`AJIN_newDB`.`검사내역`"

# DB 컬럼명(한글)
COL = {
    "businessPlace": "`사업장`",
    "plant": "`공장`",
    "process": "`공정`",
    "equipment": "`설비`",
    "inspectionType": "`검사구분`",
    "itemNumber": "`품번`",
    "reportDate": "`보고일`",
    "shiftType": "`주야구분`",
    "workSequence": "`작업순번`",
    "workType": "`작업구분`",
    "inspectionSequence": "`검사순번`",
    "inspectionItemName": "`검사항목명`",
    "inspectionDetails": "`검사내용`",
    "productionValue": "`생산`",
}


class Inspection_grid_service:
    # ------------------------ 내부 공용 유틸 ------------------------

    @staticmethod
    def _has_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() not in ("", "string")
        if isinstance(value, (int, Decimal, float)):
            return True
        return True

    def _common_where(self, req: inspectionGridRequest) -> Tuple[List[str], Dict[str, Any]]:
        """
        목록/옵션 공통 WHERE 절 + 파라미터 구성
        - 기간 필터, 기본 필드들 포함
        """
        where: List[str] = []
        params: Dict[str, Any] = {}

        hv = self._has_value

        # 기간
        if hv(req.start_work_date):
            where.append(f"DATE({COL['reportDate']}) >= :start_work_date")
            params["start_work_date"] = req.start_work_date
        if hv(req.end_work_date):
            where.append(f"DATE({COL['reportDate']}) <= :end_work_date")
            params["end_work_date"] = req.end_work_date

        # 상위 필터
        if hv(req.businessPlace):
            where.append(f"{COL['businessPlace']} = :businessPlace")
            params["businessPlace"] = req.businessPlace
        if hv(req.plant):
            where.append(f"{COL['plant']} = :plant")
            params["plant"] = req.plant
        if hv(req.process):
            where.append(f"{COL['process']} = :process")
            params["process"] = req.process
        if hv(req.equipment):
            where.append(f"{COL['equipment']} = :equipment")
            params["equipment"] = req.equipment

        return where, params

    # ------------------------ 목록 조회 ------------------------

    def get_inspection_list(self, req: inspectionGridRequest):
        db: Session = next(get_db())
        try:
            where_conditions, params = self._common_where(req)
            hv = self._has_value

            # 추가 필터
            if hv(req.inspectionType):
                where_conditions.append(f"{COL['inspectionType']} = :inspectionType")
                params["inspectionType"] = req.inspectionType

            if hv(req.itemNumber):
                where_conditions.append(f"{COL['itemNumber']} = :itemNumber")
                params["itemNumber"] = req.itemNumber

            if hv(req.shiftType):
                where_conditions.append(f"{COL['shiftType']} = :shiftType")
                params["shiftType"] = req.shiftType

            if hv(req.workSequence):
                where_conditions.append(f"{COL['workSequence']} = :workSequence")
                params["workSequence"] = req.workSequence

            if hv(req.workType):
                where_conditions.append(f"{COL['workType']} = :workType")
                params["workType"] = req.workType

            if hv(req.inspectionSequence):
                where_conditions.append(f"{COL['inspectionSequence']} = :inspectionSequence")
                params["inspectionSequence"] = req.inspectionSequence

            if hv(req.inspectionItemName):
                where_conditions.append(f"{COL['inspectionItemName']} LIKE :inspectionItemName")
                params["inspectionItemName"] = f"%{req.inspectionItemName.strip()}%"

            if hv(req.inspectionDetails):
                where_conditions.append(f"{COL['inspectionDetails']} LIKE :inspectionDetails")
                params["inspectionDetails"] = f"%{req.inspectionDetails.strip()}%"

            if hv(req.productionValue):
                where_conditions.append(f"{COL['productionValue']} = :productionValue")
                params["productionValue"] = req.productionValue

            if not where_conditions:
                where_conditions.append("1=1")

            sql = f"SELECT * FROM {TABLE} WHERE {' AND '.join(where_conditions)}"
            print(f"[list] SQL: {sql}\nParams: {params}")

            result = db.execute(text(sql), params)
            rows = result.mappings().all()

            # 한글 컬럼 → 프론트 필드 매핑
            mapped = []
            for row in rows:
                mapped.append({
                    "id": row.get("id"),
                    "businessPlace": row.get("사업장", ''),
                    "plant": row.get("공장", ''),
                    "process": row.get("공정", ''),
                    "equipment": row.get("설비", ''),
                    "inspectionType": row.get("검사구분", ''),
                    "itemNumber": row.get("품번", ''),
                    "reportDate": row.get("보고일", ''),
                    "shiftType": row.get("주야구분", ''),
                    "workSequence": row.get("작업순번"),
                    "workType": row.get("작업구분", ''),
                    "inspectionSequence": row.get("검사순번"),
                    "inspectionItemName": row.get("검사항목명", ''),
                    "inspectionDetails": row.get("검사내용", ''),
                    "productionValue": row.get("생산"),
                })
            return mapped
        finally:
            db.close()

    # ------------------------ 옵션 공통 실행기 ------------------------

    def _distinct_values(
        self, column_sql: str, req: inspectionGridRequest, extra_filters: List[Tuple[str, str]] = None
    ) -> List[str]:
        """
        특정 컬럼의 DISTINCT 값을 반환.
        extra_filters: [(param_key, sql_expr), ...] 형태로 추가 WHERE를 넣을 수 있음.
        """
        db: Session = next(get_db())
        try:
            where, params = self._common_where(req)
            if extra_filters:
                for key, expr in extra_filters:
                    val = getattr(req, key, None)
                    if self._has_value(val):
                        where.append(expr)
                        params[key] = val

            if not where:
                where.append("1=1")

            sql = f"""
                SELECT DISTINCT {column_sql} AS val
                FROM {TABLE}
                WHERE {' AND '.join(where)}
                ORDER BY val
            """
            print(f"[distinct] SQL: {sql}\nParams: {params}")

            result = db.execute(text(sql), params)
            rows = result.fetchall()
            return [r[0] for r in rows if r[0] is not None and str(r[0]).strip() != ""]
        finally:
            db.close()

    # ------------------------ 옵션별 메서드 ------------------------

    def get_distinct_plants(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_values(
            COL["plant"],
            req,
            extra_filters=[("businessPlace", f"{COL['businessPlace']} = :businessPlace")]
        )

    def get_distinct_processes(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_values(
            COL["process"],
            req,
            extra_filters=[("plant", f"{COL['plant']} = :plant")]
        )

    def get_distinct_equipments(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_values(
            COL["equipment"],
            req,
            extra_filters=[
                ("plant", f"{COL['plant']} = :plant"),
                ("process", f"{COL['process']} = :process"),
            ]
        )

    def get_distinct_part_nos(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_values(
            COL["itemNumber"],
            req,
            extra_filters=[
                ("plant", f"{COL['plant']} = :plant"),
                ("process", f"{COL['process']} = :process"),
                ("equipment", f"{COL['equipment']} = :equipment"),
            ]
        )

    def get_distinct_part_names(self, req: inspectionGridRequest) -> List[str]:
        """
        품명 컬럼이 실제 존재한다면 COL_PART_NAME을 해당 컬럼으로 교체.
        없으면 안전하게 빈 배열 반환.
        """
        COL_PART_NAME = "`품명`"  # 실제 DB에 있을 때만 사용
        try:
            return self._distinct_values(
                COL_PART_NAME,
                req,
                extra_filters=[
                    ("plant", f"{COL['plant']} = :plant"),
                    ("process", f"{COL['process']} = :process"),
                    ("equipment", f"{COL['equipment']} = :equipment"),
                ]
            )
        except Exception:
            return []


inspection_grid_service = Inspection_grid_service()
