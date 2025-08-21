# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from datetime import datetime, timedelta
# from app.config.database import get_db

# class InspectionChartService:
#     TABLE = "`AJIN_newDB`.`검사내역`"

#     # WHERE 절 공통
#     def _build_where(self, req):
#         where, params = [], {}

#         def has(v):
#             if v is None: return False
#             if isinstance(v, str): return v.strip() != "" and v.strip().lower() != "string"
#             return True

#         if has(getattr(req, "start_date", None)):
#             where.append("DATE(`보고일`) >= :start_date"); params["start_date"] = req.start_date
#         if has(getattr(req, "end_date", None)):
#             where.append("DATE(`보고일`) <= :end_date"); params["end_date"] = req.end_date
#         if has(getattr(req, "factory", None)):
#             where.append("`공장` = :factory"); params["factory"] = req.factory
#         if has(getattr(req, "process", None)):
#             where.append("`공정` = :process"); params["process"] = req.process
#         if has(getattr(req, "workType", None)):
#             where.append("`작업구분` = :workType"); params["workType"] = req.workType
#         if has(getattr(req, "inspType", None)):
#             where.append("`검사구분` = :inspType"); params["inspType"] = req.inspType
#         if has(getattr(req, "partNo", None)):
#             where.append("`품번` LIKE :partNo"); params["partNo"] = f"%{req.partNo.strip()}%"
#         if has(getattr(req, "item", None)):
#             where.append("`검사항목명` LIKE :item"); params["item"] = f"%{req.item.strip()}%"

#         if not where: where.append("1=1")
#         return " AND ".join(where), params

#     # KPI
#     def get_kpis(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT
#                     COUNT(*) AS total_cnt,
#                     COUNT(DISTINCT `품번`) AS part_kinds,
#                     COUNT(DISTINCT `검사항목명`) AS item_kinds,
#                     COALESCE(SUM(`생산`), 0) AS prod_sum
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#             """
#             k = db.execute(text(sql), params).mappings().first() or {}
#             total      = int(k.get("total_cnt", 0) or 0)
#             part_kinds = int(k.get("part_kinds", 0) or 0)
#             item_kinds = int(k.get("item_kinds", 0) or 0)
#             prod_sum   = float(k.get("prod_sum", 0) or 0.0)

#             sql_insp = f"""
#                 SELECT `검사구분` AS type, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `검사구분`
#                 ORDER BY qty DESC
#             """
#             insp_rows = [dict(r) for r in db.execute(text(sql_insp), params).mappings().all()]

#             sql_work = f"""
#                 SELECT `작업구분` AS type, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `작업구분`
#                 ORDER BY qty DESC
#             """
#             work_rows = [dict(r) for r in db.execute(text(sql_work), params).mappings().all()]

#             # 일평균
#             sql_tr = f"""
#                 SELECT DATE(`보고일`) AS d, COUNT(*) AS c
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`보고일`)
#             """
#             days = db.execute(text(sql_tr), params).mappings().all()
#             daily_avg = round(sum(int(r["c"]) for r in days) / len(days), 2) if days else 0.0

#             intensity_per_k = round(total / (prod_sum / 1000.0), 3) if prod_sum > 0 else 0.0

#             return {
#                 "total": total,
#                 "partKinds": part_kinds,
#                 "itemKinds": item_kinds,
#                 "dailyAvg": daily_avg,
#                 "prodSum": prod_sum,
#                 "intensityPerK": intensity_per_k,
#                 "byInspType": insp_rows,
#                 "byWorkType": work_rows,
#             }
#         finally:
#             db.close()

#     # 검사항목 Top N
#     def get_by_item(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             top_n = getattr(req, "topN", 5) or 5
#             sql = f"""
#                 SELECT `검사항목명` AS item, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `검사항목명`
#                 ORDER BY qty DESC
#                 LIMIT :top_n
#             """
#             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
#             return [dict(r) for r in rows]
#         finally:
#             db.close()

#     # 일자별 검사 건수 추이
#     def get_trend(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DATE(`보고일`) AS d, COUNT(*) AS cnt
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`보고일`)
#                 ORDER BY d
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [{"date": str(r["d"]), "count": int(r["cnt"] or 0)} for r in rows]
#         finally:
#             db.close()

