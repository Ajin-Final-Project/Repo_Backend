from typing import Dict, Any, List, Set
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.defect_modal import DefectModalReq

T_DEFECT  = "불량수량 및 유형"
QT_DEFECT = "`불량수량 및 유형`"
T_INSP    = "생산_검사"
QT_INSP   = "`생산_검사`"

# 후보 컬럼 목록 (테이블별로 실제 존재하는 이름이 다를 수 있어 COALESCE로 처리)
CAND = {
    # 불량 테이블 a.*
    "d_workDate":  ["근무일자", "보고일", "검사일자", "작업일자", "등록일자", "일자", "date"],
    "d_partNo":    ["자재번호", "품목번호", "품번", "PART_NO", "PartNo"],
    "d_item":      ["품명", "품목명", "품목명칭", "자재명"],
    "d_defType":   ["불량유형", "불량명", "불량유형명"],
    "d_goodQty":   ["양품수량", "양품수"],
    "d_defQty":    ["불량수량", "불량수"],
    "d_rwkQty":    ["RWK 수량", "RWK수량", "Rwk수량", "Rwk"],
    "d_scrapQty":  ["폐기 수량", "폐기수량", "Scrap수량", "폐기"],
    "d_workType":  ["작업구분"],
    "d_inspType":  ["검사구분"],
    "d_note":      ["비고", "메모"],

    # 생산_검사 x.*  (유일화 서브쿼리에서 사용)
    "i_workDate":  ["work_date", "보고일", "근무일자", "검사일자"],
    "i_process":   ["process", "공정", "작업장", "작업장명"],
    "i_equipment": ["equipment", "설비", "라인", "라인명", "설비명"],
    "i_factory":   ["plant", "공장", "공장명", "사업장"],
    "i_partNo":    ["자재번호", "품목번호", "품번", "PART_NO", "PartNo"],
    "i_item":      ["자재명", "품목명", "품명", "ITEM_NM", "ItemName"],
}

def _existing_columns(db: Session, table: str) -> Set[str]:
    sql = """
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t
    """
    return {r[0] for r in db.execute(text(sql), {"t": table}).all()}

def _present(cols: Set[str], names: List[str]) -> List[str]:
    return [c for c in names if c in cols]

def _coalesce_expr(prefix: str, present: List[str], cast_date=False, trim=True, default_null="NULL") -> str:
    """present 리스트에 있는 컬럼들을 prefix(=a/b/x)로 COALESCE"""
    if not present:
        return default_null
    parts = [f"{prefix}.`{c}`" for c in present]
    core = parts[0] if len(parts) == 1 else f"COALESCE({', '.join(parts)})"
    if trim:
        core = f"NULLIF(TRIM({core}), '')"
    if cast_date:
        core = f"CAST({core} AS DATE)"
    return core

