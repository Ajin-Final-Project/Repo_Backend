# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from app.config.database import get_db
# from app.models.inspectionGrid import inspectionGridRequest
# from decimal import Decimal
# from typing import Dict, List, Tuple, Any


# TABLE = "`AJIN_newDB`.`검사내역`"

# # DB 컬럼명(한글)
# COL = {
#     "businessPlace": "`사업장`",
#     "plant": "`공장`",
#     "process": "`공정`",
#     "equipment": "`설비`",
#     "inspectionType": "`검사구분`",
#     "itemNumber": "`품번`",
#     "reportDate": "`보고일`",
#     "shiftType": "`주야구분`",
#     "workSequence": "`작업순번`",
#     "workType": "`작업구분`",
#     "inspectionSequence": "`검사순번`",
#     "inspectionItemName": "`검사항목명`",
#     "inspectionDetails": "`검사내용`",
#     "productionValue": "`생산`",
# }


# class Inspection_grid_service:
#     # ------------------------ 내부 공용 유틸 ------------------------

#     @staticmethod
#     def _has_value(value: Any) -> bool:
#         if value is None:
#             return False
#         if isinstance(value, str):
#             return value.strip() not in ("", "string")
#         if isinstance(value, (int, Decimal, float)):
#             return True
#         return True

#     def _common_where(self, req: inspectionGridRequest) -> Tuple[List[str], Dict[str, Any]]:
#         """
#         목록/옵션 공통 WHERE 절 + 파라미터 구성
#         - 기간 필터, 기본 필드들 포함
#         """
#         where: List[str] = []
#         params: Dict[str, Any] = {}

#         hv = self._has_value

#         # 기간
#         if hv(req.start_work_date):
#             where.append(f"DATE({COL['reportDate']}) >= :start_work_date")
#             params["start_work_date"] = req.start_work_date
#         if hv(req.end_work_date):
#             where.append(f"DATE({COL['reportDate']}) <= :end_work_date")
#             params["end_work_date"] = req.end_work_date

#         # 상위 필터
#         if hv(req.businessPlace):
#             where.append(f"{COL['businessPlace']} = :businessPlace")
#             params["businessPlace"] = req.businessPlace
#         if hv(req.plant):
#             where.append(f"{COL['plant']} = :plant")
#             params["plant"] = req.plant
#         if hv(req.process):
#             where.append(f"{COL['process']} = :process")
#             params["process"] = req.process
#         if hv(req.equipment):
#             where.append(f"{COL['equipment']} = :equipment")
#             params["equipment"] = req.equipment

#         return where, params

#     # ------------------------ 목록 조회 ------------------------

#     def get_inspection_list(self, req: inspectionGridRequest):
#         db: Session = next(get_db())
#         try:
#             where_conditions, params = self._common_where(req)
#             hv = self._has_value

#             # 추가 필터
#             if hv(req.inspectionType):
#                 where_conditions.append(f"{COL['inspectionType']} = :inspectionType")
#                 params["inspectionType"] = req.inspectionType

#             if hv(req.itemNumber):
#                 where_conditions.append(f"{COL['itemNumber']} = :itemNumber")
#                 params["itemNumber"] = req.itemNumber

#             if hv(req.shiftType):
#                 where_conditions.append(f"{COL['shiftType']} = :shiftType")
#                 params["shiftType"] = req.shiftType

#             if hv(req.workSequence):
#                 where_conditions.append(f"{COL['workSequence']} = :workSequence")
#                 params["workSequence"] = req.workSequence

#             if hv(req.workType):
#                 where_conditions.append(f"{COL['workType']} = :workType")
#                 params["workType"] = req.workType

#             if hv(req.inspectionSequence):
#                 where_conditions.append(f"{COL['inspectionSequence']} = :inspectionSequence")
#                 params["inspectionSequence"] = req.inspectionSequence

#             if hv(req.inspectionItemName):
#                 where_conditions.append(f"{COL['inspectionItemName']} LIKE :inspectionItemName")
#                 params["inspectionItemName"] = f"%{req.inspectionItemName.strip()}%"

#             if hv(req.inspectionDetails):
#                 where_conditions.append(f"{COL['inspectionDetails']} LIKE :inspectionDetails")
#                 params["inspectionDetails"] = f"%{req.inspectionDetails.strip()}%"

#             if hv(req.productionValue):
#                 where_conditions.append(f"{COL['productionValue']} = :productionValue")
#                 params["productionValue"] = req.productionValue