#     # 검사구분별 누적 추이
#     def get_stacked(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT
#                     DATE(`보고일`) AS d,
#                     SUM(CASE WHEN `검사구분` = '자동검사' THEN 1 ELSE 0 END) AS auto_cnt,
#                     SUM(CASE WHEN `검사구분` LIKE '자주%%' THEN 1 ELSE 0 END) AS self_cnt,
#                     SUM(CASE WHEN `검사구분` NOT IN ('자동검사') AND `검사구분` NOT LIKE '자주%%' THEN 1 ELSE 0 END) AS other_cnt
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`보고일`)
#                 ORDER BY d
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [
#                 {"date": str(r["d"]), "auto": int(r["auto_cnt"] or 0), "self": int(r["self_cnt"] or 0), "other": int(r["other_cnt"] or 0)}
#                 for r in rows
#             ]
#         finally:
#             db.close()

#     # 품번/공정/설비 Top N
#     def get_by_part(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             top_n = getattr(req, "topN", 5) or 5
#             sql = f"""
#                 SELECT `품번` AS partNo, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `품번`
#                 ORDER BY qty DESC
#                 LIMIT :top_n
#             """
#             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
#             return [dict(r) for r in rows]
#         finally:
#             db.close()

#     def get_by_process(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             top_n = getattr(req, "topN", 5) or 5
#             sql = f"""
#                 SELECT `공정` AS proc, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `공정`
#                 ORDER BY qty DESC
#                 LIMIT :top_n
#             """
#             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
#             return [dict(r) for r in rows]
#         finally:
#             db.close()

#     def get_by_machine(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             top_n = getattr(req, "topN", 5) or 5
#             sql = f"""
#                 SELECT `설비` AS machine, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `설비`
#                 ORDER BY qty DESC
#                 LIMIT :top_n
#             """
#             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
#             return [dict(r) for r in rows]
#         finally:
#             db.close()

#     # 스루풋
#     def get_throughput(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DATE(`보고일`) AS d,
#                        COUNT(*) AS cnt,
#                        COALESCE(SUM(`생산`), 0) AS prod
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`보고일`)
#                 ORDER BY d
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [{"date": str(r["d"]), "count": int(r["cnt"] or 0), "prod": float(r["prod"] or 0.0),
#                      "intensity": round((int(r["cnt"] or 0))/(float(r["prod"] or 0.0)/1000.0), 3) if float(r["prod"] or 0.0)>0 else 0.0}
#                     for r in rows]
#         finally:
#             db.close()

#     # 주/야
#     def get_shift(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DATE(`보고일`) AS d,
#                        SUM(CASE WHEN `주야구분` = '주간' THEN 1 ELSE 0 END) AS day_cnt,
#                        SUM(CASE WHEN `주야구분` = '야간' THEN 1 ELSE 0 END) AS night_cnt
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`보고일`)
#                 ORDER BY d
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [{"date": str(r["d"]), "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)} for r in rows]
#         finally:
#             db.close()

#     # 모멘텀/요일/강도/불균형/이상치/집중도 (기존 그대로)
#     def get_momentum_parts(self, req):
#         db: Session = next(get_db())
#         try:
#             end_str = getattr(req, "end_date", None)
#             end_dt = datetime.strptime(end_str, "%Y-%m-%d") if end_str else datetime.utcnow()
#             recent_start = (end_dt - timedelta(days=14)).date()
#             prev_start   = (end_dt - timedelta(days=28)).date()
#             prev_end     = (end_dt - timedelta(days=14)).date()

#             where_sql, params = self._build_where(req)
#             sql_recent = f"""
#                 SELECT `품번` AS partNo, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND DATE(`보고일`) > :recent_start AND DATE(`보고일`) <= :end_date_cut
#                 GROUP BY `품번`
#             """
#             recent = db.execute(text(sql_recent), {**params, "recent_start": str(recent_start), "end_date_cut": end_dt.date().isoformat()}).mappings().all()
#             rmap = {r["partNo"]: int(r["qty"] or 0) for r in recent}

#             sql_prev = f"""
#                 SELECT `품번` AS partNo, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND DATE(`보고일`) >= :prev_start AND DATE(`보고일`) <= :prev_end
#                 GROUP BY `품번`
#             """
#             prev = db.execute(text(sql_prev), {**params, "prev_start": str(prev_start), "prev_end": str(prev_end)}).mappings().all()
#             pmap = {r["partNo"]: int(r["qty"] or 0) for r in prev}

#             out, keys = [], set(rmap.keys()) | set(pmap.keys())
#             for k in keys:
#                 rv, pv = rmap.get(k, 0), pmap.get(k, 0)
#                 delta = rv - pv
#                 growth = round((rv / pv - 1) * 100.0, 1) if pv > 0 else (100.0 if rv > 0 else 0.0)
#                 out.append({"partNo": k, "recent": rv, "prev": pv, "delta": delta, "growthPct": growth})

#             top_n = getattr(req, "topN", 5) or 5
#             out.sort(key=lambda x: (x["delta"], x["recent"]), reverse=True)
#             return out[:top_n]
#         finally:
#             db.close()

#     def get_weekday_profile(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DAYOFWEEK(`보고일`) AS dow,
#                        COUNT(*) AS total,
#                        SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
#                        SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DAYOFWEEK(`보고일`)
#                 ORDER BY dow
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [{"dow": int(r["dow"]), "total": int(r["total"] or 0),
#                      "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)} for r in rows]
#         finally:
#             db.close()

#     def get_intensity_by_process(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             top_n = getattr(req, "topN", 5) or 5
#             sql = f"""
#                 SELECT t.proc, t.cnt, t.prod,
#                        CASE WHEN t.prod>0 THEN ROUND(t.cnt/(t.prod/1000.0),3) ELSE 0 END AS intensity
#                 FROM (
#                   SELECT `공정` AS proc, COUNT(*) AS cnt, COALESCE(SUM(`생산`),0) AS prod
#                   FROM {self.TABLE}
#                   WHERE {where_sql}
#                   GROUP BY `공정`
#                 ) t
#                 ORDER BY intensity DESC
#                 LIMIT :top_n
#             """
#             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
#             return [dict(r) for r in rows]
#         finally:
#             db.close()

#     def get_shift_imbalance_process(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT `공정` AS proc,
#                        SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
#                        SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
#                        COUNT(*) AS total
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `공정`
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             out = []
#             for r in rows:
#                 day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
#                 total = int(r["total"] or 0)
#                 ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
#                 imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
#                 out.append({"proc": r["proc"], "day": day, "night": night, "total": total,
#                             "ratioNightPerDay": ratio, "imbalance": imbalance})
#             top_n = getattr(req, "topN", 5) or 5
#             out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
#             return out[:top_n]
#         finally:
#             db.close()

#     # 설비 기준
#     def get_intensity_by_machine(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             top_n = getattr(req, "topN", 5) or 5
#             sql = f"""
#                 SELECT t.machine, t.cnt, t.prod,
#                        CASE WHEN t.prod>0 THEN ROUND(t.cnt/(t.prod/1000.0),3) ELSE 0 END AS intensity
#                 FROM (
#                   SELECT `설비` AS machine, COUNT(*) AS cnt, COALESCE(SUM(`생산`),0) AS prod
#                   FROM {self.TABLE}
#                   WHERE {where_sql}
#                   GROUP BY `설비`
#                 ) t
#                 ORDER BY intensity DESC
#                 LIMIT :top_n
#             """
#             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
#             return [dict(r) for r in rows]
#         finally:
#             db.close()

#     def get_shift_imbalance_machine(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT `설비` AS machine,
#                        SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
#                        SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
#                        COUNT(*) AS total
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `설비`
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             out = []
#             for r in rows:
#                 day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
#                 total = int(r["total"] or 0)
#                 ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
#                 imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
#                 out.append({"machine": r["machine"], "day": day, "night": night,
#                             "total": total, "ratioNightPerDay": ratio, "imbalance": imbalance})
#             top_n = getattr(req, "topN", 5) or 5
#             out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
#             return out[:top_n]
#         finally:
#             db.close()

#     # 이상치/집중도
#     def get_anomaly_days(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DATE(`보고일`) AS d, COUNT(*) AS c
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`보고일`)
#                 ORDER BY d
#             """
#             days = [dict(r) for r in db.execute(text(sql), params).mappings().all()]
#             if not days: return []
#             c_vals = [int(x["c"]) for x in days]
#             n = len(c_vals)
#             mean = sum(c_vals) / n
#             var = sum((x - mean) ** 2 for x in c_vals) / n
#             std = (var ** 0.5) if var > 0 else 0.0

#             out = []
#             for d in days:
#                 c = int(d["c"])
#                 z = (c - mean) / std if std > 0 else 0.0
#                 if z >= 2.0:
#                     out.append({"date": str(d["d"]), "count": c, "z": round(z, 2), "avg": round(mean, 2), "std": round(std, 2)})
#             out.sort(key=lambda x: x["z"], reverse=True)
#             return out[:10]
#         finally:
#             db.close()

#     def get_pareto_concentration(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             top_n = getattr(req, "topN", 5) or 5

#             sql_total = f"SELECT COUNT(*) AS c FROM {self.TABLE} WHERE {where_sql}"
#             total = int((db.execute(text(sql_total), params).scalar() or 0))

#             def share_by(col):
#                 sql_top = f"""
#                     SELECT SUM(cnt) FROM (
#                         SELECT COUNT(*) AS cnt
#                         FROM {self.TABLE}
#                         WHERE {where_sql}
#                         GROUP BY {col}
#                         ORDER BY cnt DESC
#                         LIMIT :top_n
#                     ) t
#                 """
#                 top_sum = int(db.execute(text(sql_top), {**params, "top_n": top_n}).scalar() or 0)
#                 pct = round((top_sum / total) * 100.0, 2) if total > 0 else 0.0
#                 return {"topSum": top_sum, "total": total, "sharePct": pct}

#             return {"part": share_by("`품번`"), "item": share_by("`검사항목명`")}
#         finally:
#             db.close()

# inspection_chart_service = InspectionChartService()

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from app.config.database import get_db

class InspectionChartService:
    TABLE = "`AJIN_newDB`.`검사내역`"

    # WHERE 절 공통
    def _build_where(self, req):
        where, params = [], {}

        def has(v):
            if v is None: return False
            if isinstance(v, str): return v.strip() != "" and v.strip().lower() != "string"
            return True

        if has(getattr(req, "start_date", None)):
            where.append("DATE(`보고일`) >= :start_date"); params["start_date"] = req.start_date
        if has(getattr(req, "end_date", None)):
            where.append("DATE(`보고일`) <= :end_date"); params["end_date"] = req.end_date
        if has(getattr(req, "factory", None)):
            where.append("`공장` = :factory"); params["factory"] = req.factory
        if has(getattr(req, "process", None)):
            where.append("`공정` = :process"); params["process"] = req.process
        if has(getattr(req, "workType", None)):
            where.append("`작업구분` = :workType"); params["workType"] = req.workType
        if has(getattr(req, "inspType", None)):
            where.append("`검사구분` = :inspType"); params["inspType"] = req.inspType
        if has(getattr(req, "partNo", None)):
            where.append("`품번` LIKE :partNo"); params["partNo"] = f"%{req.partNo.strip()}%"
        if has(getattr(req, "item", None)):
            where.append("`검사항목명` LIKE :item"); params["item"] = f"%{req.item.strip()}%"

        if not where: where.append("1=1")
        return " AND ".join(where), params

    # KPI
    def get_kpis(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT
                    COUNT(*) AS total_cnt,
                    COUNT(DISTINCT `품번`) AS part_kinds,
                    COUNT(DISTINCT `검사항목명`) AS item_kinds,
                    COALESCE(SUM(`생산`), 0) AS prod_sum
                FROM {self.TABLE}
                WHERE {where_sql}
            """
            k = db.execute(text(sql), params).mappings().first() or {}
            total      = int(k.get("total_cnt", 0) or 0)
            part_kinds = int(k.get("part_kinds", 0) or 0)
            item_kinds = int(k.get("item_kinds", 0) or 0)
            prod_sum   = float(k.get("prod_sum", 0) or 0.0)

            sql_insp = f"""
                SELECT `검사구분` AS type, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `검사구분`
                ORDER BY qty DESC
            """
            insp_rows = [dict(r) for r in db.execute(text(sql_insp), params).mappings().all()]

            sql_work = f"""
                SELECT `작업구분` AS type, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `작업구분`
                ORDER BY qty DESC
            """
            work_rows = [dict(r) for r in db.execute(text(sql_work), params).mappings().all()]

            # 일평균
            sql_tr = f"""
                SELECT DATE(`보고일`) AS d, COUNT(*) AS c
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`보고일`)
            """
            days = db.execute(text(sql_tr), params).mappings().all()
            daily_avg = round(sum(int(r["c"]) for r in days) / len(days), 2) if days else 0.0

            intensity_per_k = round(total / (prod_sum / 1000.0), 3) if prod_sum > 0 else 0.0

            return {
                "total": total,
                "partKinds": part_kinds,
                "itemKinds": item_kinds,
                "dailyAvg": daily_avg,
                "prodSum": prod_sum,
                "intensityPerK": intensity_per_k,
                "byInspType": insp_rows,
                "byWorkType": work_rows,
            }
        finally:
            db.close()

    # 검사항목 Top N
    def get_by_item(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 5) or 5
            sql = f"""
                SELECT `검사항목명` AS item, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `검사항목명`
                ORDER BY qty DESC
                LIMIT :top_n
            """
            rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    # 일자별 검사 건수 추이
    def get_trend(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DATE(`보고일`) AS d, COUNT(*) AS cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`보고일`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [{"date": str(r["d"]), "count": int(r["cnt"] or 0)} for r in rows]
        finally:
            db.close()

    # 검사구분별 누적 추이
    def get_stacked(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT
                    DATE(`보고일`) AS d,
                    SUM(CASE WHEN `검사구분` = '자동검사' THEN 1 ELSE 0 END) AS auto_cnt,
                    SUM(CASE WHEN `검사구분` LIKE '자주%%' THEN 1 ELSE 0 END) AS self_cnt,
                    SUM(CASE WHEN `검사구분` NOT IN ('자동검사') AND `검사구분` NOT LIKE '자주%%' THEN 1 ELSE 0 END) AS other_cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`보고일`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [
                {"date": str(r["d"]), "auto": int(r["auto_cnt"] or 0), "self": int(r["self_cnt"] or 0), "other": int(r["other_cnt"] or 0)}
                for r in rows
            ]
        finally:
            db.close()

    # 품번/공정/설비 Top N
    def get_by_part(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 5) or 5
            sql = f"""
                SELECT `품번` AS partNo, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `품번`
                ORDER BY qty DESC
                LIMIT :top_n
            """
            rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    def get_by_process(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 5) or 5
            sql = f"""
                SELECT `공정` AS proc, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `공정`
                ORDER BY qty DESC
                LIMIT :top_n
            """
            rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    def get_by_machine(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 5) or 5
            sql = f"""
                SELECT `설비` AS machine, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `설비`
                ORDER BY qty DESC
                LIMIT :top_n
            """
            rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    # 스루풋
    def get_throughput(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DATE(`보고일`) AS d,
                       COUNT(*) AS cnt,
                       COALESCE(SUM(`생산`), 0) AS prod
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`보고일`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [{"date": str(r["d"]), "count": int(r["cnt"] or 0), "prod": float(r["prod"] or 0.0),
                     "intensity": round((int(r["cnt"] or 0))/(float(r["prod"] or 0.0)/1000.0), 3) if float(r["prod"] or 0.0)>0 else 0.0}
                    for r in rows]
        finally:
            db.close()

    # 주/야
    def get_shift(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DATE(`보고일`) AS d,
                       SUM(CASE WHEN `주야구분` = '주간' THEN 1 ELSE 0 END) AS day_cnt,
                       SUM(CASE WHEN `주야구분` = '야간' THEN 1 ELSE 0 END) AS night_cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`보고일`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [{"date": str(r["d"]), "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)} for r in rows]
        finally:
            db.close()

    # 모멘텀/요일/강도/불균형/이상치/집중도
    def get_momentum_parts(self, req):
        db: Session = next(get_db())
        try:
            end_str = getattr(req, "end_date", None)
            end_dt = datetime.strptime(end_str, "%Y-%m-%d") if end_str else datetime.utcnow()
            recent_start = (end_dt - timedelta(days=14)).date()
            prev_start   = (end_dt - timedelta(days=28)).date()
            prev_end     = (end_dt - timedelta(days=14)).date()

            where_sql, params = self._build_where(req)
            sql_recent = f"""
                SELECT `품번` AS partNo, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql} AND DATE(`보고일`) > :recent_start AND DATE(`보고일`) <= :end_date_cut
                GROUP BY `품번`
            """
            recent = db.execute(text(sql_recent), {**params, "recent_start": str(recent_start), "end_date_cut": end_dt.date().isoformat()}).mappings().all()
            rmap = {r["partNo"]: int(r["qty"] or 0) for r in recent}

            sql_prev = f"""
                SELECT `품번` AS partNo, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql} AND DATE(`보고일`) >= :prev_start AND DATE(`보고일`) <= :prev_end
                GROUP BY `품번`
            """
            prev = db.execute(text(sql_prev), {**params, "prev_start": str(prev_start), "prev_end": str(prev_end)}).mappings().all()
            pmap = {r["partNo"]: int(r["qty"] or 0) for r in prev}

            out, keys = [], set(rmap.keys()) | set(pmap.keys())
            for k in keys:
                rv, pv = rmap.get(k, 0), pmap.get(k, 0)
                delta = rv - pv
                growth = round((rv / pv - 1) * 100.0, 1) if pv > 0 else (100.0 if rv > 0 else 0.0)
                out.append({"partNo": k, "recent": rv, "prev": pv, "delta": delta, "growthPct": growth})

            top_n = getattr(req, "topN", 5) or 5
            out.sort(key=lambda x: (x["delta"], x["recent"]), reverse=True)
            return out[:top_n]
        finally:
            db.close()

    def get_weekday_profile(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DAYOFWEEK(`보고일`) AS dow,
                       COUNT(*) AS total,
                       SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
                       SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DAYOFWEEK(`보고일`)
                ORDER BY dow
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [{"dow": int(r["dow"]), "total": int(r["total"] or 0),
                     "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)} for r in rows]
        finally:
            db.close()

    def get_intensity_by_process(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 5) or 5
            sql = f"""
                SELECT t.proc, t.cnt, t.prod,
                       CASE WHEN t.prod>0 THEN ROUND(t.cnt/(t.prod/1000.0),3) ELSE 0 END AS intensity
                FROM (
                  SELECT `공정` AS proc, COUNT(*) AS cnt, COALESCE(SUM(`생산`),0) AS prod
                  FROM {self.TABLE}
                  WHERE {where_sql}
                  GROUP BY `공정`
                ) t
                ORDER BY intensity DESC
                LIMIT :top_n
            """
            rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    def get_shift_imbalance_process(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT `공정` AS proc,
                       SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
                       SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
                       COUNT(*) AS total
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `공정`
            """
            rows = db.execute(text(sql), params).mappings().all()
            out = []
            for r in rows:
                day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
                total = int(r["total"] or 0)
                ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
                imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
                out.append({"proc": r["proc"], "day": day, "night": night, "total": total,
                            "ratioNightPerDay": ratio, "imbalance": imbalance})
            top_n = getattr(req, "topN", 5) or 5
            out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
            return out[:top_n]
        finally:
            db.close()

    # 설비 기준
    def get_intensity_by_machine(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 5) or 5
            sql = f"""
                SELECT t.machine, t.cnt, t.prod,
                       CASE WHEN t.prod>0 THEN ROUND(t.cnt/(t.prod/1000.0),3) ELSE 0 END AS intensity
                FROM (
                  SELECT `설비` AS machine, COUNT(*) AS cnt, COALESCE(SUM(`생산`),0) AS prod
                  FROM {self.TABLE}
                  WHERE {where_sql}
                  GROUP BY `설비`
                ) t
                ORDER BY intensity DESC
                LIMIT :top_n
            """
            rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    def get_shift_imbalance_machine(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT `설비` AS machine,
                       SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
                       SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
                       COUNT(*) AS total
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `설비`
            """
            rows = db.execute(text(sql), params).mappings().all()
            out = []
            for r in rows:
                day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
                total = int(r["total"] or 0)
                ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
                imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
                out.append({"machine": r["machine"], "day": day, "night": night,
                            "total": total, "ratioNightPerDay": ratio, "imbalance": imbalance})
            top_n = getattr(req, "topN", 5) or 5
            out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
            return out[:top_n]
        finally:
            db.close()

    # 이상치/집중도
    def get_anomaly_days(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DATE(`보고일`) AS d, COUNT(*) AS c
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`보고일`)
                ORDER BY d
            """
            days = [dict(r) for r in db.execute(text(sql), params).mappings().all()]
            if not days: return []
            c_vals = [int(x["c"]) for x in days]
            n = len(c_vals)
            mean = sum(c_vals) / n
            var = sum((x - mean) ** 2 for x in c_vals) / n
            std = (var ** 0.5) if var > 0 else 0.0

            out = []
            for d in days:
                c = int(d["c"])
                z = (c - mean) / std if std > 0 else 0.0
                if z >= 2.0:
                    out.append({"date": str(d["d"]), "count": c, "z": round(z, 2), "avg": round(mean, 2), "std": round(std, 2)})
            out.sort(key=lambda x: x["z"], reverse=True)
            return out[:10]
        finally:
            db.close()

    def get_pareto_concentration(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 5) or 5

            sql_total = f"SELECT COUNT(*) AS c FROM {self.TABLE} WHERE {where_sql}"
            total = int((db.execute(text(sql_total), params).scalar() or 0))

            def share_by(col):
                sql_top = f"""
                    SELECT SUM(cnt) FROM (
                        SELECT COUNT(*) AS cnt
                        FROM {self.TABLE}
                        WHERE {where_sql}
                        GROUP BY {col}
                        ORDER BY cnt DESC
                        LIMIT :top_n
                    ) t
                """
                top_sum = int(db.execute(text(sql_top), {**params, "top_n": top_n}).scalar() or 0)
                pct = round((top_sum / total) * 100.0, 2) if total > 0 else 0.0
                return {"topSum": top_sum, "total": total, "sharePct": pct}

            return {"part": share_by("`품번`"), "item": share_by("`검사항목명`")}
        finally:
            db.close()

    # -------------------------------
    # ✅ 드롭다운 옵션 (누락분 추가)
    # -------------------------------
    def list_factories(self, req):
        """기간 조건만 반영해서 공장 목록 조회"""
        db: Session = next(get_db())
        try:
            # 프론트가 start/end만 보내지만, 혹시 모를 다른 필터는 무시하고 날짜만 사용
            where = []
            params = {}
            if getattr(req, "start_date", None):
                where.append("DATE(`보고일`) >= :start_date"); params["start_date"] = req.start_date
            if getattr(req, "end_date", None):
                where.append("DATE(`보고일`) <= :end_date"); params["end_date"] = req.end_date
            if not where: where.append("1=1")
            where_sql = " AND ".join(where)

            sql = f"""
                SELECT DISTINCT `공장` AS v
                FROM {self.TABLE}
                WHERE {where_sql} AND `공장` IS NOT NULL AND `공장` <> ''
                ORDER BY v
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [r["v"] for r in rows]
        finally:
            db.close()

    def list_processes(self, req):
        """선택된 상위 필터(공장 등)를 반영해서 공정 목록 조회"""
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DISTINCT `공정` AS v
                FROM {self.TABLE}
                WHERE {where_sql} AND `공정` IS NOT NULL AND `공정` <> ''
                ORDER BY v
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [r["v"] for r in rows]
        finally:
            db.close()

    def list_parts(self, req):
        """선택된 상위 필터(공장/공정 등)를 반영해서 품번 목록 조회"""
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DISTINCT `품번` AS v
                FROM {self.TABLE}
                WHERE {where_sql} AND `품번` IS NOT NULL AND `품번` <> ''
                ORDER BY v
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [r["v"] for r in rows]
        finally:
            db.close()

    def list_items(self, req):
        """선택된 상위 필터(공장/공정/품번 등)를 반영해서 검사항목 목록 조회"""
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DISTINCT `검사항목명` AS v
                FROM {self.TABLE}
                WHERE {where_sql} AND `검사항목명` IS NOT NULL AND `검사항목명` <> ''
                ORDER BY v
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [r["v"] for r in rows]
        finally:
            db.close()

inspection_chart_service = InspectionChartService()