def _build_exprs(db: Session) -> Dict[str, str]:
    cols_d = _existing_columns(db, T_DEFECT)
    cols_i = _existing_columns(db, T_INSP)

    # a.* (불량 테이블)
    a_date   = _coalesce_expr("a", _present(cols_d, CAND["d_workDate"]), cast_date=True, trim=False)
    a_part   = _coalesce_expr("a", _present(cols_d, CAND["d_partNo"]))
    a_item   = _coalesce_expr("a", _present(cols_d, CAND["d_item"]))
    a_defTp  = _coalesce_expr("a", _present(cols_d, CAND["d_defType"]), trim=False)
    a_good   = _coalesce_expr("a", _present(cols_d, CAND["d_goodQty"]), trim=False, default_null="0")
    a_def    = _coalesce_expr("a", _present(cols_d, CAND["d_defQty"]),  trim=False, default_null="0")
    a_rwk    = _coalesce_expr("a", _present(cols_d, CAND["d_rwkQty"]),  trim=False, default_null="0")
    a_scrap  = _coalesce_expr("a", _present(cols_d, CAND["d_scrapQty"]),trim=False, default_null="0")
    a_workTp = _coalesce_expr("a", _present(cols_d, CAND["d_workType"]),trim=False)
    a_inspTp = _coalesce_expr("a", _present(cols_d, CAND["d_inspType"]),trim=False)
    a_note   = _coalesce_expr("a", _present(cols_d, CAND["d_note"]),    trim=False)

    # defectQty: RWK+폐기 있으면 합산, 없으면 불량수량
    defect_qty_expr = f"(IFNULL({a_rwk},0) + IFNULL({a_scrap},0))" \
        if (_present(cols_d, CAND["d_rwkQty"]) or _present(cols_d, CAND["d_scrapQty"])) else f"IFNULL({a_def},0)"

    # x.* (생산_검사) — 유일화 서브쿼리용
    b_date   = _coalesce_expr("x", _present(cols_i, CAND["i_workDate"]), cast_date=True, trim=False)
    b_proc   = _coalesce_expr("x", _present(cols_i, CAND["i_process"]))
    b_equip  = _coalesce_expr("x", _present(cols_i, CAND["i_equipment"]))
    b_part   = _coalesce_expr("x", _present(cols_i, CAND["i_partNo"]))
    b_item   = _coalesce_expr("x", _present(cols_i, CAND["i_item"]))

    # factory: plant가 없으면 사업장-공장 조합
    has_plant = "plant" in _existing_columns(db, T_INSP)
    if has_plant:
        b_fact = _coalesce_expr("x", ["plant"])
    else:
        pieces = [p for p in ["사업장", "공장"] if p in _existing_columns(db, T_INSP)]
        if len(pieces) == 2:
            b_fact = f"CONCAT(TRIM(x.`사업장`), '-', TRIM(x.`공장`))"
        else:
            b_fact = _coalesce_expr("x", _present(cols_i, CAND["i_factory"]))

    subq = f"""
      SELECT
        {b_date}  AS work_date,
        {b_proc}  AS process,
        {b_equip} AS equipment,
        {b_fact}  AS factory,
        {b_part}  AS part_no,
        {b_item}  AS item_name
      FROM {QT_INSP} x
      GROUP BY work_date, process, equipment, factory, part_no, item_name
    """

    return dict(
        a_date=a_date, a_part=a_part, a_item=a_item, a_defTp=a_defTp, a_good=a_good,
        a_workTp=a_workTp, a_inspTp=a_inspTp, a_note=a_note, defect_qty=defect_qty_expr,
        subq=subq
    )

# ---------------------- 리스트 ----------------------
def list_defects(db: Session, req: DefectModalReq) -> List[Dict[str, Any]]:
    E = _build_exprs(db)

    sql = f"""
    SELECT
      {E['a_date']}                        AS workDate,
      b.factory                            AS factory,
      b.process                            AS process,
      b.equipment                          AS equipment,
      COALESCE({E['a_part']}, b.part_no)   AS partNo,
      COALESCE({E['a_item']}, b.item_name) AS item,
      {E['a_defTp']}                       AS defectType,
      {E['defect_qty']}                    AS defectQty,
      IFNULL({E['a_good']}, 0)             AS goodQty,
      {E['a_workTp']}                      AS workType,
      {E['a_inspTp']}                      AS inspType,
      {E['a_note']}                        AS note
    FROM {QT_DEFECT} a
    INNER JOIN ( {E['subq']} ) b
      ON b.work_date = {E['a_date']}
     AND (
          (b.part_no   IS NOT NULL AND {E['a_part']} = b.part_no) OR
          (b.item_name IS NOT NULL AND {E['a_item']} = b.item_name)
         )
    WHERE 1=1
      AND (:startDate IS NULL OR :endDate IS NULL OR {E['a_date']} BETWEEN :startDate AND :endDate)
      AND (:factory   IS NULL OR :factory   = '' OR b.factory   = :factory)
      AND (:process   IS NULL OR :process   = '' OR b.process   = :process)
      AND (:equipment IS NULL OR :equipment = '' OR b.equipment = :equipment)
      AND (:partNo    IS NULL OR :partNo    = '' OR COALESCE({E['a_part']}, b.part_no)   = :partNo)
      AND (:item      IS NULL OR :item      = '' OR COALESCE({E['a_item']}, b.item_name) LIKE CONCAT('%', :item, '%'))
      AND ({E['defect_qty']}) > 0
    ORDER BY workDate DESC, process, equipment, partNo, defectType
    LIMIT :limit OFFSET :offset
    """

    params = {
        "startDate": req.startDate,
        "endDate":   req.endDate,
        "factory":   (req.factory or "").strip() or None,
        "process":   (req.process or "").strip() or None,
        "equipment": (req.equipment or "").strip() or None,
        "partNo":    (req.partNo or "").strip() or None,
        "item":      (req.item or "").strip() or None,
        "limit": int(req.limit or 500),
        "offset": int(req.offset or 0),
    }
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]