#             if not where_conditions:
#                 where_conditions.append("1=1")

#             sql = f"SELECT * FROM {TABLE} WHERE {' AND '.join(where_conditions)}"
#             print(f"[list] SQL: {sql}\nParams: {params}")

#             result = db.execute(text(sql), params)
#             rows = result.mappings().all()

#             # 한글 컬럼 → 프론트 필드 매핑
#             mapped = []
#             for row in rows:
#                 mapped.append({
#                     "id": row.get("id"),
#                     "businessPlace": row.get("사업장", ''),
#                     "plant": row.get("공장", ''),
#                     "process": row.get("공정", ''),
#                     "equipment": row.get("설비", ''),
#                     "inspectionType": row.get("검사구분", ''),
#                     "itemNumber": row.get("품번", ''),
#                     "reportDate": row.get("보고일", ''),
#                     "shiftType": row.get("주야구분", ''),
#                     "workSequence": row.get("작업순번"),
#                     "workType": row.get("작업구분", ''),
#                     "inspectionSequence": row.get("검사순번"),
#                     "inspectionItemName": row.get("검사항목명", ''),
#                     "inspectionDetails": row.get("검사내용", ''),
#                     "productionValue": row.get("생산"),
#                 })
#             return mapped
#         finally:
#             db.close()

#     # ------------------------ 옵션 공통 실행기 ------------------------

#     def _distinct_values(
#         self, column_sql: str, req: inspectionGridRequest, extra_filters: List[Tuple[str, str]] = None
#     ) -> List[str]:
#         """
#         특정 컬럼의 DISTINCT 값을 반환.
#         extra_filters: [(param_key, sql_expr), ...] 형태로 추가 WHERE를 넣을 수 있음.
#         """
#         db: Session = next(get_db())
#         try:
#             where, params = self._common_where(req)
#             if extra_filters:
#                 for key, expr in extra_filters:
#                     val = getattr(req, key, None)
#                     if self._has_value(val):
#                         where.append(expr)
#                         params[key] = val

#             if not where:
#                 where.append("1=1")

#             sql = f"""
#                 SELECT DISTINCT {column_sql} AS val
#                 FROM {TABLE}
#                 WHERE {' AND '.join(where)}
#                 ORDER BY val
#             """
#             print(f"[distinct] SQL: {sql}\nParams: {params}")

#             result = db.execute(text(sql), params)
#             rows = result.fetchall()
#             return [r[0] for r in rows if r[0] is not None and str(r[0]).strip() != ""]
#         finally:
#             db.close()

#     # ------------------------ 옵션별 메서드 ------------------------

#     def get_distinct_plants(self, req: inspectionGridRequest) -> List[str]:
#         return self._distinct_values(
#             COL["plant"],
#             req,
#             extra_filters=[("businessPlace", f"{COL['businessPlace']} = :businessPlace")]
#         )

#     def get_distinct_processes(self, req: inspectionGridRequest) -> List[str]:
#         return self._distinct_values(
#             COL["process"],
#             req,
#             extra_filters=[("plant", f"{COL['plant']} = :plant")]
#         )

#     def get_distinct_equipments(self, req: inspectionGridRequest) -> List[str]:
#         return self._distinct_values(
#             COL["equipment"],
#             req,
#             extra_filters=[
#                 ("plant", f"{COL['plant']} = :plant"),
#                 ("process", f"{COL['process']} = :process"),
#             ]
#         )

#     def get_distinct_part_nos(self, req: inspectionGridRequest) -> List[str]:
#         return self._distinct_values(
#             COL["itemNumber"],
#             req,
#             extra_filters=[
#                 ("plant", f"{COL['plant']} = :plant"),
#                 ("process", f"{COL['process']} = :process"),
#                 ("equipment", f"{COL['equipment']} = :equipment"),
#             ]
#         )

#     def get_distinct_part_names(self, req: inspectionGridRequest) -> List[str]:
#         """
#         품명 컬럼이 실제 존재한다면 COL_PART_NAME을 해당 컬럼으로 교체.
#         없으면 안전하게 빈 배열 반환.
#         """
#         COL_PART_NAME = "`품명`"  # 실제 DB에 있을 때만 사용
#         try:
#             return self._distinct_values(
#                 COL_PART_NAME,
#                 req,
#                 extra_filters=[
#                     ("plant", f"{COL['plant']} = :plant"),
#                     ("process", f"{COL['process']} = :process"),
#                     ("equipment", f"{COL['equipment']} = :equipment"),
#                 ]
#             )
#         except Exception:
#             return []


