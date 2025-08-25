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

    # -------------------- KPI 요약 --------------------
    def get_summary(self, req: DowntimeGridResquest):
        db: Session = next(get_db())
        try:
            sql_sum = text(f"""
                SELECT
                  COALESCE(SUM(COALESCE(`비가동(분)`,0)),0) AS total,
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
            }).mappings().first() or {"total":0, "count":0, "avg":0}

            sql_top = text(f"""
                SELECT x.`비가동명` AS topName, x.minutes AS topValue
                FROM (
                  SELECT `비가동명`, SUM(COALESCE(`비가동(분)`,0)) AS minutes
                  FROM {T}
                  WHERE (:workplace IS NULL OR `작업장` = :workplace)
                    AND (:start_work_date IS NULL OR `근무일자` >= :start_work_date)
                    AND (:end_work_date   IS NULL OR `근무일자` <= :end_work_date)
                  GROUP BY `비가동명`
                  ORDER BY minutes DESC
                  LIMIT 1
                ) x;
            """)
            trow = db.execute(sql_top, {
                "workplace": req.workplace,
                "start_work_date": req.start_work_date,
                "end_work_date": req.end_work_date
            }).mappings().first() or {"topName":"-", "topValue":0}

            return {
                "total": float(srow["total"] or 0),
                "count": int(srow["count"] or 0),
                "avg":   float(srow["avg"]   or 0),
                "topName": trow["topName"] or "-",
                "topValue": float(trow["topValue"] or 0),
            }
        finally:
            db.close()

    # -------------------- 월별 합계 --------------------
    def get_monthly(self, req: DowntimeGridResquest):
        db: Session = next(get_db())
        try:
            sql = text(f"""
                SELECT DATE_FORMAT(`근무일자`, '%Y-%m') AS ym,
                       SUM(COALESCE(`비가동(분)`,0)) AS minutes
                FROM {T}
                WHERE (:workplace IS NULL OR `작업장` = :workplace)
                  AND (:itemCode  IS NULL OR `자재번호` = :itemCode)
                  AND (:start_work_date IS NULL OR `근무일자` >= :start_work_date)
                  AND (:end_work_date   IS NULL OR `근무일자` <= :end_work_date)
                GROUP BY DATE_FORMAT(`근무일자`, '%Y-%m')
                ORDER BY ym;
            """)
            rows = db.execute(sql, req.dict()).mappings().all()
            return [dict(r) for r in rows]
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
            if top and len(rows) > top and withOthers:
                top_rows = rows[:top]
                others = sum(r["minutes"] for r in rows[top:])
                top_rows.append({"label":"기타", "minutes": others})
                return top_rows
            return rows[:top] if top else rows
        finally:
            db.close()

    # -------------------- 비고 Top --------------------
    def get_top_notes(self, req: DowntimeGridResquest, limit:int=10):
        db: Session = next(get_db())
        try:
            sql = text(f"""
                SELECT COALESCE(`비고`,'(빈 값)') AS text,
                       COUNT(*) AS count,
                       SUM(COALESCE(`비가동(분)`,0)) AS minutes
                FROM {T}
                WHERE (:workplace IS NULL OR `작업장` = :workplace)
                  AND (:itemCode  IS NULL OR `자재번호` = :itemCode)
                  AND (:start_work_date IS NULL OR `근무일자` >= :start_work_date)
                  AND (:end_work_date   IS NULL OR `근무일자` <= :end_work_date)
                GROUP BY COALESCE(`비고`,'(빈 값)')
                ORDER BY count DESC
                LIMIT :limit;
            """)
            rows = db.execute(sql, {**req.dict(), "limit": limit}).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

downtime_chart_service = Downtime_chart_service()
