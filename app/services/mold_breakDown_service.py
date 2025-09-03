# app/services/mold_breakDown_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.mold_BreakDown import MoldBreakdownRequest


class Mold_breakDown_service:
    """
    금형고장내역 조회 서비스
    - 컬럼 순서: id, 플랜트, 책임자, 작업장, 품번, 품명, 이후 기존 g.* 컬럼
    - 성능 팁:
      * MySQL 8 이상에서 ROW_NUMBER() 사용 (id 생성)
      * 최신순 정렬 + LIMIT (기본 100)
      * LIKE + TRIM/UPPER는 인덱스 미사용 → 가능하면 매핑키로 전환 권장
    """

    def get_moldBreakDown_list(self, req: MoldBreakdownRequest):
        db: Session = next(get_db())
        try:
            where = []
            params = {}

            def has_value(v):
                if v is None:
                    return False
                if isinstance(v, str):
                    s = v.strip()
                    return s != "" and s.lower() != "string"
                return True

            # === 정확 일치(=) ===
            for field, col in [
                ("status", "상태"), ("document", "문서"),
                ("function_location", "기능위치"), ("equipment", "설비"),
                ("order_type", "오더유형"), ("order_type_detail", "오더유형내역"),
                ("order_no", "오더번호"), ("notification_no", "통지번호")
            ]:
                value = getattr(req, field, None)
                if has_value(value):
                    where.append(f"g.`{col}` = :{field}")
                    params[field] = value.strip() if isinstance(value, str) else value

            # === 부분 일치(LIKE) ===
            for field, col in [
                ("function_location_detail", "기능위치내역"),
                ("equipment_detail", "설비내역"),
                ("order_detail", "오더내역"),
                ("failure", "고장")
            ]:
                value = getattr(req, field, None)
                if has_value(value):
                    where.append(f"g.`{col}` LIKE :{field}")
                    params[field] = f"%{value.strip()}%"

            # === 날짜 범위 ===
            start = getattr(req, "start_date", None)
            end = getattr(req, "end_date", None)
            if has_value(start) and has_value(end):
                where.append(
                    """(
                        g.`기본시작일` BETWEEN :start_date AND :end_date
                        OR g.`기본종료일` BETWEEN :start_date AND :end_date
                        OR (g.`기본시작일` <= :start_date AND g.`기본종료일` >= :end_date)
                    )"""
                )
                params["start_date"] = start
                params["end_date"] = end
            elif has_value(start):
                where.append("g.`기본종료일` >= :start_date")
                params["start_date"] = start
            elif has_value(end):
                where.append("g.`기본시작일` <= :end_date")
                params["end_date"] = end

            if not where:
                where.append("1=1")

            # LIMIT 파라미터
            default_limit = 100
            limit_val = min(max(int(getattr(req, "limit", default_limit) or default_limit), 1), 1000)
            params["limit_val"] = limit_val

            # === SELECT: 프론트 그리드 순서에 맞춤 ===
            sql = f"""
WITH 생산내역_중복제거 AS (
    SELECT *
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY 자재번호 ORDER BY 자재번호) AS rn
        FROM `AJIN_newDB`.`생산내역`
    ) t
    WHERE rn = 1
)
SELECT
    COALESCE(s.플랜트, '') AS 플랜트,
    COALESCE(s.책임자, '') AS 책임자,
    COALESCE(s.작업장, '') AS 작업장,
    COALESCE(s.자재번호, '') AS 품번,
    COALESCE(s.자재명, '') AS 품명,
    g.상태,
    g.문서,
    g.기능위치,
    g.기능위치내역,
    g.설비,
    g.설비내역,
    g.오더유형,
    g.오더유형내역,
    g.오더번호,
    g.오더내역,
    g.기본시작일,
    g.기본종료일,
    g.계획비용,
    g.실적비용,
    g.정산비용,
    g.통지번호,
    g.오더내역 AS 고장
FROM `AJIN_newDB`.`금형고장내역` g
LEFT JOIN 생산내역_중복제거 s
    ON g.설비내역 LIKE CONCAT('%', s.자재번호, '%');

            """

            rows = db.execute(text(sql), params).mappings().all()
            print(text(sql))
            print("파람미터", params)
            return [dict(r) for r in rows]

        finally:
            db.close()


mold_breakDown_service = Mold_breakDown_service()