# inspection_grid_service = Inspection_grid_service()

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.inspectionGrid import inspectionGridRequest
from decimal import Decimal
from typing import Dict, List, Tuple, Any

# 원하는 공통 collation 하나로 고정 (DB 상황에 맞게 둘 중 하나를 쓰세요)
# ex) 생산내역 테이블이 utf8mb4_general_ci 라면 general_ci 로 통일
COLL = "utf8mb4_general_ci"   # 또는 "utf8mb4_0900_ai_ci"

# 테이블
T_INSPECTION = "`AJIN_newDB`.`검사내역`"
T_PRODUCTION = "`AJIN_newDB`.`생산내역`"      # ← 마스터(기준)

# ===== 생산내역 컬럼(한글) =====
# ⚠️ 매핑 규칙: 플랜트(=공장), 책임자(=공정), 작업장(=설비)
P = {
    "workDate":  "`근무일자`",
    "plant":     "`플랜트`",    # (= 공장)
    "process":   "`책임자`",    # (= 공정)
    "equipment": "`작업장`",    # (= 설비)
    "itemNo":    "`자재번호`",
    "itemName":  "`자재명`",
    "resultNo":  "`실적번호`",
    "carType":   "`차종`",
    "goodQty":   "`양품수량`",
    "prodQty":   "`생산수량`",
    "defectTotal": "`불량합계`",
}

# ===== 검사내역 컬럼(한글) =====
I = {
    "businessPlace": "`사업장`",
    "plant":         "`공장`",
    "process":       "`공정`",
    "equipment":     "`설비`",
    "inspectionType": "`검사구분`",
    "itemNo":        "`품번`",
    "reportDate":    "`보고일`",
    "shiftType":     "`주야구분`",
    "workSeq":       "`작업순번`",
    "workType":      "`작업구분`",
    "inspSeq":       "`검사순번`",
    "inspItem":      "`검사항목명`",
    "inspDetail":    "`검사내용`",
    "production":    "`생산`",
}

# -------- 동의어 매핑 --------
SYNONYMS = {
    # 공장(=플랜트)
    "plant": {
        "본사공장": ["본사공장", "아진산업-경산(본사)"],
        "아진산업-경산(본사)": ["본사공장", "아진산업-경산(본사)"],
    },
    # 설비(=작업장)
    "equipment": {
        "E라인": ["E라인", "1500T"],
        "1500T": ["E라인", "1500T"],
    },
}

def expand_vals(kind: str, val: str) -> List[str]:
    """동의어 확장"""
    if val is None or str(val).strip() == "":
        return []
    val = str(val).strip()
    return SYNONYMS.get(kind, {}).get(val, [val])

def _qual_p(col_backticked: str) -> str:
    """생산내역 컬럼에 p. 접두어 부여"""
    return f"p.{col_backticked}"

def _qual_i(col_backticked: str) -> str:
    """검사내역 컬럼에 i. 접두어 부여"""
    return f"i.{col_backticked}"

def _col(col_sql: str) -> str:
    """해당 컬럼 비교용으로 공통 COLLATE 부여"""
    return f"{col_sql} COLLATE {COLL}"

def _in_clause(col_sql: str, values: List[str], params: Dict[str, Any], base_name: str) -> str:
    """
    안전한 IN 절 생성기 (text()에서 tuple 확장 문제 회피)
    ex) col IN (:base_name_0, :base_name_1, ...)
    """
    if not values:
        return "1=0"
    if len(values) == 1:
        pname = f"{base_name}_0"
        params[pname] = values[0]
        return f"{_col(col_sql)} = :{pname}"
    placeholders = []
    for idx, v in enumerate(values):
        pname = f"{base_name}_{idx}"
        params[pname] = v
        placeholders.append(f":{pname}")
    return f"{_col(col_sql)} IN ({', '.join(placeholders)})"