# ---------------------- 옵션 ----------------------
def option_values(db: Session, req: DefectModalReq, which: str) -> List[Dict[str, Any]]:
    """
    which ∈ { 'factory','process','equipment','partNo','item','defectType','workType','inspType' }
    """
    E = _build_exprs(db)

    # 타깃 표현식
    targets = {
        "factory":   "b.factory",
        "process":   "b.process",
        "equipment": "b.equipment",
        "partNo":    f"COALESCE({E['a_part']}, b.part_no)",
        "item":      f"COALESCE({E['a_item']}, b.item_name)",
        "defectType":E['a_defTp'],
        "workType":  E['a_workTp'],
        "inspType":  E['a_inspTp'],
    }
    target = targets.get(which)
    if not target:
        return []

    sql = f"""
    SELECT {target} AS value, COUNT(*) AS count
    FROM {QT_DEFECT} a
    INNER JOIN ( {E['subq']} ) b
      ON b.work_date = {E['a_date']}
     AND (
          (b.part_no   IS NOT NULL AND {E['a_part']} = b.part_no) OR
          (b.item_name IS NOT NULL AND {E['a_item']} = b.item_name)
         )
    WHERE 1=1
      AND (:startDate IS NULL OR :endDate IS NULL OR {E['a_date']} BETWEEN :startDate AND :endDate)
    """

    # 타깃 자신은 필터에서 제외하고 나머지 조건만 반영
    if which != "factory":
        sql += "  AND (:factory   IS NULL OR :factory   = '' OR b.factory   = :factory)\n"
    if which != "process":
        sql += "  AND (:process   IS NULL OR :process   = '' OR b.process   = :process)\n"
    if which != "equipment":
        sql += "  AND (:equipment IS NULL OR :equipment = '' OR b.equipment = :equipment)\n"
    if which != "partNo":
        sql += f"  AND (:partNo    IS NULL OR :partNo    = '' OR COALESCE({E['a_part']}, b.part_no)   = :partNo)\n"
    if which != "item":
        sql += f"  AND (:item      IS NULL OR :item      = '' OR COALESCE({E['a_item']}, b.item_name) LIKE CONCAT('%', :item, '%'))\n"

    sql += f"""  AND ({E['defect_qty']}) > 0
    GROUP BY value
    HAVING value IS NOT NULL AND value <> ''
    ORDER BY value
    """

    params = {
        "startDate": req.startDate,
        "endDate":   req.endDate,
        "factory":   (req.factory or "").strip() or None,
        "process":   (req.process or "").strip() or None,
        "equipment": (req.equipment or "").strip() or None,
        "partNo":    (req.partNo or "").strip() or None,
        "item":      (req.item or "").strip() or None,
    }
    return [dict(r) for r in db.execute(text(sql), params).mappings().all()]

def list_all_options(db: Session, req: DefectModalReq) -> Dict[str, List[Dict[str, Any]]]:
    kinds = ["factory","process","equipment","partNo","item","defectType","workType","inspType"]
    return {k: option_values(db, req, k) for k in kinds}
