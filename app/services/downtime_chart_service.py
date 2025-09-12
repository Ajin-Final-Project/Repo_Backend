# app/services/downtime_chart_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.models.downtimeGrid import DowntimeGridResquest

# 사용할 테이블명 직접 지정
T = "`AJIN_newDB`.`비가동시간 및 현황`"

class Downtime_chart_service:

    # -------------------- 자재번호 목록 --------------------
    def get_item_codes(self, req: DowntimeGridResquest):
        db: Session = next(get_db())
        try:
            sql = text(f"""
                SELECT DISTINCT `자재번호`
                FROM {T}
                WHERE (:workplace IS NULL OR `작업장` = :workplace)
                  AND (:start_work_date IS NULL OR `근무일자` >= :start_work_date)
                  AND (:end_work_date   IS NULL OR `근무일자` <= :end_work_date)
                ORDER BY `자재번호`;
            """)
            rows = db.execute(sql, {
                "workplace": req.workplace,
                "start_work_date": req.start_work_date,
                "end_work_date": req.end_work_date
            }).mappings().all()
            return [r["자재번호"] for r in rows]
        finally:
            db.close()

    # -------------------- KPI 요약 (TOP N) --------------------
    def get_summary(self, req: DowntimeGridResquest, top_n: int = 3):
        db: Session = next(get_db())
        try:
            # 총합/건수/평균
            sql_sum = text(f"""
                SELECT
                    COALESCE(SUM(COALESCE(`비가동(분)`,0)),0) / 60 AS total, -- UI에서 '분'표시면 /60 제거 고려
                    COUNT(*) AS count,
                    COALESCE(AVG(COALESCE(`비가동(분)`,0)),0) AS avg
                FROM {T}
                WHERE (:workplace IS NULL OR `작업장` = :workplace)
                  AND (:start_work_date IS NULL OR `근무일자` >= :start_work_date)
                  AND (:end_work_date   IS NULL OR `근무일자` <= :end_work_date)
            """)
            srow = db.execute(sql_sum, {
                "workplace": req.workplace,
                "start_work_date": req.start_work_date,
                "end_work_date": req.end_work_date
            }).mappings().first() or {"total": 0, "count": 0, "avg": 0}

            # TOP N (minutes DESC, 동점 시 이름 ASC)
            top_n_safe = int(top_n if top_n and top_n > 0 else 3)
            sql_topn = text(f"""
                SELECT `비가동명` AS name,
                       SUM(COALESCE(`비가동(분)`,0)) AS minutes
                FROM {T}
                WHERE (:workplace IS NULL OR `작업장` = :workplace)
                  AND (:start_work_date IS NULL OR `근무일자` >= :start_work_date)
                  AND (:end_work_date   IS NULL OR `근무일자` <= :end_work_date)
                GROUP BY `비가동명`
                ORDER BY minutes DESC, `비가동명` ASC
                LIMIT {top_n_safe};
            """)
            top_rows = db.execute(sql_topn, {
                "workplace": req.workplace,
                "start_work_date": req.start_work_date,
                "end_work_date": req.end_work_date,
            }).mappings().all()

            top_list = [
                {"name": r["name"] or "-", "minutes": float(r["minutes"] or 0)}
                for r in top_rows
            ]
            first = top_list[0] if top_list else {"name": "-", "minutes": 0}

            return {
                "total":   float(srow["total"] or 0),
                "count":   int(srow["count"] or 0),
                "avg":     float(srow["avg"]   or 0),
                "topName": first["name"],          # 하위 호환
                "topValue": first["minutes"],      # 하위 호환
                "topList": top_list,               # 신규
            }
        finally:
            db.close()

    # -------------------- 월별 합계 및 해당 월 비가동 top3--------------------
    def get_monthly(self, req: DowntimeGridResquest):
        db: Session = next(get_db())
        try:
            # 월별·비가동명 집계까지 한 번에 가져오기
            sql = text(f"""
                SELECT
                    DATE_FORMAT(`근무일자`, '%Y-%m') AS ym,
                    COALESCE(`비가동명`, '(없음)') AS name,
                    SUM(COALESCE(`비가동(분)`,0)) AS minutes
                FROM {T}
                WHERE (:workplace IS NULL OR `작업장` = :workplace)
                AND (:itemCode  IS NULL OR `자재번호` = :itemCode)
                AND (:start_work_date IS NULL OR `근무일자` >= :start_work_date)
                AND (:end_work_date   IS NULL OR `근무일자` <= :end_work_date)
                GROUP BY DATE_FORMAT(`근무일자`, '%Y-%m'), COALESCE(`비가동명`, '(없음)')
                ORDER BY ym ASC, minutes DESC;
            """)
            rows = [dict(r) for r in db.execute(sql, req.dict()).mappings().all()]

            # 파이썬에서 월별 합계 + top3 계산
            by_month = {}
            for r in rows:
                ym = r["ym"]
                by_month.setdefault(ym, {"total": 0, "list": []})
                by_month[ym]["total"] += float(r["minutes"] or 0)
                by_month[ym]["list"].append({"name": r["name"], "minutes": float(r["minutes"] or 0)})

            result = []
            for ym, info in by_month.items():
                # minutes 내림차순 정렬 후 TOP3 추출
                top3 = sorted(info["list"], key=lambda x: x["minutes"], reverse=True)[:3]
                result.append({
                    "ym": ym,
                    "minutes": info["total"],  # 해당 월 총 비가동(분)
                    "top": top3,               # [{name, minutes}] 최대 3개
                })

            # ym 오름차순으로 정렬 보장
            result.sort(key=lambda x: x["ym"])
            return result
        finally:
            db.close()


    # -------------------- 파이(비가동명 비중) --------------------
    def get_pie(self, req: DowntimeGridResquest, top:int=5, withOthers:bool=True):
        db: Session = next(get_db())
        try:
            sql = text(f"""
                SELECT `비가동명` AS label, SUM(COALESCE(`비가동(분)`,0)) AS minutes
                FROM {T}
                WHERE (:workplace IS NULL OR `작업장` = :workplace)
                  AND (:itemCode  IS NULL OR `자재번호` = :itemCode)
                  AND (:start_work_date IS NULL OR `근무일자` >= :start_work_date)
                  AND (:end_work_date   IS NULL OR `근무일자` <= :end_work_date)
                GROUP BY `비가동명`
                ORDER BY minutes DESC;
            """)
            rows = [dict(r) for r in db.execute(sql, req.dict()).mappings().all()]

            return rows[:top] # 요청하는 품번에 상위 비가동 정보 5개만 반환
        finally:
            db.close()

    # -------------------- 비고 Top --------------------
    def get_top_notes(self, req: DowntimeGridResquest, limit:int=10):
        db: Session = next(get_db())
        try:
            sql = text(f"""
                        SELECT 
                            조치카테고리 AS text,
                            COUNT(*) AS count,
                            SUM(COALESCE(`비가동(분)`,0)) AS minutes
                        FROM (
                            SELECT 
                                CASE
                                    -- 신규 추가 카테고리
                                    WHEN 비고 LIKE '%M/B%' AND 비고 LIKE '%안착%' 
                                        THEN '안착 불량'
                                    WHEN 비고 LIKE '%콤프레셔%' OR 비고 LIKE '%콤프레샤%' OR 비고 LIKE '%에어 탱크%' 
                                        THEN '콤프레셔/에어탱크'
                                    WHEN 비고 LIKE '%소재 틀어짐%' 
                                        THEN '소재 틀어짐'
                                    WHEN 비고 LIKE '%이물질%' 
                                        THEN '이물질 투입'
                                    WHEN 비고 LIKE '%쿠션핀%' 
                                        THEN '쿠션핀 이상'
                                    WHEN 비고 LIKE '%사양교체%' OR 비고 LIKE '%사양변경%' 
                                        THEN '사양 변경/교체'
                                    WHEN 비고 LIKE '%디스테커%' OR 비고 LIKE '%에어 블로우%' 
                                        THEN '디스테커/에어블로우'
                                    WHEN 비고 LIKE '%교육%' 
                                        THEN '교육/훈련'

                                    -- 기존 카테고리
                                    WHEN 비고 LIKE '%품질%' OR 비고 LIKE '%확보%' 
                                        THEN '품질 확인'
                                    WHEN 비고 LIKE '%초품검사%' 
                                        THEN '초품검사'
                                    WHEN 비고 LIKE '%수리조%' OR 비고 LIKE '%수리용 판넬%' 
                                        THEN '수리/판넬'
                                    WHEN 비고 LIKE '%소재%' OR 비고 LIKE '%센터링소재%' 
                                        THEN '소재 대기'
                                    WHEN 비고 LIKE '%비전%' OR 비고 LIKE '%Vision%' 
                                        THEN '비전 검사'
                                    WHEN 비고 LIKE '%스크랩%' 
                                        THEN '스크랩 불량'
                                    WHEN 비고 LIKE '%에어%' 
                                        THEN '에어 이상'
                                    WHEN 비고 LIKE '%티칭%' 
                                        THEN '티칭 관련'
                                    WHEN 비고 LIKE '%하사점%' 
                                        THEN '하사점 이상'
                                    WHEN 비고 LIKE '%낙하%' 
                                        THEN '제품 낙하'
                                    WHEN 비고 LIKE '%발란스%' OR 비고 LIKE '%심 조정%' OR 비고 LIKE '%심조정%' 
                                    OR 비고 LIKE '%심 추가%' OR 비고 LIKE '%심 제거%' OR 비고 LIKE '%심조절%' 
                                        THEN '발란스/심 조정'
                                    WHEN 비고 LIKE '%버 발생%' OR 비고 LIKE '%주름%' OR 비고 LIKE '%홀빨림%' 
                                        THEN '성형 불량'
                                    WHEN 비고 LIKE '%칩%' OR 비고 LIKE '%컷팅%' 
                                        THEN '칩/컷팅 이상'
                                    WHEN 비고 LIKE '%인버터%' 
                                        THEN '인버터 이상'
                                    WHEN 비고 LIKE '%무빙%' OR 비고 LIKE '%그립바%' OR 비고 LIKE '%그립버%' 
                                        THEN '무빙/그립바'
                                    WHEN 비고 LIKE '%자동화%' OR 비고 LIKE '%자동 기동%' OR 비고 LIKE '%운전모드%' OR 비고 LIKE '%운전준비%' 
                                        THEN '자동화/운전모드'
                                    WHEN 비고 LIKE '%조회%' OR 비고 LIKE '%작업준비%' OR 비고 LIKE '%이상무%' 
                                        THEN '생산 준비'

                                    -- 기존 큰 분류
                                    WHEN 비고 LIKE '%진공%' OR 비고 LIKE '%흡착%' OR 비고 LIKE '%2매감지%' OR 비고 LIKE '%소재탈착%' 
                                        THEN '진공/흡착'
                                    WHEN 비고 LIKE '%찍힘%' OR 비고 LIKE '%요철%' OR 비고 LIKE '%쇠까시%' OR 비고 LIKE '%넥%' OR 비고 LIKE '%크랙%' 
                                        THEN '표면불량/크랙'
                                    WHEN 비고 LIKE '%센서%' OR 비고 LIKE '%파트 감지%' OR 비고 LIKE '%언로딩%' OR 비고 LIKE '%광센서%' 
                                        THEN '센서관련'
                                    WHEN 비고 LIKE '%금형 미대기%' OR 비고 LIKE '%차기금형%' OR 비고 LIKE '%금형대기%' 
                                        THEN '금형 미대기'
                                    WHEN 비고 LIKE '%금형%' OR 비고 LIKE '%청소%' OR 비고 LIKE '%사상%' 
                                        THEN '금형/청소'
                                    WHEN 비고 LIKE '%쿠션압%' 
                                        THEN '쿠션압'
                                    WHEN 비고 LIKE '%PLT%' 
                                        THEN 'PLT 교체'
                                    WHEN 비고 LIKE '%실수%' OR 비고 LIKE '%오기입%' OR 비고 LIKE '%보전%' 
                                        THEN '작업자/관리'
                                    WHEN 비고 LIKE '%QDC%' OR 비고 LIKE '%후진불%'  
                                        THEN 'QDC 확인'
                                    WHEN 비고 LIKE '%ATC%' 
                                        THEN 'ATC 불량'
                                    WHEN 비고 LIKE '%컨베어%' 
                                        THEN '컨베어 이상'

                                    -- 빈 값 처리
                                    WHEN 비고 IS NULL OR 비고 = '' OR 비고 = '-' 
                                        THEN '(없음)'

                                    ELSE '기타'
                                END AS 조치카테고리,
                                `비가동(분)`
                            FROM {T}
                            WHERE (:workplace IS NULL OR `작업장` = :workplace)
                            AND (:itemCode  IS NULL OR `자재번호` = :itemCode)
                            AND (:start_work_date IS NULL OR `근무일자` >= :start_work_date)
                            AND (:end_work_date   IS NULL OR `근무일자` <= :end_work_date)
                            AND (비고 IS NOT NULL AND 비고 <> '' AND 비고 <> '-')
                        ) t
                        GROUP BY 조치카테고리
                        ORDER BY minutes DESC
                        LIMIT :limit;
                    """)
            rows = db.execute(sql, {**req.dict(), "limit": limit}).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    def get_facility_item_downtime_agg(self, req: DowntimeGridResquest):
        db: Session = next(get_db())
        try:
            sql = text("""
                SELECT
                    base.downtime_name,
                    COUNT(*)                                   AS cnt,
                    SUM(base.minutes)                           AS total_minutes,
                    ROUND(AVG(NULLIF(base.minutes, 0)))         AS expected_minutes
                FROM (
                    SELECT
                        /* ↓ 여기 컬럼명을 '비가동명' 또는 실제 있는 컬럼명(예: '비가동')으로 하나만 쓰세요 */
                        a.`비가동명`                                   AS downtime_name,
                        CAST(COALESCE(a.`비가동(분)`, 0) AS DECIMAL(10,2)) AS minutes
                    FROM `AJIN_newDB`.`비가동시간 및 현황` AS a
                    JOIN `AJIN_newDB`.`금형고장내역` AS b
                    ON DATE(a.`근무일자`) = DATE(b.`기본시작일`)
                    AND a.`자재번호` COLLATE utf8mb4_general_ci
                        = SUBSTRING_INDEX(SUBSTRING_INDEX(b.`설비내역`, ' ', 2), ' ', -1) COLLATE utf8mb4_general_ci
                    WHERE (:workplace IS NULL OR :workplace = '' OR a.`작업장` = :workplace)
                    AND (:itemCode  IS NULL OR :itemCode  = '' OR a.`자재번호` = :itemCode)
                    AND (:start_work_date IS NULL OR a.`근무일자` >= :start_work_date)
                    AND (:end_work_date   IS NULL OR a.`근무일자` <= :end_work_date)
                ) AS base
                GROUP BY base.downtime_name
                ORDER BY cnt DESC, downtime_name ASC;
            """)

            rows = [dict(r) for r in db.execute(sql, req.dict()).mappings().all()]
            return rows
        finally:
            db.close()

    def get_facility_line_downtime_agg(self, req: DowntimeGridResquest):
        db: Session = next(get_db())
        try:
            sql = text("""
                SELECT
                    base.downtime_name,
                    COUNT(*)                                   AS cnt,
                    SUM(base.minutes)                           AS total_minutes,
                    ROUND(AVG(NULLIF(base.minutes, 0)))         AS expected_minutes
                FROM (
                    SELECT
                        /* ↓ 여기 컬럼명을 '비가동명' 또는 실제 있는 컬럼명(예: '비가동')으로 하나만 쓰세요 */
                        a.`비가동명`                                   AS downtime_name,
                        CAST(COALESCE(a.`비가동(분)`, 0) AS DECIMAL(10,2)) AS minutes
                    FROM `AJIN_newDB`.`비가동시간 및 현황` AS a
                    JOIN `AJIN_newDB`.`금형고장내역` AS b
                    ON DATE(a.`근무일자`) = DATE(b.`기본시작일`)
                    AND a.`자재번호` COLLATE utf8mb4_general_ci
                        = SUBSTRING_INDEX(SUBSTRING_INDEX(b.`설비내역`, ' ', 2), ' ', -1) COLLATE utf8mb4_general_ci
                    WHERE (:workplace IS NULL OR :workplace = '' OR a.`작업장` = :workplace)
                    AND (:start_work_date IS NULL OR a.`근무일자` >= :start_work_date)
                    AND (:end_work_date   IS NULL OR a.`근무일자` <= :end_work_date)
                ) AS base
                GROUP BY base.downtime_name
                ORDER BY cnt DESC, downtime_name ASC;
            """)

            rows = [dict(r) for r in db.execute(sql, req.dict()).mappings().all()]
            return rows
        finally:
            db.close()


downtime_chart_service = Downtime_chart_service()