class Inspection_grid_service:
    # ------------------------ 내부 유틸 ------------------------
    @staticmethod
    def _has_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() not in ("", "string")
        if isinstance(value, (int, Decimal, float)):
            return True
        return True

    # ------------------------ 메인 목록: 생산내역 마스터 + 검사내역 LEFT JOIN ------------------------
    def get_inspection_list(self, req: inspectionGridRequest):
        db: Session = next(get_db())
        try:
            hv = self._has_value
            where_sql: List[str] = []
            params: Dict[str, Any] = {}

            # 기간: 생산내역(근무일자) 기준
            if hv(req.start_work_date):
                where_sql.append(f"DATE({_qual_p(P['workDate'])}) >= :start_work_date")
                params["start_work_date"] = req.start_work_date
            if hv(req.end_work_date):
                where_sql.append(f"DATE({_qual_p(P['workDate'])}) <= :end_work_date")
                params["end_work_date"] = req.end_work_date

            # 상위 필터들 (모두 '생산내역' 기준)
            if hv(req.plant):
                plant_vals = expand_vals("plant", req.plant)
                where_sql.append(_in_clause(_qual_p(P["plant"]), plant_vals, params, "plant_vals"))
            if hv(req.process):
                pname = "process"
                params[pname] = req.process
                where_sql.append(f"{_col(_qual_p(P['process']))} = :{pname}")
            if hv(req.equipment):
                equip_vals = expand_vals("equipment", req.equipment)
                where_sql.append(_in_clause(_qual_p(P["equipment"]), equip_vals, params, "equip_vals"))
            if hv(req.itemNumber):
                params["itemNumber"] = req.itemNumber
                where_sql.append(f"{_col(_qual_p(P['itemNo']))} = :itemNumber")

            # 검사쪽 추가 필터들 (LEFT JOIN 주의)
            if hv(req.inspectionType):
                params["inspectionType"] = req.inspectionType
                where_sql.append(f"{_col(_qual_i(I['inspectionType']))} = :inspectionType")
            if hv(req.shiftType):
                params["shiftType"] = req.shiftType
                where_sql.append(f"{_col(_qual_i(I['shiftType']))} = :shiftType")
            if hv(req.workSequence):
                params["workSequence"] = req.workSequence
                where_sql.append(f"{_qual_i(I['workSeq'])} = :workSequence")
            if hv(req.workType):
                params["workType"] = req.workType
                where_sql.append(f"{_col(_qual_i(I['workType']))} = :workType")
            if hv(req.inspectionSequence):
                params["inspectionSequence"] = req.inspectionSequence
                where_sql.append(f"{_qual_i(I['inspSeq'])} = :inspectionSequence")
            if hv(req.inspectionItemName):
                params["inspectionItemName"] = f"%{req.inspectionItemName.strip()}%"
                where_sql.append(f"{_col(_qual_i(I['inspItem']))} LIKE :inspectionItemName")
            if hv(req.inspectionDetails):
                params["inspectionDetails"] = f"%{req.inspectionDetails.strip()}%"
                where_sql.append(f"{_col(_qual_i(I['inspDetail']))} LIKE :inspectionDetails")
            if hv(req.productionValue):
                params["productionValue"] = req.productionValue
                where_sql.append(f"{_qual_i(I['production'])} = :productionValue")

            if not where_sql:
                where_sql.append("1=1")

            # ----- JOIN (품번 + 날짜 + 설비/공장 동의어 매칭) -----
            join_sql = f"""
            LEFT JOIN {T_INSPECTION} i
              ON {_col("i.품번")} = {_col("p.자재번호")}
             AND DATE(i.보고일) = DATE(p.근무일자)
             AND (
                   {_col("i.설비")} = {_col("p.작업장")}
                OR ({_col("i.설비")} IN ('E라인','1500T') AND {_col("p.작업장")} IN ('E라인','1500T'))
             )
             AND (
                   {_col("i.공장")} = {_col("p.플랜트")}
                OR ({_col("i.공장")} IN ('본사공장','아진산업-경산(본사)')
                    AND {_col("p.플랜트")} IN ('본사공장','아진산업-경산(본사)'))
             )
            """

            sql = f"""
            SELECT
              ROW_NUMBER() OVER() AS id,

              -- 생산(마스터)
              p.플랜트     AS plant,
              p.책임자     AS process,    -- (= 공정)
              p.작업장     AS equipment,  -- (= 설비)
              p.근무일자   AS workDate,
              p.자재번호   AS itemNumber,
              p.자재명     AS itemName,
              p.실적번호   AS resultNo,
              p.차종       AS carType,
              p.양품수량   AS goodQty,
              p.생산수량   AS prodQty,
              p.불량합계   AS defectTotal,

              -- 검사(붙임)
              i.사업장     AS businessPlace,
              i.공장       AS i_plant,
              i.공정       AS i_process,
              i.설비       AS i_equipment,
              i.검사구분   AS inspectionType,
              i.보고일     AS reportDate,
              i.주야구분   AS shiftType,
              i.작업순번   AS workSequence,
              i.작업구분   AS workType,
              i.검사순번   AS inspectionSequence,
              i.검사항목명 AS inspectionItemName,
              i.검사내용   AS inspectionDetails,
              i.생산       AS productionValue
            FROM {T_PRODUCTION} p
            {join_sql}
            WHERE {" AND ".join(where_sql)}
            ORDER BY p.근무일자 DESC, p.자재번호 ASC, COALESCE(i.검사순번,0) ASC
            """

            print("[JOIN master=생산내역] SQL:", sql, "\nParams:", params)
            rows = db.execute(text(sql), params).mappings().all()

            # 프론트 매핑
            mapped = []
            for r in rows:
                mapped.append({
                    "id": r["id"],

                    # 그리드 기본(생산 기준)
                    "plant": r["plant"],
                    "process": r["process"],
                    "equipment": r["equipment"],
                    "reportDate": r["workDate"],          # 기간은 생산 근무일자 기준
                    "itemNumber": r["itemNumber"],
                    "itemName": r["itemName"],

                    # 검사 정보
                    "inspectionType": r["inspectionType"],
                    "inspectionItemName": r["inspectionItemName"],
                    "inspectionDetails": r["inspectionDetails"],
                    "shiftType": r["shiftType"],
                    "workSequence": r["workSequence"],
                    "workType": r["workType"],
                    "inspectionSequence": r["inspectionSequence"],
                    "productionValue": r["productionValue"],

                    # 생산 지표
                    "prodQty": r["prodQty"],
                    "goodQty": r["goodQty"],
                    "defectTotal": r["defectTotal"],
                    "resultNo": r["resultNo"],
                    "carType": r["carType"],
                })
            return mapped
        finally:
            db.close()

    # ------------------------ 옵션은 전부 '생산내역'에서 DISTINCT ------------------------
    def _distinct_from_production(
        self,
        col_sql: str,
        req: inspectionGridRequest,
        extra: List[Tuple[str, str]] = None
    ) -> List[str]:
        db: Session = next(get_db())
        try:
            hv = self._has_value
            where: List[str] = []
            params: Dict[str, Any] = {}

            # 기간(생산 기준)
            if hv(req.start_work_date):
                where.append(f"DATE({_qual_p(P['workDate'])}) >= :start_work_date")
                params["start_work_date"] = req.start_work_date
            if hv(req.end_work_date):
                where.append(f"DATE({_qual_p(P['workDate'])}) <= :end_work_date")
                params["end_work_date"] = req.end_work_date

            # 상위 필터(생산 컬럼)
            if hv(req.plant):
                plant_vals = expand_vals("plant", req.plant)
                where.append(_in_clause(_qual_p(P["plant"]), plant_vals, params, "plant_vals"))
            if hv(req.process):
                params["process"] = req.process
                where.append(f"{_col(_qual_p(P['process']))} = :process")
            if hv(req.equipment):
                equip_vals = expand_vals("equipment", req.equipment)
                where.append(_in_clause(_qual_p(P["equipment"]), equip_vals, params, "equip_vals"))

            if not where:
                where.append("1=1")

            sql = f"""
            SELECT DISTINCT {col_sql} AS val
            FROM {T_PRODUCTION} p
            WHERE {" AND ".join(where)}
            ORDER BY val
            """
            print("[options from 생산내역] SQL:", sql, "\nParams:", params)
            rows = db.execute(text(sql), params).fetchall()
            return [r[0] for r in rows if r[0] is not None and str(r[0]).strip() != ""]
        finally:
            db.close()

    # ----- 옵션 API들 -----
    def get_distinct_plants(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_from_production(_qual_p(P["plant"]), req)

    def get_distinct_processes(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_from_production(_qual_p(P["process"]), req)

    def get_distinct_equipments(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_from_production(_qual_p(P["equipment"]), req)

    def get_distinct_part_nos(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_from_production(_qual_p(P["itemNo"]), req)

    def get_distinct_part_names(self, req: inspectionGridRequest) -> List[str]:
        return self._distinct_from_production(_qual_p(P["itemName"]), req)


inspection_grid_service = Inspection_grid_service()
