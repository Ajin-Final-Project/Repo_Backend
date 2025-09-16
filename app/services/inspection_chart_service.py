# # from sqlalchemy.orm import Session
# # from sqlalchemy import text
# # from datetime import datetime, timedelta
# # from app.config.database import get_db
# # import re


# # class InspectionChartService:
# #     # ✅ 실제 테이블
# #     SCHEMA = "AJIN_newDB"
# #     TBL = "생산_검사"
# #     TABLE = "`AJIN_newDB`.`생산_검사`"

# #     # ---- 내부 캐시 ----
# #     _cache = {}

# #     # ---------- 컬럼 존재/선택 ----------
# #     def _col_exists(self, db: Session, col: str) -> bool:
# #         key = f"exists::{col}"
# #         if key in self._cache:
# #             return self._cache[key]
# #         sql = """
# #             SELECT 1
# #             FROM INFORMATION_SCHEMA.COLUMNS
# #             WHERE TABLE_SCHEMA = :s AND TABLE_NAME = :t AND COLUMN_NAME = :c
# #             LIMIT 1
# #         """
# #         ok = db.execute(text(sql), {"s": self.SCHEMA, "t": self.TBL, "c": col}).first() is not None
# #         self._cache[key] = ok
# #         return ok

# #     def _pick_col(self, db: Session, candidates) -> str | None:
# #         key = f"pick::{','.join(candidates)}"
# #         if key in self._cache:
# #             return self._cache[key]
# #         for c in candidates:
# #             if self._col_exists(db, c):
# #                 self._cache[key] = f"`{c}`"
# #                 return self._cache[key]
# #         self._cache[key] = None
# #         return None

# #     def _value_col(self, db: Session) -> str:
# #         """Xn에 표시할 '값' 컬럼 자동 선택 (✅ '생산' 최우선)"""
# #         key = "value_col"
# #         if key in self._cache:
# #             return self._cache[key]
# #         sql = """
# #             SELECT COLUMN_NAME
# #             FROM INFORMATION_SCHEMA.COLUMNS
# #             WHERE TABLE_SCHEMA = :s AND TABLE_NAME = :t
# #               AND COLUMN_NAME IN ('생산','검사값','측정값','결과값','값','측정치','측정결과')
# #             ORDER BY FIELD(COLUMN_NAME,'생산','검사값','측정값','결과값','값','측정치','측정결과')
# #             LIMIT 1
# #         """
# #         row = db.execute(text(sql), {"s": self.SCHEMA, "t": self.TBL}).first()
# #         if row and row[0]:
# #             self._cache[key] = f"`{row[0]}`"
# #         else:
# #             # 기본값도 '생산' 우선
# #             self._cache[key] = "`생산`" if self._col_exists(db, "생산") else (
# #                 "`검사값`" if self._col_exists(db, "검사값") else "NULL"
# #             )
# #         return self._cache[key]

# #     # ---------- WHERE ----------
# #     def _build_where(self, req):
# #         where, params = [], {}

# #         def has(v):
# #             if v is None:
# #                 return False
# #             if isinstance(v, str):
# #                 s = v.strip()
# #                 return s != "" and s.lower() != "string"
# #             return True

# #         if has(getattr(req, "start_date", None)):
# #             where.append("`work_date` >= :start_date")
# #             params["start_date"] = req.start_date
# #         if has(getattr(req, "end_date", None)):
# #             where.append("`work_date` < DATE_ADD(:end_date, INTERVAL 1 DAY)")
# #             params["end_date"] = req.end_date

# #         if has(getattr(req, "factory", None)):
# #             where.append("`plant` = :factory")
# #             params["factory"] = req.factory
# #         if has(getattr(req, "process", None)):
# #             where.append("`process` = :process")
# #             params["process"] = req.process
# #         if has(getattr(req, "equipment", None)):
# #             where.append("`equipment` = :equipment")
# #             params["equipment"] = req.equipment
# #         if has(getattr(req, "workType", None)):
# #             where.append("`작업구분` = :workType")
# #             params["workType"] = req.workType
# #         if has(getattr(req, "inspType", None)):
# #             where.append("`검사구분` = :inspType")
# #             params["inspType"] = req.inspType
# #         if has(getattr(req, "shiftType", None)):
# #             where.append("`주야구분` = :shiftType")
# #             params["shiftType"] = req.shiftType
# #         if has(getattr(req, "partNo", None)):
# #             where.append("`자재번호` LIKE :partNo")
# #             params["partNo"] = f"%{req.partNo.strip()}%"

# #         # 품명(=자재명)
# #         part_name = getattr(req, "partName", None) or getattr(req, "item", None)
# #         if has(part_name):
# #             params["partName"] = f"%{part_name.strip()}%"
# #             where.append("`자재명` LIKE :partName")

# #         # 검사항목명
# #         inspect_item = getattr(req, "inspectItem", None)
# #         if has(inspect_item):
# #             params["inspectItem"] = f"%{inspect_item.strip()}%"
# #             where.append("`검사항목명` LIKE :inspectItem")

# #         if not where:
# #             where.append("1=1")
# #         return " AND ".join(where), params

# #     # =========================================================
# #     # A. 일자별 Xn 표 (주/야 헤더 + X1~Xn + 작업구분 라벨)
# #     # =========================================================
# #     def _short_work(self, s: str) -> str:
# #         if not s:
# #             return ""
# #         s = str(s)
# #         if s.startswith("초"):
# #             return "초"
# #         if s.startswith("중"):
# #             return "중"
# #         if s.startswith("종"):
# #             return "종"
# #         return s

# #     def get_xn_daily(self, req):
# #         """
# #         응답:
# #         {
# #           "cols": ["X1","X2",...],
# #           "days": ["YYYY-MM-DD", ...],
# #           "shifts": ["주간","야간", ...],
# #           "workHeaders": { "YYYY-MM-DD": { "주간": {"X1":"초",...}, "야간": {...} } },
# #           "tables": {
# #              "YYYY-MM-DD": [
# #                { "NO":1, "검사순번":1, "검사항목명":"...", "검사내용":"...",
# #                  "주간":{"X1":..., "X2":...}, "야간":{"X1":..., ...}, "평균": ... },
# #                ...
# #              ]
# #           },
# #           "dayList": [ { "d":"YYYY-MM-DD", "equipment":"...", "partNo":"..." }, ... ]  # ✅ 추가
# #         }
# #         """
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)

# #             # 동적 컬럼
# #             date_col = "`work_date`"
# #             item_col = "`검사항목명`" if self._col_exists(db, "검사항목명") else None

# #             # spec(검사내용) 후보
# #             spec_col = None
# #             for c in ["검사내용", "기준", "규격", "판정기준", "상세", "내용", "비고"]:
# #                 if self._col_exists(db, c):
# #                     spec_col = f"`{c}`"
# #                     break

# #             # 작업순번(=Xn 시퀀스)
# #             step_col = None
# #             for c in ["작업순번", "op_seq", "seq", "검사순번", "검사순서"]:
# #                 if self._col_exists(db, c):
# #                     step_col = f"`{c}`"
# #                     break
# #             if not step_col:
# #                 step_col = "1"

# #             # 검사순번(행 정렬용)
# #             insp_col = None
# #             for c in ["검사순번", "검사순서", "insp_seq"]:
# #                 if self._col_exists(db, c):
# #                     insp_col = f"`{c}`"
# #                     break

# #             shift_col = "`주야구분`" if self._col_exists(db, "주야구분") else "''"
# #             work_col = "`작업구분`" if self._col_exists(db, "작업구분") else "NULL"

# #             val_col = self._value_col(db)

# #             # 보고일 목록
# #             sql_days = f"""
# #                 SELECT DATE({date_col}) AS d
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY DATE({date_col})
# #                 ORDER BY d
# #             """
# #             days = [str(r["d"]) for r in db.execute(text(sql_days), params).mappings().all()]

# #             # ✅ 날짜별 대표 설비/품번(최빈값; 없으면 NULL)
# #             sql_day_meta = f"""
# #                 WITH b AS (
# #                     SELECT DATE({date_col}) AS d,
# #                            COALESCE(`equipment`,'') AS eq,
# #                            COALESCE(`자재번호`,'')  AS part
# #                     FROM {self.TABLE}
# #                     WHERE {where_sql}
# #                 ),
# #                 eqm AS (
# #                     SELECT d, eq,
# #                            ROW_NUMBER() OVER (PARTITION BY d ORDER BY COUNT(*) DESC, eq) AS rn
# #                     FROM b WHERE eq <> ''
# #                     GROUP BY d, eq
# #                 ),
# #                 pm AS (
# #                     SELECT d, part,
# #                            ROW_NUMBER() OVER (PARTITION BY d ORDER BY COUNT(*) DESC, part) AS rn
# #                     FROM b WHERE part <> ''
# #                     GROUP BY d, part
# #                 )
# #                 SELECT x.d,
# #                        (SELECT eq   FROM eqm WHERE eqm.d = x.d AND eqm.rn = 1)   AS equipment,
# #                        (SELECT part FROM pm  WHERE pm.d  = x.d AND pm.rn  = 1)   AS partNo
# #                 FROM (SELECT DISTINCT d FROM b) x
# #                 ORDER BY x.d
# #             """
# #             day_list_rows = db.execute(text(sql_day_meta), params).mappings().all()
# #             day_list = [{"d": str(r["d"]), "equipment": r["equipment"], "partNo": r["partNo"]} for r in day_list_rows]

# #             # Xn 최대(상한 10)
# #             sql_n = f"SELECT COUNT(DISTINCT {step_col}) FROM {self.TABLE} WHERE {where_sql}"
# #             max_n = int(db.execute(text(sql_n), params).scalar() or 0)
# #             max_n = min(max_n if max_n > 0 else 1, 10)
# #             cols = [f"X{i}" for i in range(1, max_n + 1)]

# #             # spec/항목 없으면 빈 결과
# #             if not item_col:
# #                 return {"cols": cols, "days": days, "shifts": [], "workHeaders": {}, "tables": {}, "dayList": day_list}
# #             spec_expr = f"COALESCE({spec_col},'')" if spec_col else "''"
# #             item_expr = f"COALESCE({item_col},'')"

# #             # insp_seq 식
# #             insp_seq_expr = (
# #                 f"""
# #                 CASE
# #                   WHEN {insp_col} REGEXP '^[0-9]+$' THEN CAST({insp_col} AS UNSIGNED)
# #                   ELSE DENSE_RANK() OVER (
# #                          PARTITION BY DATE({date_col})
# #                          ORDER BY COALESCE({insp_col},''), {item_expr}, {spec_expr}
# #                        )
# #                 END
# #                 """ if insp_col else
# #                 f"DENSE_RANK() OVER (PARTITION BY DATE({date_col}) ORDER BY {item_expr}, {spec_expr})"
# #             )

# #             # 기본 집계(일자·항목·스펙·주야·seq)
# #             sql_agg = f"""
# #                 WITH base AS (
# #                   SELECT
# #                     DATE({date_col}) AS d,
# #                     {item_expr} AS item,
# #                     {spec_expr} AS spec,
# #                     COALESCE({shift_col},'') AS shift,
# #                     COALESCE({work_col},'')  AS work,
# #                     CAST({val_col} AS DECIMAL(20,6)) AS val,
# #                     CASE
# #                       WHEN {step_col} REGEXP '^[0-9]+$' THEN CAST({step_col} AS UNSIGNED)
# #                       ELSE DENSE_RANK() OVER (
# #                           PARTITION BY DATE({date_col}), {item_expr}, {spec_expr}, COALESCE({shift_col},'')
# #                           ORDER BY COALESCE({step_col},'')
# #                       )
# #                     END AS seq,
# #                     {insp_seq_expr} AS insp_no
# #                   FROM {self.TABLE}
# #                   WHERE {where_sql}
# #                 ),
# #                 agg AS (
# #                   SELECT d, item, spec, shift, seq, AVG(val) AS avg_val
# #                   FROM base
# #                   GROUP BY d, item, spec, shift, seq
# #                 ),
# #                 insp_min AS (
# #                   SELECT d, item, spec, MIN(insp_no) AS insp_no
# #                   FROM base
# #                   GROUP BY d, item, spec
# #                 ),
# #                 work_mode AS (
# #                   SELECT d, shift, seq, work,
# #                          ROW_NUMBER() OVER (PARTITION BY d, shift, seq ORDER BY COUNT(*) DESC, work) AS rn
# #                   FROM base
# #                   WHERE work IS NOT NULL AND work <> ''
# #                   GROUP BY d, shift, seq, work
# #                 )
# #                 SELECT a.d, a.item, a.spec, a.shift, a.seq, a.avg_val,
# #                        wm.work AS work_label,
# #                        im.insp_no
# #                 FROM agg a
# #                 LEFT JOIN work_mode wm
# #                   ON a.d = wm.d AND a.shift = wm.shift AND a.seq = wm.seq AND wm.rn = 1
# #                 LEFT JOIN insp_min im
# #                   ON a.d = im.d AND a.item = im.item AND a.spec = im.spec
# #                 ORDER BY a.d, im.insp_no, a.item, a.spec, a.shift, a.seq
# #             """
# #             recs = [dict(r) for r in db.execute(text(sql_agg), params).mappings().all()]

# #             # shifts 정렬(주간, 야간 우선)
# #             shift_order = []
# #             for r in recs:
# #                 s = r["shift"] or ""
# #                 if s not in shift_order:
# #                     shift_order.append(s)
# #             order_pref = ["주간", "야간"]
# #             shift_order.sort(key=lambda x: (order_pref.index(x) if x in order_pref else len(order_pref), x))

# #             # 일자별 헤더 라벨/테이블 구성
# #             work_headers = {}
# #             tables = {}

# #             # (d,item,spec) -> row
# #             rowmap = {}

# #             for r in recs:
# #                 d = str(r["d"])
# #                 item = (r["item"] or "").strip()
# #                 spec = (r["spec"] or "").strip()
# #                 shift = (r["shift"] or "").strip()
# #                 seq = int(r["seq"] or 0)
# #                 insp_no = int(r["insp_no"] or 0) if r["insp_no"] is not None else None
# #                 val = float(r["avg_val"]) if r["avg_val"] is not None else None
# #                 xn = f"X{seq}"
# #                 if seq < 1 or seq > max_n:
# #                     continue

# #                 if r.get("work_label"):
# #                     work_headers.setdefault(d, {}).setdefault(shift, {})[xn] = self._short_work(r["work_label"])

# #                 tables.setdefault(d, [])
# #                 key = (d, item, spec)
# #                 if key not in rowmap:
# #                     row = {"NO": 0, "검사항목명": item, "검사내용": spec, "검사순번": insp_no}
# #                     for s in shift_order:
# #                         row[s] = {}
# #                     row["평균"] = None
# #                     tables[d].append(row)
# #                     rowmap[key] = row
# #                 row = rowmap[key]
# #                 row["검사순번"] = insp_no if insp_no is not None else row.get("검사순번")
# #                 row.setdefault(shift, {})[xn] = val

# #             # 일자별 정렬(검사순번 asc) + NO/평균 계산
# #             for d in tables.keys():
# #                 tables[d].sort(
# #                     key=lambda rw: (
# #                         rw.get("검사순번") if rw.get("검사순번") is not None else 10**9,
# #                         rw.get("검사항목명") or "",
# #                         rw.get("검사내용") or "",
# #                     )
# #                 )
# #                 for idx, row in enumerate(tables[d], start=1):
# #                     row["NO"] = idx
# #                     vals = []
# #                     for s in shift_order:
# #                         for c in cols:
# #                             v = row.get(s, {}).get(c, None)
# #                             if v is not None:
# #                                 try:
# #                                     vals.append(float(v))
# #                                 except Exception:
# #                                     pass
# #                     row["평균"] = round(sum(vals) / len(vals), 6) if vals else None

# #             return {
# #                 "cols": cols,
# #                 "days": days,
# #                 "shifts": shift_order,
# #                 "workHeaders": work_headers,
# #                 "tables": tables,
# #                 "dayList": day_list,  # ✅ 좌측 패널용 메타
# #             }
# #         finally:
# #             db.close()

# #     # =========================================================
# #     # B. Xn 그룹 시리즈 (기존)
# #     # =========================================================
# #     def _normalize_group_by(self, gb: str):
# #         if not gb:
# #             return None
# #         m = {
# #             "partno": "`자재번호`",
# #             "part": "`자재번호`",
# #             "part_no": "`자재번호`",
# #             "partname": "`자재명`",
# #             "partName": "`자재명`",
# #             "shift": "`주야구분`",
# #             "shifttype": "`주야구분`",
# #             "shiftType": "`주야구분`",
# #             "insp": "`검사구분`",
# #             "insptype": "`검사구분`",
# #             "inspType": "`검사구분`",
# #             "item": "`검사항목명`",
# #             "spec": "`검사내용`",
# #         }
# #         return m.get(str(gb).replace(" ", "").lower())

# #     def get_xn_series(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             val_col = self._value_col(db)

# #             group_col = self._normalize_group_by(getattr(req, "groupBy", None))
# #             if not group_col:
# #                 return {"groupBy": None, "cols": [], "rows": []}
# #             if group_col == "`검사내용`":
# #                 spec = None
# #                 for c in ["검사내용", "기준", "규격", "판정기준", "상세", "내용", "비고"]:
# #                     if self._col_exists(db, c):
# #                         spec = f"`{c}`"
# #                         break
# #                 group_col = spec or "''"

# #             step_col = None
# #             for c in ["작업순번", "검사순번", "검사순서", "op_seq", "seq"]:
# #                 if self._col_exists(db, c):
# #                     step_col = f"`{c}`"
# #                     break
# #             if not step_col:
# #                 step_col = "1"

# #             sql_n = f"SELECT COUNT(DISTINCT {step_col}) FROM {self.TABLE} WHERE {where_sql}"
# #             max_n = int(db.execute(text(sql_n), params).scalar() or 0)
# #             max_n = min(max_n if max_n > 0 else 1, 20)
# #             cols = [f"X{i}" for i in range(1, max_n + 1)]
# #             top_n = getattr(req, "topN", 5) or 5

# #             sql_series = f"""
# #                 WITH base AS (
# #                     SELECT
# #                         {group_col} AS grp,
# #                         CAST({val_col} AS DECIMAL(20,6)) AS val,
# #                         {step_col} AS step_raw
# #                     FROM {self.TABLE}
# #                     WHERE {where_sql}
# #                 ),
# #                 topgrp AS (
# #                     SELECT grp
# #                     FROM base
# #                     WHERE grp IS NOT NULL AND grp <> ''
# #                     GROUP BY grp
# #                     ORDER BY COUNT(*) DESC
# #                     LIMIT :top_n
# #                 ),
# #                 ranked AS (
# #                     SELECT
# #                         b.grp,
# #                         CASE
# #                           WHEN b.step_raw REGEXP '^[0-9]+$' THEN CAST(b.step_raw AS UNSIGNED)
# #                           ELSE DENSE_RANK() OVER (PARTITION BY b.grp ORDER BY COALESCE(b.step_raw,''))
# #                         END AS seq,
# #                         b.val
# #                     FROM base b
# #                     JOIN topgrp t ON b.grp = t.grp
# #                 )
# #                 SELECT grp, seq, AVG(val) AS avg_val
# #                 FROM ranked
# #                 GROUP BY grp, seq
# #                 ORDER BY grp, seq
# #             """
# #             recs = [dict(r) for r in db.execute(text(sql_series), {**params, "top_n": top_n}).mappings().all()]

# #             series_map = {}
# #             for r in recs:
# #                 g = r["grp"]
# #                 n = int(r["seq"])
# #                 v = float(r["avg_val"]) if r["avg_val"] is not None else None
# #                 series_map.setdefault(g, {c: None for c in cols})
# #                 if 1 <= n <= max_n:
# #                     series_map[g][f"X{n}"] = v

# #             out_rows = [{"label": g, **series_map[g]} for g in series_map.keys()]
# #             return {"groupBy": group_col, "cols": cols, "rows": out_rows}
# #         finally:
# #             db.close()

# #     # =========================================================
# #     # C. 숫자형(실측값) 검사항목 — 일자별 추이
# #     # =========================================================
# #     def _parse_spec_numbers(self, s: str):
# #         if not s:
# #             return (None, None, None)
# #         try:
# #             txt = s.replace("㎜", "mm").replace("＋", "+").replace("－", "-").strip()

# #             m = re.search(r"([+-]?\d+(?:\.\d+)?)\s*±\s*([+-]?\d+(?:\.\d+)?)", txt)
# #             if m:
# #                 nom = float(m.group(1)); tol = float(m.group(2))
# #                 return (nom, nom - tol, nom + tol)

# #             m = re.search(r"([+-]?\d+(?:\.\d+)?)[^\d+-]+([+]\s*\d+(?:\.\d+)?)\s*mm?\s*이내", txt, re.IGNORECASE)
# #             if m:
# #                 nom = float(m.group(1)); up = float(m.group(2).replace("+",""))
# #                 return (nom, None, nom + up)

# #             m = re.search(r"([+-]?\d+(?:\.\d+)?)", txt)
# #             if m:
# #                 nom = float(m.group(1))
# #                 return (nom, None, None)
# #         except Exception:
# #             pass
# #         return (None, None, None)

# #     def get_numeric_trend(self, req):
# #         """
# #         스펙(텍스트)에 숫자가 포함된 (검사항목명, 스펙) TopN 대해 일자별 평균 실측값
# #         """
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             val_col = self._value_col(db)
# #             top_n = getattr(req, "topN", 5) or 5

# #             item_col = "`검사항목명`" if self._col_exists(db, "검사항목명") else None
# #             spec_col = None
# #             for c in ["검사내용", "기준", "규격", "판정기준", "상세", "내용", "비고"]:
# #                 if self._col_exists(db, c):
# #                     spec_col = f"`{c}`"
# #                     break
# #             if not (item_col and spec_col):
# #                 return {"dates": [], "series": []}

# #             sql_days = f"""
# #                 SELECT DATE(`work_date`) AS d
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql} AND {spec_col} REGEXP '[0-9]'
# #                 GROUP BY DATE(`work_date`)
# #                 ORDER BY d
# #             """
# #             days = [str(r["d"]) for r in db.execute(text(sql_days), params).mappings().all()]
# #             if not days:
# #                 return {"dates": [], "series": []}

# #             sql_avg = f"""
# #                 WITH base AS (
# #                   SELECT DATE(`work_date`) AS d,
# #                          COALESCE({item_col},'') AS item,
# #                          COALESCE({spec_col},'') AS spec,
# #                          CAST({val_col} AS DECIMAL(20,6)) AS val
# #                   FROM {self.TABLE}
# #                   WHERE {where_sql} AND {spec_col} REGEXP '[0-9]'
# #                 )
# #                 SELECT b.d, b.item, b.spec, AVG(b.val) AS avg_val
# #                 FROM base b
# #                 JOIN (
# #                     SELECT item, spec
# #                     FROM (
# #                       SELECT COALESCE({item_col},'') AS item,
# #                              COALESCE({spec_col},'') AS spec,
# #                              COUNT(*) AS c
# #                       FROM {self.TABLE}
# #                       WHERE {where_sql} AND {spec_col} REGEXP '[0-9]'
# #                       GROUP BY COALESCE({item_col},''), COALESCE({spec_col},'')
# #                       ORDER BY c DESC
# #                       LIMIT :top_n
# #                     ) t
# #                 ) tp ON b.item = tp.item AND b.spec = tp.spec
# #                 GROUP BY b.item, b.spec, b.d
# #                 ORDER BY b.item, b.spec, b.d
# #             """
# #             avg_rows = db.execute(text(sql_avg), {**params, "top_n": top_n}).mappings().all()

# #             # 레이블/값 매핑
# #             top_pairs = {}
# #             for r in avg_rows:
# #                 top_pairs[(r["item"], r["spec"])] = True

# #             label_map = {}
# #             val_map = {}
# #             for (item, spec) in top_pairs.keys():
# #                 item_s = (item or "").strip()
# #                 spec_s = (spec or "").strip()
# #                 label = f"{item_s} | {spec_s}" if spec_s else item_s
# #                 label_map[(item, spec)] = label
# #                 val_map[label] = {d: None for d in days}

# #             spec_nums = {}
# #             for (item, spec), label in label_map.items():
# #                 spec_nums[label] = self._parse_spec_numbers(spec)

# #             for r in avg_rows:
# #                 item = r["item"]
# #                 spec = r["spec"]
# #                 label = label_map.get((item, spec))
# #                 d = str(r["d"])
# #                 v = float(r["avg_val"]) if r["avg_val"] is not None else None
# #                 if label in val_map and d in val_map[label]:
# #                     val_map[label][d] = v

# #             series = []
# #             for label, dayvals in val_map.items():
# #                 series.append({
# #                     "label": label,
# #                     "data": [dayvals[d] for d in days],
# #                     "nominal": spec_nums.get(label, (None,None,None))[0],
# #                     "lsl": spec_nums.get(label, (None,None,None))[1],
# #                     "usl": spec_nums.get(label, (None,None,None))[2],
# #                 })

# #             return {"dates": days, "series": series}
# #         finally:
# #             db.close()

# #     # =========================================================
# #     # D. 기존 대시보드(생략 없이 유지)
# #     # =========================================================
# #     def get_dashboard(self, req):
# #         return {
# #             "kpis": self.get_kpis(req),
# #             "byItem": self.get_by_item(req),
# #             "trend": self.get_trend(req),
# #             "stacked": self.get_stacked(req),
# #             "byPart": self.get_by_part(req),
# #             "byProcess": self.get_by_process(req),
# #             "machines": self.get_by_machine(req),
# #             "throughput": self.get_throughput(req),
# #             "shift": self.get_shift(req),
# #             "momentum": self.get_momentum_parts(req),
# #             "weekdayProfile": self.get_weekday_profile(req),
# #             "machIntensity": self.get_intensity_by_machine(req),
# #             "machShiftImbalance": self.get_shift_imbalance_machine(req),
# #             "anomalyDays": self.get_anomaly_days(req),
# #         }

# #     def get_kpis(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT
# #                     COUNT(*) AS total_cnt,
# #                     COUNT(DISTINCT `자재번호`) AS part_kinds,
# #                     COUNT(DISTINCT `검사항목명`) AS item_kinds,
# #                     COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)), 0) AS prod_sum
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #             """
# #             k = db.execute(text(sql), params).mappings().first() or {}
# #             total = int(k.get("total_cnt", 0) or 0)
# #             part_kinds = int(k.get("part_kinds", 0) or 0)
# #             item_kinds = int(k.get("item_kinds", 0) or 0)
# #             prod_sum = float(k.get("prod_sum", 0) or 0.0)

# #             sql_insp = f"""
# #                 SELECT `검사구분` AS type, COUNT(*) AS qty
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY `검사구분`
# #                 ORDER BY qty DESC
# #             """
# #             insp_rows = [dict(r) for r in db.execute(text(sql_insp), params).mappings().all()]

# #             sql_work = f"""
# #                 SELECT `작업구분` AS type, COUNT(*) AS qty
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY `작업구분`
# #                 ORDER BY qty DESC
# #             """
# #             work_rows = [dict(r) for r in db.execute(text(sql_work), params).mappings().all()]

# #             sql_tr = f"""
# #                 SELECT DATE(`work_date`) AS d, COUNT(*) AS c
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY DATE(`work_date`)
# #             """
# #             days = db.execute(text(sql_tr), params).mappings().all()
# #             daily_avg = round(sum(int(r["c"]) for r in days) / len(days), 2) if days else 0.0
# #             intensity_per_k = round(total / (prod_sum / 1000.0), 3) if prod_sum > 0 else 0.0

# #             return {
# #                 "total": total,
# #                 "partKinds": part_kinds,
# #                 "itemKinds": item_kinds,
# #                 "dailyAvg": daily_avg,
# #                 "prodSum": prod_sum,
# #                 "intensityPerK": intensity_per_k,
# #                 "byInspType": insp_rows,
# #                 "byWorkType": work_rows,
# #             }
# #         finally:
# #             db.close()

# #     def get_by_item(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             top_n = getattr(req, "topN", 5) or 5
# #             sql = f"""
# #                 SELECT `검사항목명` AS item, COUNT(*) AS qty
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY `검사항목명`
# #                 ORDER BY qty DESC
# #                 LIMIT :top_n
# #             """
# #             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
# #             return [dict(r) for r in rows]
# #         finally:
# #             db.close()

# #     def get_trend(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT DATE(`work_date`) AS d, COUNT(*) AS cnt
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY DATE(`work_date`)
# #                 ORDER BY d
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [{"date": str(r["d"]), "count": int(r["cnt"] or 0)} for r in rows]
# #         finally:
# #             db.close()

# #     def get_stacked(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT
# #                     DATE(`work_date`) AS d,
# #                     SUM(CASE WHEN `검사구분` = '자동검사' THEN 1 ELSE 0 END) AS auto_cnt,
# #                     SUM(CASE WHEN `검사구분` LIKE '자주%%' THEN 1 ELSE 0 END) AS self_cnt,
# #                     SUM(CASE WHEN `검사구분` NOT IN ('자동검사') AND `검사구분` NOT LIKE '자주%%' THEN 1 ELSE 0 END) AS other_cnt
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY DATE(`work_date`)
# #                 ORDER BY d
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [
# #                 {"date": str(r["d"]), "auto": int(r["auto_cnt"] or 0), "self": int(r["self_cnt"] or 0), "other": int(r["other_cnt"] or 0)}
# #                 for r in rows
# #             ]
# #         finally:
# #             db.close()

# #     def get_by_part(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             top_n = getattr(req, "topN", 5) or 5
# #             sql = f"""
# #                 SELECT `자재번호` AS v, COUNT(*) AS qty
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY `자재번호`
# #                 ORDER BY qty DESC
# #                 LIMIT :top_n
# #             """
# #             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
# #             return [dict(r) for r in rows]
# #         finally:
# #             db.close()

# #     def get_by_process(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             top_n = getattr(req, "topN", 5) or 5
# #             sql = f"""
# #                 SELECT `process` AS proc, COUNT(*) AS qty
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY `process`
# #                 ORDER BY qty DESC
# #                 LIMIT :top_n
# #             """
# #             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
# #             return [dict(r) for r in rows]
# #         finally:
# #             db.close()

# #     def get_by_machine(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             top_n = getattr(req, "topN", 5) or 5
# #             sql = f"""
# #                 SELECT `equipment` AS machine, COUNT(*) AS qty
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY `equipment`
# #                 ORDER BY qty DESC
# #                 LIMIT :top_n
# #             """
# #             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
# #             return [dict(r) for r in rows]
# #         finally:
# #             db.close()

# #     def get_throughput(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT DATE(`work_date`) AS d,
# #                        COUNT(*) AS cnt,
# #                        COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)), 0) AS prod
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY DATE(`work_date`)
# #                 ORDER BY d
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [
# #                 {
# #                     "date": str(r["d"]),
# #                     "count": int(r["cnt"] or 0),
# #                     "prod": float(r["prod"] or 0.0),
# #                     "intensity": round((int(r["cnt"] or 0)) / (float(r["prod"] or 0.0) / 1000.0), 3)
# #                     if float(r["prod"] or 0.0) > 0
# #                     else 0.0,
# #                 }
# #                 for r in rows
# #             ]
# #         finally:
# #             db.close()

# #     def get_shift(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT DATE(`work_date`) AS d,
# #                        SUM(CASE WHEN `주야구분` = '주간' THEN 1 ELSE 0 END) AS day_cnt,
# #                        SUM(CASE WHEN `주야구분` = '야간' THEN 1 ELSE 0 END) AS night_cnt
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY DATE(`work_date`)
# #                 ORDER BY d
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [{"date": str(r["d"]), "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)} for r in rows]
# #         finally:
# #             db.close()

# #     def get_momentum_parts(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             end_str = getattr(req, "end_date", None)
# #             end_dt = datetime.strptime(end_str, "%Y-%m-%d") if end_str else datetime.utcnow()
# #             recent_start = (end_dt - timedelta(days=14)).date()
# #             prev_start = (end_dt - timedelta(days=28)).date()
# #             prev_end = (end_dt - timedelta(days=14)).date()

# #             where_sql, params = self._build_where(req)
# #             sql_recent = f"""
# #                 SELECT `자재번호` AS partNo, COUNT(*) AS qty
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql} AND DATE(`work_date`) > :recent_start AND DATE(`work_date`) <= :end_date_cut
# #                 GROUP BY `자재번호`
# #             """
# #             recent = db.execute(
# #                 text(sql_recent),
# #                 {**params, "recent_start": str(recent_start), "end_date_cut": end_dt.date().isoformat()},
# #             ).mappings().all()
# #             rmap = {r["partNo"]: int(r["qty"] or 0) for r in recent}

# #             sql_prev = f"""
# #                 SELECT `자재번호` AS partNo, COUNT(*) AS qty
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql} AND DATE(`work_date`) >= :prev_start AND DATE(`work_date`) <= :prev_end
# #                 GROUP BY `자재번호`
# #             """
# #             prev = db.execute(
# #                 text(sql_prev), {**params, "prev_start": str(prev_start), "prev_end": str(prev_end)}
# #             ).mappings().all()
# #             pmap = {r["partNo"]: int(r["qty"] or 0) for r in prev}

# #             out, keys = [], set(rmap.keys()) | set(pmap.keys())
# #             for k in keys:
# #                 rv, pv = rmap.get(k, 0), pmap.get(k, 0)
# #                 delta = rv - pv
# #                 growth = round((rv / pv - 1) * 100.0, 1) if pv > 0 else (100.0 if rv > 0 else 0.0)
# #                 out.append({"partNo": k, "recent": rv, "prev": pv, "delta": delta, "growthPct": growth})

# #             top_n = getattr(req, "topN", 5) or 5
# #             out.sort(key=lambda x: (x["delta"], x["recent"]), reverse=True)
# #             return out[:top_n]
# #         finally:
# #             db.close()

# #     def get_weekday_profile(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT DAYOFWEEK(`work_date`) AS dow,
# #                        COUNT(*) AS total,
# #                        SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
# #                        SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY DAYOFWEEK(`work_date`)
# #                 ORDER BY dow
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [
# #                 {"dow": int(r["dow"]), "total": int(r["total"] or 0), "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)}
# #                 for r in rows
# #             ]
# #         finally:
# #             db.close()

# #     def get_intensity_by_process(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             top_n = getattr(req, "topN", 5) or 5
# #             sql = f"""
# #                 SELECT t.proc, t.cnt, t.prod,
# #                        CASE WHEN t.prod>0 THEN ROUND(t.cnt/(t.prod/1000.0),3) ELSE 0 END AS intensity
# #                 FROM (
# #                   SELECT `process` AS proc, COUNT(*) AS cnt, COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)),0) AS prod
# #                   FROM {self.TABLE}
# #                   WHERE {where_sql}
# #                   GROUP BY `process`
# #                 ) t
# #                 ORDER BY intensity DESC
# #                 LIMIT :top_n
# #             """
# #             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
# #             return [dict(r) for r in rows]
# #         finally:
# #             db.close()

# #     def get_shift_imbalance_process(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT `process` AS proc,
# #                        SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
# #                        SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
# #                        COUNT(*) AS total
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY `process`
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             out = []
# #             for r in rows:
# #                 day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
# #                 total = int(r["total"] or 0)
# #                 ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
# #                 imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
# #                 out.append(
# #                     {"proc": r["proc"], "day": day, "night": night, "total": total, "ratioNightPerDay": ratio, "imbalance": imbalance}
# #                 )
# #             top_n = getattr(req, "topN", 5) or 5
# #             out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
# #             return out[:top_n]
# #         finally:
# #             db.close()

# #     def get_intensity_by_machine(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             top_n = getattr(req, "topN", 5) or 5
# #             sql = f"""
# #                 SELECT t.machine, t.cnt, t.prod,
# #                        CASE WHEN t.prod>0 THEN ROUND(t.cnt/(t.prod/1000.0),3) ELSE 0 END AS intensity
# #                 FROM (
# #                   SELECT `equipment` AS machine, COUNT(*) AS cnt, COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)),0) AS prod
# #                   FROM {self.TABLE}
# #                   WHERE {where_sql}
# #                   GROUP BY `equipment`
# #                 ) t
# #                 ORDER BY intensity DESC
# #                 LIMIT :top_n
# #             """
# #             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
# #             return [dict(r) for r in rows]
# #         finally:
# #             db.close()

# #     def get_shift_imbalance_machine(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT `equipment` AS machine,
# #                        SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
# #                        SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
# #                        COUNT(*) AS total
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY `equipment`
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             out = []
# #             for r in rows:
# #                 day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
# #                 total = int(r["total"] or 0)
# #                 ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
# #                 imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
# #                 out.append(
# #                     {"machine": r["machine"], "day": day, "night": night, "total": total, "ratioNightPerDay": ratio, "imbalance": imbalance}
# #                 )
# #             top_n = getattr(req, "topN", 5) or 5
# #             out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
# #             return out[:top_n]
# #         finally:
# #             db.close()

# #     def get_anomaly_days(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT DATE(`work_date`) AS d, COUNT(*) AS c
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 GROUP BY DATE(`work_date`)
# #                 ORDER BY d
# #             """
# #             days = [dict(r) for r in db.execute(text(sql), params).mappings().all()]
# #             if not days:
# #                 return []
# #             c_vals = [int(x["c"]) for x in days]
# #             n = len(c_vals)
# #             mean_v = sum(c_vals) / n
# #             var = sum((x - mean_v) ** 2 for x in c_vals) / n
# #             std = (var ** 0.5) if var > 0 else 0.0

# #             out = []
# #             for d in days:
# #                 c = int(d["c"])
# #                 z = (c - mean_v) / std if std > 0 else 0.0
# #                 if z >= 2.0:
# #                     out.append(
# #                         {"date": str(d["d"]), "count": c, "z": round(z, 2), "avg": round(mean_v, 2), "std": round(std, 2)}
# #                     )
# #             out.sort(key=lambda x: x["z"], reverse=True)
# #             return out[:10]
# #         finally:
# #             db.close()

# #     def get_pareto_concentration(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             top_n = getattr(req, "topN", 5) or 5

# #             sql_total = f"SELECT COUNT(*) AS c FROM {self.TABLE} WHERE {where_sql}"
# #             total = int((db.execute(text(sql_total), params).scalar() or 0))

# #             def share_by(col):
# #                 sql_top = f"""
# #                     SELECT SUM(cnt) FROM (
# #                         SELECT COUNT(*) AS cnt
# #                         FROM {self.TABLE}
# #                         WHERE {where_sql}
# #                         GROUP BY {col}
# #                         LIMIT :top_n
# #                     ) t
# #                 """
# #                 top_sum = int(db.execute(text(sql_top), {**params, "top_n": top_n}).scalar() or 0)
# #                 pct = round((top_sum / total) * 100.0, 2) if total > 0 else 0.0
# #                 return {"topSum": top_sum, "total": total, "sharePct": pct}

# #             return {"part": share_by("`자재번호`"), "item": share_by("`검사항목명`")}
# #         finally:
# #             db.close()

# #     # ---------------- 옵션 ----------------
# #     def list_factories(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where, params = [], {}
# #             if getattr(req, "start_date", None):
# #                 where.append("`work_date` >= :start_date")
# #                 params["start_date"] = req.start_date
# #             if getattr(req, "end_date", None):
# #                 where.append("`work_date` < DATE_ADD(:end_date, INTERVAL 1 DAY)")
# #                 params["end_date"] = req.end_date
# #             if not where:
# #                 where.append("1=1")
# #             where_sql = " AND ".join(where)
# #             sql = f"""
# #                 SELECT DISTINCT `plant` AS v
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql} AND `plant` IS NOT NULL AND `plant` <> ''
# #                 ORDER BY v
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [r["v"] for r in rows]
# #         finally:
# #             db.close()

# #     def list_processes(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT DISTINCT `process` AS v
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql} AND `process` IS NOT NULL AND `process` <> ''
# #                 ORDER BY v
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [r["v"] for r in rows]
# #         finally:
# #             db.close()

# #     def list_equipments(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT DISTINCT `equipment` AS v
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql} AND `equipment` IS NOT NULL AND `equipment` <> ''
# #                 ORDER BY v
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [r["v"] for r in rows]
# #         finally:
# #             db.close()

# #     def list_parts(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT DISTINCT `자재번호` AS v
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql} AND `자재번호` IS NOT NULL AND `자재번호` <> ''
# #                 ORDER BY v
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [r["v"] for r in rows]
# #         finally:
# #             db.close()

# #     def list_items(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where_sql, params = self._build_where(req)
# #             sql = f"""
# #                 SELECT DISTINCT `검사항목명` AS v
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql} AND `검사항목명` IS NOT NULL AND `검사항목명` <> ''
# #                 ORDER BY v
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [r["v"] for r in rows]
# #         finally:
# #             db.close()

# #     def list_years(self, req):
# #         db: Session = next(get_db())
# #         try:
# #             where, params = [], {}
# #             if getattr(req, "factory", None):
# #                 where.append("`plant` = :factory")
# #                 params["factory"] = req.factory
# #             if getattr(req, "process", None):
# #                 where.append("`process` = :process")
# #                 params["process"] = req.process
# #             if getattr(req, "partNo", None):
# #                 where.append("`자재번호` LIKE :partNo")
# #                 params["partNo"] = f"%{req.partNo.strip()}%"
# #             if getattr(req, "inspType", None):
# #                 where.append("`검사구분` = :inspType")
# #                 params["inspType"] = req.inspType
# #             if getattr(req, "workType", None):
# #                 where.append("`작업구분` = :workType")
# #                 params["workType"] = req.workType
# #             pnm = getattr(req, "partName", None) or getattr(req, "item", None)
# #             if pnm:
# #                 params["partName"] = f"%{pnm.strip()}%"
# #                 where.append("`자재명` LIKE :partName")
# #             if getattr(req, "inspectItem", None):
# #                 where.append("`검사항목명` LIKE :inspectItem")
# #                 params["inspectItem"] = f"%{req.inspectItem.strip()}%"

# #             where_sql = " AND ".join(where) if where else "1=1"
# #             sql = f"""
# #                 SELECT DISTINCT YEAR(`work_date`) AS y
# #                 FROM {self.TABLE}
# #                 WHERE {where_sql}
# #                 ORDER BY y DESC
# #             """
# #             rows = db.execute(text(sql), params).mappings().all()
# #             return [int(r["y"]) for r in rows if r["y"] is not None]
# #         finally:
# #             db.close()


# # inspection_chart_service = InspectionChartService()


# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from datetime import datetime, timedelta, date
# from app.config.database import get_db
# import re
# import calendar


# class InspectionChartService:
#     # ✅ 실제 테이블
#     SCHEMA = "AJIN_newDB"
#     TBL = "생산_검사"
#     TABLE = "`AJIN_newDB`.`생산_검사`"

#     # ---- 내부 캐시 ----
#     _cache = {}

#     # ---------- 컬럼 존재/선택 ----------
#     def _col_exists(self, db: Session, col: str) -> bool:
#         key = f"exists::{col}"
#         if key in self._cache:
#             return self._cache[key]
#         sql = """
#             SELECT 1
#             FROM INFORMATION_SCHEMA.COLUMNS
#             WHERE TABLE_SCHEMA = :s AND TABLE_NAME = :t AND COLUMN_NAME = :c
#             LIMIT 1
#         """
#         ok = db.execute(text(sql), {"s": self.SCHEMA, "t": self.TBL, "c": col}).first() is not None
#         self._cache[key] = ok
#         return ok

#     def _pick_col(self, db: Session, candidates) -> str | None:
#         key = f"pick::{','.join(candidates)}"
#         if key in self._cache:
#             return self._cache[key]
#         for c in candidates:
#             if self._col_exists(db, c):
#                 self._cache[key] = f"`{c}`"
#                 return self._cache[key]
#         self._cache[key] = None
#         return None

#     def _value_col(self, db: Session) -> str:
#         """Xn에 표시할 '값' 컬럼 자동 선택 (✅ '생산' 최우선)"""
#         key = "value_col"
#         if key in self._cache:
#             return self._cache[key]
#         sql = """
#             SELECT COLUMN_NAME
#             FROM INFORMATION_SCHEMA.COLUMNS
#             WHERE TABLE_SCHEMA = :s AND TABLE_NAME = :t
#               AND COLUMN_NAME IN ('생산','검사값','측정값','결과값','값','측정치','측정결과')
#             ORDER BY FIELD(COLUMN_NAME,'생산','검사값','측정값','결과값','값','측정치','측정결과')
#             LIMIT 1
#         """
#         row = db.execute(text(sql), {"s": self.SCHEMA, "t": self.TBL}).first()
#         if row and row[0]:
#             self._cache[key] = f"`{row[0]}`"
#         else:
#             # 기본값도 '생산' 우선
#             self._cache[key] = "`생산`" if self._col_exists(db, "생산") else (
#                 "`검사값`" if self._col_exists(db, "검사값") else "NULL"
#             )
#         return self._cache[key]

#     # ---------- WHERE ----------
#     def _build_where(self, req):
#         where, params = [], {}

#         def has(v):
#             if v is None:
#                 return False
#             if isinstance(v, str):
#                 s = v.strip()
#                 return s != "" and s.lower() != "string"
#             return True

#         if has(getattr(req, "start_date", None)):
#             where.append("`work_date` >= :start_date")
#             params["start_date"] = req.start_date
#         if has(getattr(req, "end_date", None)):
#             where.append("`work_date` < DATE_ADD(:end_date, INTERVAL 1 DAY)")
#             params["end_date"] = req.end_date

#         if has(getattr(req, "factory", None)):
#             where.append("`plant` = :factory")
#             params["factory"] = req.factory
#         if has(getattr(req, "process", None)):
#             where.append("`process` = :process")
#             params["process"] = req.process
#         if has(getattr(req, "equipment", None)):
#             where.append("`equipment` = :equipment")
#             params["equipment"] = req.equipment
#         if has(getattr(req, "workType", None)):
#             where.append("`작업구분` = :workType")
#             params["workType"] = req.workType
#         if has(getattr(req, "inspType", None)):
#             where.append("`검사구분` = :inspType")
#             params["inspType"] = req.inspType
#         if has(getattr(req, "shiftType", None)):
#             where.append("`주야구분` = :shiftType")
#             params["shiftType"] = req.shiftType
#         if has(getattr(req, "partNo", None)):
#             where.append("`자재번호` LIKE :partNo")
#             params["partNo"] = f"%{req.partNo.strip()}%"

#         # 품명(=자재명)
#         part_name = getattr(req, "partName", None) or getattr(req, "item", None)
#         if has(part_name):
#             params["partName"] = f"%{part_name.strip()}%"
#             where.append("`자재명` LIKE :partName")

#         # 검사항목명
#         inspect_item = getattr(req, "inspectItem", None)
#         if has(inspect_item):
#             params["inspectItem"] = f"%{inspect_item.strip()}%"
#             where.append("`검사항목명` LIKE :inspectItem")

#         if not where:
#             where.append("1=1")
#         return " AND ".join(where), params

#     # ✅ 날짜 조건을 제외한 WHERE (최신 달 계산용)
#     def _build_where_without_dates(self, req):
#         class _Dummy:  # shallow object with selected attrs
#             pass
#         dummy = _Dummy()
#         # 날짜는 넣지 않음
#         for f in ["factory", "process", "equipment", "workType", "inspType",
#                   "shiftType", "partNo", "partName", "item", "inspectItem"]:
#             setattr(dummy, f, getattr(req, f, None))
#         return self._build_where(dummy)

#     # =========================================================
#     # A. 일자별 Xn 표 (주/야 헤더 + X1~Xn + 작업구분 라벨)
#     # =========================================================
#     def _short_work(self, s: str) -> str:
#         if not s:
#             return ""
#         s = str(s)
#         if s.startswith("초"):
#             return "초"
#         if s.startswith("중"):
#             return "중"
#         if s.startswith("종"):
#             return "종"
#         return s

#     def get_xn_daily(self, req):
#         """
#         응답:
#         {
#           "cols": ["X1","X2",...],
#           "days": ["YYYY-MM-DD", ...],
#           "shifts": ["주간","야간", ...],
#           "workHeaders": { "YYYY-MM-DD": { "주간": {"X1":"초",...}, "야간": {...} } },
#           "tables": {
#              "YYYY-MM-DD": [
#                { "NO":1, "검사순번":1, "검사항목명":"...", "검사내용":"...",
#                  "주간":{"X1":..., "X2":...}, "야간":{"X1":..., ...}, "평균": ... },
#                ...
#              ]
#           },
#           "dayList": [ { "d":"YYYY-MM-DD", "equipment":"...", "partNo":"..." }, ... ]  # ✅ 추가
#         }
#         """
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)

#             # 동적 컬럼
#             date_col = "`work_date`"
#             item_col = "`검사항목명`" if self._col_exists(db, "검사항목명") else None

#             # spec(검사내용) 후보
#             spec_col = None
#             for c in ["검사내용", "기준", "규격", "판정기준", "상세", "내용", "비고"]:
#                 if self._col_exists(db, c):
#                     spec_col = f"`{c}`"
#                     break

#             # 작업순번(=Xn 시퀀스)
#             step_col = None
#             for c in ["작업순번", "op_seq", "seq", "검사순번", "검사순서"]:
#                 if self._col_exists(db, c):
#                     step_col = f"`{c}`"
#                     break
#             if not step_col:
#                 step_col = "1"

#             # 검사순번(행 정렬용)
#             insp_col = None
#             for c in ["검사순번", "검사순서", "insp_seq"]:
#                 if self._col_exists(db, c):
#                     insp_col = f"`{c}`"
#                     break

#             shift_col = "`주야구분`" if self._col_exists(db, "주야구분") else "''"
#             work_col = "`작업구분`" if self._col_exists(db, "작업구분") else "NULL"

#             val_col = self._value_col(db)

#             # 보고일 목록
#             sql_days = f"""
#                 SELECT DATE({date_col}) AS d
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE({date_col})
#                 ORDER BY d
#             """
#             days = [str(r["d"]) for r in db.execute(text(sql_days), params).mappings().all()]

#             # ✅ 날짜별 대표 설비/품번(최빈값; 없으면 NULL)
#             sql_day_meta = f"""
#                 WITH b AS (
#                     SELECT DATE({date_col}) AS d,
#                            COALESCE(`equipment`,'') AS eq,
#                            COALESCE(`자재번호`,'')  AS part
#                     FROM {self.TABLE}
#                     WHERE {where_sql}
#                 ),
#                 eqm AS (
#                     SELECT d, eq,
#                            ROW_NUMBER() OVER (PARTITION BY d ORDER BY COUNT(*) DESC, eq) AS rn
#                     FROM b WHERE eq <> ''
#                     GROUP BY d, eq
#                 ),
#                 pm AS (
#                     SELECT d, part,
#                            ROW_NUMBER() OVER (PARTITION BY d ORDER BY COUNT(*) DESC, part) AS rn
#                     FROM b WHERE part <> ''
#                     GROUP BY d, part
#                 )
#                 SELECT x.d,
#                        (SELECT eq   FROM eqm WHERE eqm.d = x.d AND eqm.rn = 1)   AS equipment,
#                        (SELECT part FROM pm  WHERE pm.d  = x.d AND pm.rn  = 1)   AS partNo
#                 FROM (SELECT DISTINCT d FROM b) x
#                 ORDER BY x.d
#             """
#             day_list_rows = db.execute(text(sql_day_meta), params).mappings().all()
#             day_list = [{"d": str(r["d"]), "equipment": r["equipment"], "partNo": r["partNo"]} for r in day_list_rows]

#             # Xn 최대(상한 10)
#             sql_n = f"SELECT COUNT(DISTINCT {step_col}) FROM {self.TABLE} WHERE {where_sql}"
#             max_n = int(db.execute(text(sql_n), params).scalar() or 0)
#             max_n = min(max_n if max_n > 0 else 1, 10)
#             cols = [f"X{i}" for i in range(1, max_n + 1)]

#             # spec/항목 없으면 빈 결과
#             if not item_col:
#                 return {"cols": cols, "days": days, "shifts": [], "workHeaders": {}, "tables": {}, "dayList": day_list}
#             spec_expr = f"COALESCE({spec_col},'')" if spec_col else "''"
#             item_expr = f"COALESCE({item_col},'')"

#             # insp_seq 식
#             insp_seq_expr = (
#                 f"""
#                 CASE
#                   WHEN {insp_col} REGEXP '^[0-9]+$' THEN CAST({insp_col} AS UNSIGNED)
#                   ELSE DENSE_RANK() OVER (
#                          PARTITION BY DATE({date_col})
#                          ORDER BY COALESCE({insp_col},''), {item_expr}, {spec_expr}
#                        )
#                 END
#                 """ if insp_col else
#                 f"DENSE_RANK() OVER (PARTITION BY DATE({date_col}) ORDER BY {item_expr}, {spec_expr})"
#             )

#             # 기본 집계(일자·항목·스펙·주야·seq)
#             sql_agg = f"""
#                 WITH base AS (
#                   SELECT
#                     DATE({date_col}) AS d,
#                     {item_expr} AS item,
#                     {spec_expr} AS spec,
#                     COALESCE({shift_col},'') AS shift,
#                     COALESCE({work_col},'')  AS work,
#                     CAST({val_col} AS DECIMAL(20,6)) AS val,
#                     CASE
#                       WHEN {step_col} REGEXP '^[0-9]+$' THEN CAST({step_col} AS UNSIGNED)
#                       ELSE DENSE_RANK() OVER (
#                           PARTITION BY DATE({date_col}), {item_expr}, {spec_expr}, COALESCE({shift_col},'')
#                           ORDER BY COALESCE({step_col},'')
#                       )
#                     END AS seq,
#                     {insp_seq_expr} AS insp_no
#                   FROM {self.TABLE}
#                   WHERE {where_sql}
#                 ),
#                 agg AS (
#                   SELECT d, item, spec, shift, seq, AVG(val) AS avg_val
#                   FROM base
#                   GROUP BY d, item, spec, shift, seq
#                 ),
#                 insp_min AS (
#                   SELECT d, item, spec, MIN(insp_no) AS insp_no
#                   FROM base
#                   GROUP BY d, item, spec
#                 ),
#                 work_mode AS (
#                   SELECT d, shift, seq, work,
#                          ROW_NUMBER() OVER (PARTITION BY d, shift, seq ORDER BY COUNT(*) DESC, work) AS rn
#                   FROM base
#                   WHERE work IS NOT NULL AND work <> ''
#                   GROUP BY d, shift, seq, work
#                 )
#                 SELECT a.d, a.item, a.spec, a.shift, a.seq, a.avg_val,
#                        wm.work AS work_label,
#                        im.insp_no
#                 FROM agg a
#                 LEFT JOIN work_mode wm
#                   ON a.d = wm.d AND a.shift = wm.shift AND a.seq = wm.seq AND wm.rn = 1
#                 LEFT JOIN insp_min im
#                   ON a.d = im.d AND a.item = im.item AND a.spec = im.spec
#                 ORDER BY a.d, im.insp_no, a.item, a.spec, a.shift, a.seq
#             """
#             recs = [dict(r) for r in db.execute(text(sql_agg), params).mappings().all()]

#             # shifts 정렬(주간, 야간 우선)
#             shift_order = []
#             for r in recs:
#                 s = r["shift"] or ""
#                 if s not in shift_order:
#                     shift_order.append(s)
#             order_pref = ["주간", "야간"]
#             shift_order.sort(key=lambda x: (order_pref.index(x) if x in order_pref else len(order_pref), x))

#             # 일자별 헤더 라벨/테이블 구성
#             work_headers = {}
#             tables = {}

#             # (d,item,spec) -> row
#             rowmap = {}

#             for r in recs:
#                 d = str(r["d"])
#                 item = (r["item"] or "").strip()
#                 spec = (r["spec"] or "").strip()
#                 shift = (r["shift"] or "").strip()
#                 seq = int(r["seq"] or 0)
#                 insp_no = int(r["insp_no"] or 0) if r["insp_no"] is not None else None
#                 val = float(r["avg_val"]) if r["avg_val"] is not None else None
#                 xn = f"X{seq}"
#                 if seq < 1 or seq > max_n:
#                     continue

#                 if r.get("work_label"):
#                     work_headers.setdefault(d, {}).setdefault(shift, {})[xn] = self._short_work(r["work_label"])

#                 tables.setdefault(d, [])
#                 key = (d, item, spec)
#                 if key not in rowmap:
#                     row = {"NO": 0, "검사항목명": item, "검사내용": spec, "검사순번": insp_no}
#                     for s in shift_order:
#                         row[s] = {}
#                     row["평균"] = None
#                     tables[d].append(row)
#                     rowmap[key] = row
#                 row = rowmap[key]
#                 row["검사순번"] = insp_no if insp_no is not None else row.get("검사순번")
#                 row.setdefault(shift, {})[xn] = val

#             # 일자별 정렬(검사순번 asc) + NO/평균 계산
#             for d in tables.keys():
#                 tables[d].sort(
#                     key=lambda rw: (
#                         rw.get("검사순번") if rw.get("검사순번") is not None else 10**9,
#                         rw.get("검사항목명") or "",
#                         rw.get("검사내용") or "",
#                     )
#                 )
#                 for idx, row in enumerate(tables[d], start=1):
#                     row["NO"] = idx
#                     vals = []
#                     for s in shift_order:
#                         for c in cols:
#                             v = row.get(s, {}).get(c, None)
#                             if v is not None:
#                                 try:
#                                     vals.append(float(v))
#                                 except Exception:
#                                     pass
#                     row["평균"] = round(sum(vals) / len(vals), 6) if vals else None

#             return {
#                 "cols": cols,
#                 "days": days,
#                 "shifts": shift_order,
#                 "workHeaders": work_headers,
#                 "tables": tables,
#                 "dayList": day_list,  # ✅ 좌측 패널용 메타
#             }
#         finally:
#             db.close()

#     # =========================================================
#     # B. Xn 그룹 시리즈 (기존)
#     # =========================================================
#     def _normalize_group_by(self, gb: str):
#         if not gb:
#             return None
#         m = {
#             "partno": "`자재번호`",
#             "part": "`자재번호`",
#             "part_no": "`자재번호`",
#             "partname": "`자재명`",
#             "partName": "`자재명`",
#             "shift": "`주야구분`",
#             "shifttype": "`주야구분`",
#             "shiftType": "`주야구분`",
#             "insp": "`검사구분`",
#             "insptype": "`검사구분`",
#             "inspType": "`검사구분`",
#             "item": "`검사항목명`",
#             "spec": "`검사내용`",
#         }
#         return m.get(str(gb).replace(" ", "").lower())

#     def get_xn_series(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             val_col = self._value_col(db)

#             group_col = self._normalize_group_by(getattr(req, "groupBy", None))
#             if not group_col:
#                 return {"groupBy": None, "cols": [], "rows": []}
#             if group_col == "`검사내용`":
#                 spec = None
#                 for c in ["검사내용", "기준", "규격", "판정기준", "상세", "내용", "비고"]:
#                     if self._col_exists(db, c):
#                         spec = f"`{c}`"
#                         break
#                 group_col = spec or "''"

#             step_col = None
#             for c in ["작업순번", "검사순번", "검사순서", "op_seq", "seq"]:
#                 if self._col_exists(db, c):
#                     step_col = f"`{c}`"
#                     break
#             if not step_col:
#                 step_col = "1"

#             sql_n = f"SELECT COUNT(DISTINCT {step_col}) FROM {self.TABLE} WHERE {where_sql}"
#             max_n = int(db.execute(text(sql_n), params).scalar() or 0)
#             max_n = min(max_n if max_n > 0 else 1, 20)
#             cols = [f"X{i}" for i in range(1, max_n + 1)]
#             top_n = getattr(req, "topN", 5) or 5

#             sql_series = f"""
#                 WITH base AS (
#                     SELECT
#                         {group_col} AS grp,
#                         CAST({val_col} AS DECIMAL(20,6)) AS val,
#                         {step_col} AS step_raw
#                     FROM {self.TABLE}
#                     WHERE {where_sql}
#                 ),
#                 topgrp AS (
#                     SELECT grp
#                     FROM base
#                     WHERE grp IS NOT NULL AND grp <> ''
#                     GROUP BY grp
#                     ORDER BY COUNT(*) DESC
#                     LIMIT :top_n
#                 ),
#                 ranked AS (
#                     SELECT
#                         b.grp,
#                         CASE
#                           WHEN b.step_raw REGEXP '^[0-9]+$' THEN CAST(b.step_raw AS UNSIGNED)
#                           ELSE DENSE_RANK() OVER (PARTITION BY b.grp ORDER BY COALESCE(b.step_raw,''))
#                         END AS seq,
#                         b.val
#                     FROM base b
#                     JOIN topgrp t ON b.grp = t.grp
#                 )
#                 SELECT grp, seq, AVG(val) AS avg_val
#                 FROM ranked
#                 GROUP BY grp, seq
#                 ORDER BY grp, seq
#             """
#             recs = [dict(r) for r in db.execute(text(sql_series), {**params, "top_n": top_n}).mappings().all()]

#             series_map = {}
#             for r in recs:
#                 g = r["grp"]
#                 n = int(r["seq"])
#                 v = float(r["avg_val"]) if r["avg_val"] is not None else None
#                 series_map.setdefault(g, {c: None for c in cols})
#                 if 1 <= n <= max_n:
#                     series_map[g][f"X{n}"] = v

#             out_rows = [{"label": g, **series_map[g]} for g in series_map.keys()]
#             return {"groupBy": group_col, "cols": cols, "rows": out_rows}
#         finally:
#             db.close()

#     # =========================================================
#     # C. 숫자형(실측값) 검사항목 — 일자별 추이
#     # =========================================================
#     def _parse_spec_numbers(self, s: str):
#         if not s:
#             return (None, None, None)
#         try:
#             txt = s.replace("㎜", "mm").replace("＋", "+").replace("－", "-").strip()

#             m = re.search(r"([+-]?\d+(?:\.\d+)?)\s*±\s*([+-]?\d+(?:\.\d+)?)", txt)
#             if m:
#                 nom = float(m.group(1)); tol = float(m.group(2))
#                 return (nom, nom - tol, nom + tol)

#             m = re.search(r"([+-]?\d+(?:\.\d+)?)[^\d+-]+([+]\s*\d+(?:\.\d+)?)\s*mm?\s*이내", txt, re.IGNORECASE)
#             if m:
#                 nom = float(m.group(1)); up = float(m.group(2).replace("+",""))
#                 return (nom, None, nom + up)

#             m = re.search(r"([+-]?\d+(?:\.\d+)?)", txt)
#             if m:
#                 nom = float(m.group(1))
#                 return (nom, None, None)
#         except Exception:
#             pass
#         return (None, None, None)

#     def get_numeric_trend(self, req):
#         """
#         스펙(텍스트)에 숫자가 포함된 (검사항목명, 스펙) TopN 대해 일자별 평균 실측값
#         """
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             val_col = self._value_col(db)
#             top_n = getattr(req, "topN", 5) or 5

#             item_col = "`검사항목명`" if self._col_exists(db, "검사항목명") else None
#             spec_col = None
#             for c in ["검사내용", "기준", "규격", "판정기준", "상세", "내용", "비고"]:
#                 if self._col_exists(db, c):
#                     spec_col = f"`{c}`"
#                     break
#             if not (item_col and spec_col):
#                 return {"dates": [], "series": []}

#             sql_days = f"""
#                 SELECT DATE(`work_date`) AS d
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND {spec_col} REGEXP '[0-9]'
#                 GROUP BY DATE(`work_date`)
#                 ORDER BY d
#             """
#             days = [str(r["d"]) for r in db.execute(text(sql_days), params).mappings().all()]
#             if not days:
#                 return {"dates": [], "series": []}

#             sql_avg = f"""
#                 WITH base AS (
#                   SELECT DATE(`work_date`) AS d,
#                          COALESCE({item_col},'') AS item,
#                          COALESCE({spec_col},'') AS spec,
#                          CAST({val_col} AS DECIMAL(20,6)) AS val
#                   FROM {self.TABLE}
#                   WHERE {where_sql} AND {spec_col} REGEXP '[0-9]'
#                 )
#                 SELECT b.d, b.item, b.spec, AVG(b.val) AS avg_val
#                 FROM base b
#                 JOIN (
#                     SELECT item, spec
#                     FROM (
#                       SELECT COALESCE({item_col},'') AS item,
#                              COALESCE({spec_col},'') AS spec,
#                              COUNT(*) AS c
#                       FROM {self.TABLE}
#                       WHERE {where_sql} AND {spec_col} REGEXP '[0-9]'
#                       GROUP BY COALESCE({item_col},''), COALESCE({spec_col},'')
#                       ORDER BY c DESC
#                       LIMIT :top_n
#                     ) t
#                 ) tp ON b.item = tp.item AND b.spec = tp.spec
#                 GROUP BY b.item, b.spec, b.d
#                 ORDER BY b.item, b.spec, b.d
#             """
#             avg_rows = db.execute(text(sql_avg), {**params, "top_n": top_n}).mappings().all()

#             # 레이블/값 매핑
#             top_pairs = {}
#             for r in avg_rows:
#                 top_pairs[(r["item"], r["spec"])] = True

#             label_map = {}
#             val_map = {}
#             for (item, spec) in top_pairs.keys():
#                 item_s = (item or "").strip()
#                 spec_s = (spec or "").strip()
#                 label = f"{item_s} | {spec_s}" if spec_s else item_s
#                 label_map[(item, spec)] = label
#                 val_map[label] = {d: None for d in days}

#             spec_nums = {}
#             for (item, spec), label in label_map.items():
#                 spec_nums[label] = self._parse_spec_numbers(spec)

#             for r in avg_rows:
#                 item = r["item"]
#                 spec = r["spec"]
#                 label = label_map.get((item, spec))
#                 d = str(r["d"])
#                 v = float(r["avg_val"]) if r["avg_val"] is not None else None
#                 if label in val_map and d in val_map[label]:
#                     val_map[label][d] = v

#             series = []
#             for label, dayvals in val_map.items():
#                 series.append({
#                     "label": label,
#                     "data": [dayvals[d] for d in days],
#                     "nominal": spec_nums.get(label, (None,None,None))[0],
#                     "lsl": spec_nums.get(label, (None,None,None))[1],
#                     "usl": spec_nums.get(label, (None,None,None))[2],
#                 })

#             return {"dates": days, "series": series}
#         finally:
#             db.close()

#     # =========================================================
#     # D. 기존 대시보드(생략 없이 유지)
#     # =========================================================
#     def get_dashboard(self, req):
#         return {
#             "kpis": self.get_kpis(req),
#             "byItem": self.get_by_item(req),
#             "trend": self.get_trend(req),
#             "stacked": self.get_stacked(req),
#             "byPart": self.get_by_part(req),
#             "byProcess": self.get_by_process(req),
#             "machines": self.get_by_machine(req),
#             "throughput": self.get_throughput(req),
#             "shift": self.get_shift(req),
#             "momentum": self.get_momentum_parts(req),
#             "weekdayProfile": self.get_weekday_profile(req),
#             "machIntensity": self.get_intensity_by_machine(req),
#             "machShiftImbalance": self.get_shift_imbalance_machine(req),
#             "anomalyDays": self.get_anomaly_days(req),
#         }

#     def get_kpis(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT
#                     COUNT(*) AS total_cnt,
#                     COUNT(DISTINCT `자재번호`) AS part_kinds,
#                     COUNT(DISTINCT `검사항목명`) AS item_kinds,
#                     COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)), 0) AS prod_sum
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#             """
#             k = db.execute(text(sql), params).mappings().first() or {}
#             total = int(k.get("total_cnt", 0) or 0)
#             part_kinds = int(k.get("part_kinds", 0) or 0)
#             item_kinds = int(k.get("item_kinds", 0) or 0)
#             prod_sum = float(k.get("prod_sum", 0) or 0.0)

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

#             sql_tr = f"""
#                 SELECT DATE(`work_date`) AS d, COUNT(*) AS c
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`work_date`)
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

#     def get_trend(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DATE(`work_date`) AS d, COUNT(*) AS cnt
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`work_date`)
#                 ORDER BY d
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [{"date": str(r["d"]), "count": int(r["cnt"] or 0)} for r in rows]
#         finally:
#             db.close()

#     def get_stacked(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT
#                     DATE(`work_date`) AS d,
#                     SUM(CASE WHEN `검사구분` = '자동검사' THEN 1 ELSE 0 END) AS auto_cnt,
#                     SUM(CASE WHEN `검사구분` LIKE '자주%%' THEN 1 ELSE 0 END) AS self_cnt,
#                     SUM(CASE WHEN `검사구분` NOT IN ('자동검사') AND `검사구분` NOT LIKE '자주%%' THEN 1 ELSE 0 END) AS other_cnt
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`work_date`)
#                 ORDER BY d
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [
#                 {"date": str(r["d"]), "auto": int(r["auto_cnt"] or 0), "self": int(r["self_cnt"] or 0), "other": int(r["other_cnt"] or 0)}
#                 for r in rows
#             ]
#         finally:
#             db.close()

#     def get_by_part(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             top_n = getattr(req, "topN", 5) or 5
#             sql = f"""
#                 SELECT `자재번호` AS v, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `자재번호`
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
#                 SELECT `process` AS proc, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `process`
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
#                 SELECT `equipment` AS machine, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `equipment`
#                 ORDER BY qty DESC
#                 LIMIT :top_n
#             """
#             rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
#             return [dict(r) for r in rows]
#         finally:
#             db.close()

#     def get_throughput(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DATE(`work_date`) AS d,
#                        COUNT(*) AS cnt,
#                        COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)), 0) AS prod
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`work_date`)
#                 ORDER BY d
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [
#                 {
#                     "date": str(r["d"]),
#                     "count": int(r["cnt"] or 0),
#                     "prod": float(r["prod"] or 0.0),
#                     "intensity": round((int(r["cnt"] or 0)) / (float(r["prod"] or 0.0) / 1000.0), 3)
#                     if float(r["prod"] or 0.0) > 0
#                     else 0.0,
#                 }
#                 for r in rows
#             ]
#         finally:
#             db.close()

#     def get_shift(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DATE(`work_date`) AS d,
#                        SUM(CASE WHEN `주야구분` = '주간' THEN 1 ELSE 0 END) AS day_cnt,
#                        SUM(CASE WHEN `주야구분` = '야간' THEN 1 ELSE 0 END) AS night_cnt
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`work_date`)
#                 ORDER BY d
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [{"date": str(r["d"]), "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)} for r in rows]
#         finally:
#             db.close()

#     def get_momentum_parts(self, req):
#         db: Session = next(get_db())
#         try:
#             end_str = getattr(req, "end_date", None)
#             end_dt = datetime.strptime(end_str, "%Y-%m-%d") if end_str else datetime.utcnow()
#             recent_start = (end_dt - timedelta(days=14)).date()
#             prev_start = (end_dt - timedelta(days=28)).date()
#             prev_end = (end_dt - timedelta(days=14)).date()

#             where_sql, params = self._build_where(req)
#             sql_recent = f"""
#                 SELECT `자재번호` AS partNo, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND DATE(`work_date`) > :recent_start AND DATE(`work_date`) <= :end_date_cut
#                 GROUP BY `자재번호`
#             """
#             recent = db.execute(
#                 text(sql_recent),
#                 {**params, "recent_start": str(recent_start), "end_date_cut": end_dt.date().isoformat()},
#             ).mappings().all()
#             rmap = {r["partNo"]: int(r["qty"] or 0) for r in recent}

#             sql_prev = f"""
#                 SELECT `자재번호` AS partNo, COUNT(*) AS qty
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND DATE(`work_date`) >= :prev_start AND DATE(`work_date`) <= :prev_end
#                 GROUP BY `자재번호`
#             """
#             prev = db.execute(
#                 text(sql_prev), {**params, "prev_start": str(prev_start), "prev_end": str(prev_end)}
#             ).mappings().all()
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
#                 SELECT DAYOFWEEK(`work_date`) AS dow,
#                        COUNT(*) AS total,
#                        SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
#                        SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DAYOFWEEK(`work_date`)
#                 ORDER BY dow
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [
#                 {"dow": int(r["dow"]), "total": int(r["total"] or 0), "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)}
#                 for r in rows
#             ]
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
#                   SELECT `process` AS proc, COUNT(*) AS cnt, COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)),0) AS prod
#                   FROM {self.TABLE}
#                   WHERE {where_sql}
#                   GROUP BY `process`
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
#                 SELECT `process` AS proc,
#                        SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
#                        SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
#                        COUNT(*) AS total
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `process`
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             out = []
#             for r in rows:
#                 day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
#                 total = int(r["total"] or 0)
#                 ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
#                 imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
#                 out.append(
#                     {"proc": r["proc"], "day": day, "night": night, "total": total, "ratioNightPerDay": ratio, "imbalance": imbalance}
#                 )
#             top_n = getattr(req, "topN", 5) or 5
#             out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
#             return out[:top_n]
#         finally:
#             db.close()

#     def get_intensity_by_machine(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             top_n = getattr(req, "topN", 5) or 5
#             sql = f"""
#                 SELECT t.machine, t.cnt, t.prod,
#                        CASE WHEN t.prod>0 THEN ROUND(t.cnt/(t.prod/1000.0),3) ELSE 0 END AS intensity
#                 FROM (
#                   SELECT `equipment` AS machine, COUNT(*) AS cnt, COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)),0) AS prod
#                   FROM {self.TABLE}
#                   WHERE {where_sql}
#                   GROUP BY `equipment`
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
#                 SELECT `equipment` AS machine,
#                        SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
#                        SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
#                        COUNT(*) AS total
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY `equipment`
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             out = []
#             for r in rows:
#                 day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
#                 total = int(r["total"] or 0)
#                 ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
#                 imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
#                 out.append(
#                     {"machine": r["machine"], "day": day, "night": night, "total": total, "ratioNightPerDay": ratio, "imbalance": imbalance}
#                 )
#             top_n = getattr(req, "topN", 5) or 5
#             out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
#             return out[:top_n]
#         finally:
#             db.close()

#     def get_anomaly_days(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DATE(`work_date`) AS d, COUNT(*) AS c
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 GROUP BY DATE(`work_date`)
#                 ORDER BY d
#             """
#             days = [dict(r) for r in db.execute(text(sql), params).mappings().all()]
#             if not days:
#                 return []
#             c_vals = [int(x["c"]) for x in days]
#             n = len(c_vals)
#             mean_v = sum(c_vals) / n
#             var = sum((x - mean_v) ** 2 for x in c_vals) / n
#             std = (var ** 0.5) if var > 0 else 0.0

#             out = []
#             for d in days:
#                 c = int(d["c"])
#                 z = (c - mean_v) / std if std > 0 else 0.0
#                 if z >= 2.0:
#                     out.append(
#                         {"date": str(d["d"]), "count": c, "z": round(z, 2), "avg": round(mean_v, 2), "std": round(std, 2)}
#                     )
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
#                         LIMIT :top_n
#                     ) t
#                 """
#                 top_sum = int(db.execute(text(sql_top), {**params, "top_n": top_n}).scalar() or 0)
#                 pct = round((top_sum / total) * 100.0, 2) if total > 0 else 0.0
#                 return {"topSum": top_sum, "total": total, "sharePct": pct}

#             return {"part": share_by("`자재번호`"), "item": share_by("`검사항목명`")}
#         finally:
#             db.close()

#     # ---------------- 옵션 ----------------
#     def list_factories(self, req):
#         db: Session = next(get_db())
#         try:
#             where, params = [], {}
#             if getattr(req, "start_date", None):
#                 where.append("`work_date` >= :start_date")
#                 params["start_date"] = req.start_date
#             if getattr(req, "end_date", None):
#                 where.append("`work_date` < DATE_ADD(:end_date, INTERVAL 1 DAY)")
#                 params["end_date"] = req.end_date
#             if not where:
#                 where.append("1=1")
#             where_sql = " AND ".join(where)
#             sql = f"""
#                 SELECT DISTINCT `plant` AS v
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND `plant` IS NOT NULL AND `plant` <> ''
#                 ORDER BY v
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [r["v"] for r in rows]
#         finally:
#             db.close()

#     def list_processes(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DISTINCT `process` AS v
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND `process` IS NOT NULL AND `process` <> ''
#                 ORDER BY v
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [r["v"] for r in rows]
#         finally:
#             db.close()

#     def list_equipments(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DISTINCT `equipment` AS v
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND `equipment` IS NOT NULL AND `equipment` <> ''
#                 ORDER BY v
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [r["v"] for r in rows]
#         finally:
#             db.close()

#     def list_parts(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DISTINCT `자재번호` AS v
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND `자재번호` IS NOT NULL AND `자재번호` <> ''
#                 ORDER BY v
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [r["v"] for r in rows]
#         finally:
#             db.close()

#     def list_items(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where(req)
#             sql = f"""
#                 SELECT DISTINCT `검사항목명` AS v
#                 FROM {self.TABLE}
#                 WHERE {where_sql} AND `검사항목명` IS NOT NULL AND `검사항목명` <> ''
#                 ORDER BY v
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [r["v"] for r in rows]
#         finally:
#             db.close()

#     def list_years(self, req):
#         db: Session = next(get_db())
#         try:
#             where, params = [], {}
#             if getattr(req, "factory", None):
#                 where.append("`plant` = :factory")
#                 params["factory"] = req.factory
#             if getattr(req, "process", None):
#                 where.append("`process` = :process")
#                 params["process"] = req.process
#             if getattr(req, "partNo", None):
#                 where.append("`자재번호` LIKE :partNo")
#                 params["partNo"] = f"%{req.partNo.strip()}%"
#             if getattr(req, "inspType", None):
#                 where.append("`검사구분` = :inspType")
#                 params["inspType"] = req.inspType
#             if getattr(req, "workType", None):
#                 where.append("`작업구분` = :workType")
#                 params["workType"] = req.workType
#             pnm = getattr(req, "partName", None) or getattr(req, "item", None)
#             if pnm:
#                 params["partName"] = f"%{pnm.strip()}%"
#                 where.append("`자재명` LIKE :partName")
#             if getattr(req, "inspectItem", None):
#                 where.append("`검사항목명` LIKE :inspectItem")
#                 params["inspectItem"] = f"%{req.inspectItem.strip()}%"

#             where_sql = " AND ".join(where) if where else "1=1"
#             sql = f"""
#                 SELECT DISTINCT YEAR(`work_date`) AS y
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#                 ORDER BY y DESC
#             """
#             rows = db.execute(text(sql), params).mappings().all()
#             return [int(r["y"]) for r in rows if r["y"] is not None]
#         finally:
#             db.close()

#     # ✅ 최신 보고일의 년/월 및 범위를 반환 (날짜 조건 제외, 나머지 필터는 적용)
#     def latest_month(self, req):
#         db: Session = next(get_db())
#         try:
#             where_sql, params = self._build_where_without_dates(req)
#             sql = f"""
#                 SELECT MAX(DATE(`work_date`)) AS d
#                 FROM {self.TABLE}
#                 WHERE {where_sql}
#             """
#             row = db.execute(text(sql), params).mappings().first()
#             if not row or not row["d"]:
#                 return {
#                     "latestDate": None,
#                     "year": None,
#                     "month": None,
#                     "start": None,
#                     "end": None
#                 }
#             latest_date: date = row["d"]
#             y, m = latest_date.year, latest_date.month
#             start = date(y, m, 1)
#             last_day = calendar.monthrange(y, m)[1]
#             end = date(y, m, last_day)
#             return {
#                 "latestDate": latest_date.isoformat(),
#                 "year": y,
#                 "month": m,
#                 "start": start.isoformat(),
#                 "end": end.isoformat(),
#             }
#         finally:
#             db.close()


# inspection_chart_service = InspectionChartService()

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta, date
from app.config.database import get_db
import re
import calendar


class InspectionChartService:
    # ✅ 실제 테이블
    SCHEMA = "AJIN_newDB"
    TBL = "생산_검사"
    TABLE = "`AJIN_newDB`.`생산_검사`"

    # ---- 내부 캐시 ----
    _cache = {}

    # ---------- 컬럼 존재/선택 ----------
    def _col_exists(self, db: Session, col: str) -> bool:
        key = f"exists::{col}"
        if key in self._cache:
            return self._cache[key]
        sql = """
            SELECT 1
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :s AND TABLE_NAME = :t AND COLUMN_NAME = :c
            LIMIT 1
        """
        ok = db.execute(text(sql), {"s": self.SCHEMA, "t": self.TBL, "c": col}).first() is not None
        self._cache[key] = ok
        return ok

    def _pick_col(self, db: Session, candidates) -> str | None:
        key = f"pick::{','.join(candidates)}"
        if key in self._cache:
            return self._cache[key]
        for c in candidates:
            if self._col_exists(db, c):
                self._cache[key] = f"`{c}`"
                return self._cache[key]
        self._cache[key] = None
        return None

    def _value_col(self, db: Session) -> str:
        """Xn에 표시할 '값' 컬럼 자동 선택 (✅ '생산' 최우선)"""
        key = "value_col"
        if key in self._cache:
            return self._cache[key]
        sql = """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :s AND TABLE_NAME = :t
              AND COLUMN_NAME IN ('생산','검사값','측정값','결과값','값','측정치','측정결과')
            ORDER BY FIELD(COLUMN_NAME,'생산','검사값','측정값','결과값','값','측정치','측정결과')
            LIMIT 1
        """
        row = db.execute(text(sql), {"s": self.SCHEMA, "t": self.TBL}).first()
        if row and row[0]:
            self._cache[key] = f"`{row[0]}`"
        else:
            # 기본값도 '생산' 우선
            self._cache[key] = "`생산`" if self._col_exists(db, "생산") else (
                "`검사값`" if self._col_exists(db, "검사값") else "NULL"
            )
        return self._cache[key]

    # ---------- WHERE ----------
    def _build_where(self, req):
        where, params = [], {}

        def has(v):
            if v is None:
                return False
            if isinstance(v, str):
                s = v.strip()
                return s != "" and s.lower() != "string"
            return True

        if has(getattr(req, "start_date", None)):
            where.append("`work_date` >= :start_date")
            params["start_date"] = req.start_date
        if has(getattr(req, "end_date", None)):
            where.append("`work_date` < DATE_ADD(:end_date, INTERVAL 1 DAY)")
            params["end_date"] = req.end_date

        if has(getattr(req, "factory", None)):
            where.append("`plant` = :factory")
            params["factory"] = req.factory
        if has(getattr(req, "process", None)):
            where.append("`process` = :process")
            params["process"] = req.process
        if has(getattr(req, "equipment", None)):
            where.append("`equipment` = :equipment")
            params["equipment"] = req.equipment
        if has(getattr(req, "workType", None)):
            where.append("`작업구분` = :workType")
            params["workType"] = req.workType
        if has(getattr(req, "inspType", None)):
            where.append("`검사구분` = :inspType")
            params["inspType"] = req.inspType
        if has(getattr(req, "shiftType", None)):
            where.append("`주야구분` = :shiftType")
            params["shiftType"] = req.shiftType
        if has(getattr(req, "partNo", None)):
            where.append("`자재번호` LIKE :partNo")
            params["partNo"] = f"%{req.partNo.strip()}%"

        # 품명(=자재명)
        part_name = getattr(req, "partName", None) or getattr(req, "item", None)
        if has(part_name):
            params["partName"] = f"%{part_name.strip()}%"
            where.append("`자재명` LIKE :partName")

        # 검사항목명
        inspect_item = getattr(req, "inspectItem", None)
        if has(inspect_item):
            params["inspectItem"] = f"%{inspect_item.strip()}%"
            where.append("`검사항목명` LIKE :inspectItem")

        if not where:
            where.append("1=1")
        return " AND ".join(where), params

    # ✅ 날짜 조건을 제외한 WHERE (최신 달 계산용)
    def _build_where_without_dates(self, req):
        class _Dummy:
            pass
        dummy = _Dummy()
        for f in ["factory", "process", "equipment", "workType", "inspType",
                  "shiftType", "partNo", "partName", "item", "inspectItem"]:
            setattr(dummy, f, getattr(req, f, None))
        return self._build_where(dummy)

    # ---------------- 공통: 스펙 파싱 ----------------
    def _parse_spec_numbers(self, s: str):
        if not s:
            return (None, None, None)
        try:
            txt = s.replace("㎜", "mm").replace("＋", "+").replace("－", "-").strip()

            m = re.search(r"([+-]?\d+(?:\.\d+)?)\s*±\s*([+-]?\d+(?:\.\d+)?)", txt)
            if m:
                nom = float(m.group(1)); tol = float(m.group(2))
                return (nom, nom - tol, nom + tol)

            m = re.search(r"([+-]?\d+(?:\.\d+)?)[^\d+-]+([+]\s*\d+(?:\.\d+)?)\s*mm?\s*이내", txt, re.IGNORECASE)
            if m:
                nom = float(m.group(1)); up = float(m.group(2).replace("+",""))
                return (nom, None, nom + up)

            m = re.search(r"([+-]?\d+(?:\.\d+)?)", txt)
            if m:
                nom = float(m.group(1))
                return (nom, None, None)
        except Exception:
            pass
        return (None, None, None)

    # =========================================================
    # A. 일자별 Xn 표 (주/야 헤더 + X1~Xn + 작업구분 라벨)
    # =========================================================
    def _short_work(self, s: str) -> str:
        if not s:
            return ""
        s = str(s)
        if s.startswith("초"):
            return "초"
        if s.startswith("중"):
            return "중"
        if s.startswith("종"):
            return "종"
        return s

    def get_xn_daily(self, req):
        """
        응답:
        {
          "cols": ["X1","X2",...],
          "days": ["YYYY-MM-DD", ...],
          "shifts": ["주간","야간", ...],
          "workHeaders": { "YYYY-MM-DD": { "주간": {"X1":"초",...}, "야간": {...} } },
          "tables": {
             "YYYY-MM-DD": [
               { "NO":1, "검사순번":1, "검사항목명":"...", "검사내용":"...",
                 "nominal":..., "lsl":..., "usl":...,
                 "주간":{"X1":..., "X2":...}, "야간":{"X1":..., ...}, "평균": ... },
               ...
             ]
          },
          "dayList": [ { "d":"YYYY-MM-DD", "equipment":"...", "partNo":"..." }, ... ]
        }
        """
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)

            # 동적 컬럼
            date_col = "`work_date`"
            item_col = "`검사항목명`" if self._col_exists(db, "검사항목명") else None

            # spec(검사내용) 후보
            spec_col = None
            for c in ["검사내용", "기준", "규격", "판정기준", "상세", "내용", "비고"]:
                if self._col_exists(db, c):
                    spec_col = f"`{c}`"
                    break

            # 작업순번(=Xn 시퀀스)
            step_col = None
            for c in ["작업순번", "op_seq", "seq", "검사순번", "검사순서"]:
                if self._col_exists(db, c):
                    step_col = f"`{c}`"
                    break
            if not step_col:
                step_col = "1"

            # 검사순번(행 정렬용)
            insp_col = None
            for c in ["검사순번", "검사순서", "insp_seq"]:
                if self._col_exists(db, c):
                    insp_col = f"`{c}`"
                    break

            shift_col = "`주야구분`" if self._col_exists(db, "주야구분") else "''"
            work_col = "`작업구분`" if self._col_exists(db, "작업구분") else "NULL"

            val_col = self._value_col(db)

            # 보고일 목록
            sql_days = f"""
                SELECT DATE({date_col}) AS d
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE({date_col})
                ORDER BY d
            """
            days = [str(r["d"]) for r in db.execute(text(sql_days), params).mappings().all()]

            # ✅ 날짜별 대표 설비/품번(최빈값; 없으면 NULL)
            sql_day_meta = f"""
                WITH b AS (
                    SELECT DATE({date_col}) AS d,
                           COALESCE(`equipment`,'') AS eq,
                           COALESCE(`자재번호`,'')  AS part
                    FROM {self.TABLE}
                    WHERE {where_sql}
                ),
                eqm AS (
                    SELECT d, eq,
                           ROW_NUMBER() OVER (PARTITION BY d ORDER BY COUNT(*) DESC, eq) AS rn
                    FROM b WHERE eq <> ''
                    GROUP BY d, eq
                ),
                pm AS (
                    SELECT d, part,
                           ROW_NUMBER() OVER (PARTITION BY d ORDER BY COUNT(*) DESC, part) AS rn
                    FROM b WHERE part <> ''
                    GROUP BY d, part
                )
                SELECT x.d,
                       (SELECT eq   FROM eqm WHERE eqm.d = x.d AND eqm.rn = 1)   AS equipment,
                       (SELECT part FROM pm  WHERE pm.d  = x.d AND pm.rn  = 1)   AS partNo
                FROM (SELECT DISTINCT d FROM b) x
                ORDER BY x.d
            """
            day_list_rows = db.execute(text(sql_day_meta), params).mappings().all()
            day_list = [{"d": str(r["d"]), "equipment": r["equipment"], "partNo": r["partNo"]} for r in day_list_rows]

            # ✅ Xn 최대: 프론트와 동일한 seq 규칙으로 계산한 MAX(seq)
            sql_n = f"""
                WITH base AS (
                  SELECT
                    CASE
                      WHEN {step_col} REGEXP '^[0-9]+$' THEN CAST({step_col} AS UNSIGNED)
                      ELSE DENSE_RANK() OVER (
                        PARTITION BY DATE({date_col}),
                                     COALESCE({item_col},''),
                                     COALESCE({spec_col if spec_col else "''"},''),
                                     COALESCE({shift_col},'')
                        ORDER BY COALESCE({step_col},'')
                      )
                    END AS seq
                  FROM {self.TABLE}
                  WHERE {where_sql}
                )
                SELECT COALESCE(MAX(seq),0) FROM base
            """
            max_n = int(db.execute(text(sql_n), params).scalar() or 0)
            max_n = max_n if max_n > 0 else 1
            max_n = min(max_n, 40)  # 상한 완화
            cols = [f"X{i}" for i in range(1, max_n + 1)]

            # spec/항목 없으면 빈 결과
            if not item_col:
                return {"cols": cols, "days": days, "shifts": [], "workHeaders": {}, "tables": {}, "dayList": day_list}
            spec_expr = f"COALESCE({spec_col},'')" if spec_col else "''"
            item_expr = f"COALESCE({item_col},'')"

            # insp_seq 식
            insp_seq_expr = (
                f"""
                CASE
                  WHEN {insp_col} REGEXP '^[0-9]+$' THEN CAST({insp_col} AS UNSIGNED)
                  ELSE DENSE_RANK() OVER (
                         PARTITION BY DATE({date_col})
                         ORDER BY COALESCE({insp_col},''), {item_expr}, {spec_expr}
                       )
                END
                """ if insp_col else
                f"DENSE_RANK() OVER (PARTITION BY DATE({date_col}) ORDER BY {item_expr}, {spec_expr})"
            )

            # 기본 집계(일자·항목·스펙·주야·seq)
            sql_agg = f"""
                WITH base AS (
                  SELECT
                    DATE({date_col}) AS d,
                    {item_expr} AS item,
                    {spec_expr} AS spec,
                    COALESCE({shift_col},'') AS shift,
                    COALESCE({work_col},'')  AS work,
                    CAST({val_col} AS DECIMAL(20,6)) AS val,
                    CASE
                      WHEN {step_col} REGEXP '^[0-9]+$' THEN CAST({step_col} AS UNSIGNED)
                      ELSE DENSE_RANK() OVER (
                          PARTITION BY DATE({date_col}), {item_expr}, {spec_expr}, COALESCE({shift_col},'')
                          ORDER BY COALESCE({step_col},'')
                      )
                    END AS seq,
                    {insp_seq_expr} AS insp_no
                  FROM {self.TABLE}
                  WHERE {where_sql}
                ),
                agg AS (
                  SELECT d, item, spec, shift, seq, AVG(val) AS avg_val
                  FROM base
                  GROUP BY d, item, spec, shift, seq
                ),
                insp_min AS (
                  SELECT d, item, spec, MIN(insp_no) AS insp_no
                  FROM base
                  GROUP BY d, item, spec
                ),
                work_mode AS (
                  SELECT d, shift, seq, work,
                         ROW_NUMBER() OVER (PARTITION BY d, shift, seq ORDER BY COUNT(*) DESC, work) AS rn
                  FROM base
                  WHERE work IS NOT NULL AND work <> ''
                  GROUP BY d, shift, seq, work
                )
                SELECT a.d, a.item, a.spec, a.shift, a.seq, a.avg_val,
                       wm.work AS work_label,
                       im.insp_no
                FROM agg a
                LEFT JOIN work_mode wm
                  ON a.d = wm.d AND a.shift = wm.shift AND a.seq = wm.seq AND wm.rn = 1
                LEFT JOIN insp_min im
                  ON a.d = im.d AND a.item = im.item AND a.spec = im.spec
                ORDER BY a.d, im.insp_no, a.item, a.spec, a.shift, a.seq
            """
            recs = [dict(r) for r in db.execute(text(sql_agg), params).mappings().all()]

            # shifts 정렬(주간, 야간 우선)
            shift_order = []
            for r in recs:
                s = r["shift"] or ""
                if s not in shift_order:
                    shift_order.append(s)
            order_pref = ["주간", "야간"]
            shift_order.sort(key=lambda x: (order_pref.index(x) if x in order_pref else len(order_pref), x))

            # 일자별 헤더 라벨/테이블 구성
            work_headers = {}
            tables = {}

            # (d,item,spec) -> row
            rowmap = {}

            for r in recs:
                d = str(r["d"])
                item = (r["item"] or "").strip()
                spec = (r["spec"] or "").strip()
                shift = (r["shift"] or "").strip()
                seq = int(r["seq"] or 0)
                insp_no = int(r["insp_no"] or 0) if r["insp_no"] is not None else None
                val = float(r["avg_val"]) if r["avg_val"] is not None else None
                xn = f"X{seq}"
                if seq < 1 or seq > max_n:
                    continue

                if r.get("work_label"):
                    work_headers.setdefault(d, {}).setdefault(shift, {})[xn] = self._short_work(r["work_label"])

                tables.setdefault(d, [])
                key = (d, item, spec)
                if key not in rowmap:
                    # ✅ 스펙 파싱(명목/LSL/USL) — 정상 범위를 프론트로 전달
                    nom, lsl, usl = self._parse_spec_numbers(spec)
                    row = {
                        "NO": 0,
                        "검사항목명": item,
                        "검사내용": spec,
                        "검사순번": insp_no,
                        "nominal": nom,
                        "lsl": lsl,
                        "usl": usl,
                    }
                    for s in shift_order:
                        row[s] = {}
                    row["평균"] = None
                    tables[d].append(row)
                    rowmap[key] = row
                row = rowmap[key]
                row["검사순번"] = insp_no if insp_no is not None else row.get("검사순번")
                row.setdefault(shift, {})[xn] = val

            # 일자별 정렬(검사순번 asc) + NO/평균 계산
            for d in tables.keys():
                tables[d].sort(
                    key=lambda rw: (
                        rw.get("검사순번") if rw.get("검사순번") is not None else 10**9,
                        rw.get("검사항목명") or "",
                        rw.get("검사내용") or "",
                    )
                )
                for idx, row in enumerate(tables[d], start=1):
                    row["NO"] = idx
                    vals = []
                    for s in shift_order:
                        for c in cols:
                            v = row.get(s, {}).get(c, None)
                            if v is not None:
                                try:
                                    vals.append(float(v))
                                except Exception:
                                    pass
                    row["평균"] = round(sum(vals) / len(vals), 6) if vals else None

            return {
                "cols": cols,
                "days": days,
                "shifts": shift_order,
                "workHeaders": work_headers,
                "tables": tables,
                "dayList": day_list,
            }
        finally:
            db.close()

    # =========================================================
    # B. Xn 그룹 시리즈 (기존)
    # =========================================================
    def _normalize_group_by(self, gb: str):
        if not gb:
            return None
        m = {
            "partno": "`자재번호`",
            "part": "`자재번호`",
            "part_no": "`자재번호`",
            "partname": "`자재명`",
            "partName": "`자재명`",
            "shift": "`주야구분`",
            "shifttype": "`주야구분`",
            "shiftType": "`주야구분`",
            "insp": "`검사구분`",
            "insptype": "`검사구분`",
            "inspType": "`검사구분`",
            "item": "`검사항목명`",
            "spec": "`검사내용`",
        }
        return m.get(str(gb).replace(" ", "").lower())

    def get_xn_series(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            val_col = self._value_col(db)

            group_col = self._normalize_group_by(getattr(req, "groupBy", None))
            if not group_col:
                return {"groupBy": None, "cols": [], "rows": []}
            if group_col == "`검사내용`":
                spec = None
                for c in ["검사내용", "기준", "규격", "판정기준", "상세", "내용", "비고"]:
                    if self._col_exists(db, c):
                        spec = f"`{c}`"
                        break
                group_col = spec or "''"

            step_col = None
            for c in ["작업순번", "검사순번", "검사순서", "op_seq", "seq"]:
                if self._col_exists(db, c):
                    step_col = f"`{c}`"
                    break
            if not step_col:
                step_col = "1"

            # 상한 20 그대로 유지
            sql_n = f"SELECT COUNT(DISTINCT {step_col}) FROM {self.TABLE} WHERE {where_sql}"
            max_n = int(db.execute(text(sql_n), params).scalar() or 0)
            max_n = min(max_n if max_n > 0 else 1, 20)
            cols = [f"X{i}" for i in range(1, max_n + 1)]
            top_n = getattr(req, "topN", 5) or 5

            sql_series = f"""
                WITH base AS (
                    SELECT
                        {group_col} AS grp,
                        CAST({val_col} AS DECIMAL(20,6)) AS val,
                        {step_col} AS step_raw
                    FROM {self.TABLE}
                    WHERE {where_sql}
                ),
                topgrp AS (
                    SELECT grp
                    FROM base
                    WHERE grp IS NOT NULL AND grp <> ''
                    GROUP BY grp
                    ORDER BY COUNT(*) DESC
                    LIMIT :top_n
                ),
                ranked AS (
                    SELECT
                        b.grp,
                        CASE
                          WHEN b.step_raw REGEXP '^[0-9]+$' THEN CAST(b.step_raw AS UNSIGNED)
                          ELSE DENSE_RANK() OVER (PARTITION BY b.grp ORDER BY COALESCE(b.step_raw,''))
                        END AS seq,
                        b.val
                    FROM base b
                    JOIN topgrp t ON b.grp = t.grp
                )
                SELECT grp, seq, AVG(val) AS avg_val
                FROM ranked
                GROUP BY grp, seq
                ORDER BY grp, seq
            """
            recs = [dict(r) for r in db.execute(text(sql_series), {**params, "top_n": top_n}).mappings().all()]

            series_map = {}
            for r in recs:
                g = r["grp"]
                n = int(r["seq"])
                v = float(r["avg_val"]) if r["avg_val"] is not None else None
                series_map.setdefault(g, {c: None for c in cols})
                if 1 <= n <= max_n:
                    series_map[g][f"X{n}"] = v

            out_rows = [{"label": g, **series_map[g]} for g in series_map.keys()]
            return {"groupBy": group_col, "cols": cols, "rows": out_rows}
        finally:
            db.close()

    # =========================================================
    # C. 숫자형(실측값) 검사항목 — 일자별 추이
    # =========================================================
    def get_numeric_trend(self, req):
        """
        스펙(텍스트)에 숫자가 포함된 (검사항목명, 스펙) TopN 대해 일자별 평균 실측값
        """
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            val_col = self._value_col(db)
            top_n = getattr(req, "topN", 5) or 5

            item_col = "`검사항목명`" if self._col_exists(db, "검사항목명") else None
            spec_col = None
            for c in ["검사내용", "기준", "규격", "판정기준", "상세", "내용", "비고"]:
                if self._col_exists(db, c):
                    spec_col = f"`{c}`"
                    break
            if not (item_col and spec_col):
                return {"dates": [], "series": []}

            sql_days = f"""
                SELECT DATE(`work_date`) AS d
                FROM {self.TABLE}
                WHERE {where_sql} AND {spec_col} REGEXP '[0-9]'
                GROUP BY DATE(`work_date`)
                ORDER BY d
            """
            days = [str(r["d"]) for r in db.execute(text(sql_days), params).mappings().all()]
            if not days:
                return {"dates": [], "series": []}

            sql_avg = f"""
                WITH base AS (
                  SELECT DATE(`work_date`) AS d,
                         COALESCE({item_col},'') AS item,
                         COALESCE({spec_col},'') AS spec,
                         CAST({val_col} AS DECIMAL(20,6)) AS val
                  FROM {self.TABLE}
                  WHERE {where_sql} AND {spec_col} REGEXP '[0-9]'
                )
                SELECT b.d, b.item, b.spec, AVG(b.val) AS avg_val
                FROM base b
                JOIN (
                    SELECT item, spec
                    FROM (
                      SELECT COALESCE({item_col},'') AS item,
                             COALESCE({spec_col},'') AS spec,
                             COUNT(*) AS c
                      FROM {self.TABLE}
                      WHERE {where_sql} AND {spec_col} REGEXP '[0-9]'
                      GROUP BY COALESCE({item_col},''), COALESCE({spec_col},'')
                      ORDER BY c DESC
                      LIMIT :top_n
                    ) t
                ) tp ON b.item = tp.item AND b.spec = tp.spec
                GROUP BY b.item, b.spec, b.d
                ORDER BY b.item, b.spec, b.d
            """
            avg_rows = db.execute(text(sql_avg), {**params, "top_n": top_n}).mappings().all()

            # 레이블/값 매핑
            top_pairs = {}
            for r in avg_rows:
                top_pairs[(r["item"], r["spec"])] = True

            label_map = {}
            val_map = {}
            for (item, spec) in top_pairs.keys():
                item_s = (item or "").strip()
                spec_s = (spec or "").strip()
                label = f"{item_s} | {spec_s}" if spec_s else item_s
                label_map[(item, spec)] = label
                val_map[label] = {d: None for d in days}

            spec_nums = {}
            for (item, spec), label in label_map.items():
                spec_nums[label] = self._parse_spec_numbers(spec)

            for r in avg_rows:
                item = r["item"]
                spec = r["spec"]
                label = label_map.get((item, spec))
                d = str(r["d"])
                v = float(r["avg_val"]) if r["avg_val"] is not None else None
                if label in val_map and d in val_map[label]:
                    val_map[label][d] = v

            series = []
            for label, dayvals in val_map.items():
                series.append({
                    "label": label,
                    "data": [dayvals[d] for d in days],
                    "nominal": spec_nums.get(label, (None,None,None))[0],
                    "lsl": spec_nums.get(label, (None,None,None))[1],
                    "usl": spec_nums.get(label, (None,None,None))[2],
                })

            return {"dates": days, "series": series}
        finally:
            db.close()

    # =========================================================
    # D. 기존 대시보드(생략 없이 유지)
    # =========================================================
    def get_dashboard(self, req):
        return {
            "kpis": self.get_kpis(req),
            "byItem": self.get_by_item(req),
            "trend": self.get_trend(req),
            "stacked": self.get_stacked(req),
            "byPart": self.get_by_part(req),
            "byProcess": self.get_by_process(req),
            "machines": self.get_by_machine(req),
            "throughput": self.get_throughput(req),
            "shift": self.get_shift(req),
            "momentum": self.get_momentum_parts(req),
            "weekdayProfile": self.get_weekday_profile(req),
            "machIntensity": self.get_intensity_by_machine(req),
            "machShiftImbalance": self.get_shift_imbalance_machine(req),
            "anomalyDays": self.get_anomaly_days(req),
        }

    def get_kpis(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT
                    COUNT(*) AS total_cnt,
                    COUNT(DISTINCT `자재번호`) AS part_kinds,
                    COUNT(DISTINCT `검사항목명`) AS item_kinds,
                    COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)), 0) AS prod_sum
                FROM {self.TABLE}
                WHERE {where_sql}
            """
            k = db.execute(text(sql), params).mappings().first() or {}
            total = int(k.get("total_cnt", 0) or 0)
            part_kinds = int(k.get("part_kinds", 0) or 0)
            item_kinds = int(k.get("item_kinds", 0) or 0)
            prod_sum = float(k.get("prod_sum", 0) or 0.0)

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

            sql_tr = f"""
                SELECT DATE(`work_date`) AS d, COUNT(*) AS c
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`work_date`)
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

    def get_trend(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DATE(`work_date`) AS d, COUNT(*) AS cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`work_date`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [{"date": str(r["d"]), "count": int(r["cnt"] or 0)} for r in rows]
        finally:
            db.close()

    def get_stacked(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT
                    DATE(`work_date`) AS d,
                    SUM(CASE WHEN `검사구분` = '자동검사' THEN 1 ELSE 0 END) AS auto_cnt,
                    SUM(CASE WHEN `검사구분` LIKE '자주%%' THEN 1 ELSE 0 END) AS self_cnt,
                    SUM(CASE WHEN `검사구분` NOT IN ('자동검사') AND `검사구분` NOT LIKE '자주%%' THEN 1 ELSE 0 END) AS other_cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`work_date`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [
                {"date": str(r["d"]), "auto": int(r["auto_cnt"] or 0), "self": int(r["self_cnt"] or 0), "other": int(r["other_cnt"] or 0)}
                for r in rows
            ]
        finally:
            db.close()

    def get_by_part(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 5) or 5
            sql = f"""
                SELECT `자재번호` AS v, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `자재번호`
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
                SELECT `process` AS proc, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `process`
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
                SELECT `equipment` AS machine, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `equipment`
                ORDER BY qty DESC
                LIMIT :top_n
            """
            rows = db.execute(text(sql), {**params, "top_n": top_n}).mappings().all()
            return [dict(r) for r in rows]
        finally:
            db.close()

    def get_throughput(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DATE(`work_date`) AS d,
                       COUNT(*) AS cnt,
                       COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)), 0) AS prod
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`work_date`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [
                {
                    "date": str(r["d"]),
                    "count": int(r["cnt"] or 0),
                    "prod": float(r["prod"] or 0.0),
                    "intensity": round((int(r["cnt"] or 0)) / (float(r["prod"] or 0.0) / 1000.0), 3)
                    if float(r["prod"] or 0.0) > 0
                    else 0.0,
                }
                for r in rows
            ]
        finally:
            db.close()

    def get_shift(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DATE(`work_date`) AS d,
                       SUM(CASE WHEN `주야구분` = '주간' THEN 1 ELSE 0 END) AS day_cnt,
                       SUM(CASE WHEN `주야구분` = '야간' THEN 1 ELSE 0 END) AS night_cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`work_date`)
                ORDER BY d
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [{"date": str(r["d"]), "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)} for r in rows]
        finally:
            db.close()

    def get_momentum_parts(self, req):
        db: Session = next(get_db())
        try:
            end_str = getattr(req, "end_date", None)
            end_dt = datetime.strptime(end_str, "%Y-%m-%d") if end_str else datetime.utcnow()
            recent_start = (end_dt - timedelta(days=14)).date()
            prev_start = (end_dt - timedelta(days=28)).date()
            prev_end = (end_dt - timedelta(days=14)).date()

            where_sql, params = self._build_where(req)
            sql_recent = f"""
                SELECT `자재번호` AS partNo, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql} AND DATE(`work_date`) > :recent_start AND DATE(`work_date`) <= :end_date_cut
                GROUP BY `자재번호`
            """
            recent = db.execute(
                text(sql_recent),
                {**params, "recent_start": str(recent_start), "end_date_cut": end_dt.date().isoformat()},
            ).mappings().all()
            rmap = {r["partNo"]: int(r["qty"] or 0) for r in recent}

            sql_prev = f"""
                SELECT `자재번호` AS partNo, COUNT(*) AS qty
                FROM {self.TABLE}
                WHERE {where_sql} AND DATE(`work_date`) >= :prev_start AND DATE(`work_date`) <= :prev_end
                GROUP BY `자재번호`
            """
            prev = db.execute(
                text(sql_prev), {**params, "prev_start": str(prev_start), "prev_end": str(prev_end)}
            ).mappings().all()
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
                SELECT DAYOFWEEK(`work_date`) AS dow,
                       COUNT(*) AS total,
                       SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
                       SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DAYOFWEEK(`work_date`)
                ORDER BY dow
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [
                {"dow": int(r["dow"]), "total": int(r["total"] or 0), "day": int(r["day_cnt"] or 0), "night": int(r["night_cnt"] or 0)}
                for r in rows
            ]
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
                  SELECT `process` AS proc, COUNT(*) AS cnt, COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)),0) AS prod
                  FROM {self.TABLE}
                  WHERE {where_sql}
                  GROUP BY `process`
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
                SELECT `process` AS proc,
                       SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
                       SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
                       COUNT(*) AS total
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `process`
            """
            rows = db.execute(text(sql), params).mappings().all()
            out = []
            for r in rows:
                day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
                total = int(r["total"] or 0)
                ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
                imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
                out.append(
                    {"proc": r["proc"], "day": day, "night": night, "total": total, "ratioNightPerDay": ratio, "imbalance": imbalance}
                )
            top_n = getattr(req, "topN", 5) or 5
            out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
            return out[:top_n]
        finally:
            db.close()

    def get_intensity_by_machine(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            top_n = getattr(req, "topN", 5) or 5
            sql = f"""
                SELECT t.machine, t.cnt, t.prod,
                       CASE WHEN t.prod>0 THEN ROUND(t.cnt/(t.prod/1000.0),3) ELSE 0 END AS intensity
                FROM (
                  SELECT `equipment` AS machine, COUNT(*) AS cnt, COALESCE(SUM(COALESCE(`생산수량`,`양품수량`,0)),0) AS prod
                  FROM {self.TABLE}
                  WHERE {where_sql}
                  GROUP BY `equipment`
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
                SELECT `equipment` AS machine,
                       SUM(CASE WHEN `주야구분`='주간' THEN 1 ELSE 0 END) AS day_cnt,
                       SUM(CASE WHEN `주야구분`='야간' THEN 1 ELSE 0 END) AS night_cnt,
                       COUNT(*) AS total
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY `equipment`
            """
            rows = db.execute(text(sql), params).mappings().all()
            out = []
            for r in rows:
                day, night = int(r["day_cnt"] or 0), int(r["night_cnt"] or 0)
                total = int(r["total"] or 0)
                ratio = round(night / day, 2) if day > 0 else (night if night > 0 else 0)
                imbalance = round(abs(night - day) / total, 3) if total > 0 else 0
                out.append(
                    {"machine": r["machine"], "day": day, "night": night, "total": total, "ratioNightPerDay": ratio, "imbalance": imbalance}
                )
            top_n = getattr(req, "topN", 5) or 5
            out.sort(key=lambda x: (x["imbalance"], x["total"]), reverse=True)
            return out[:top_n]
        finally:
            db.close()

    def get_anomaly_days(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DATE(`work_date`) AS d, COUNT(*) AS c
                FROM {self.TABLE}
                WHERE {where_sql}
                GROUP BY DATE(`work_date`)
                ORDER BY d
            """
            days = [dict(r) for r in db.execute(text(sql), params).mappings().all()]
            if not days:
                return []
            c_vals = [int(x["c"]) for x in days]
            n = len(c_vals)
            mean_v = sum(c_vals) / n
            var = sum((x - mean_v) ** 2 for x in c_vals) / n
            std = (var ** 0.5) if var > 0 else 0.0

            out = []
            for d in days:
                c = int(d["c"])
                z = (c - mean_v) / std if std > 0 else 0.0
                if z >= 2.0:
                    out.append(
                        {"date": str(d["d"]), "count": c, "z": round(z, 2), "avg": round(mean_v, 2), "std": round(std, 2)}
                    )
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
                        LIMIT :top_n
                    ) t
                """
                top_sum = int(db.execute(text(sql_top), {**params, "top_n": top_n}).scalar() or 0)
                pct = round((top_sum / total) * 100.0, 2) if total > 0 else 0.0
                return {"topSum": top_sum, "total": total, "sharePct": pct}

            return {"part": share_by("`자재번호`"), "item": share_by("`검사항목명`")}
        finally:
            db.close()

    # ---------------- 옵션 ----------------
    def list_factories(self, req):
        db: Session = next(get_db())
        try:
            where, params = [], {}
            if getattr(req, "start_date", None):
                where.append("`work_date` >= :start_date")
                params["start_date"] = req.start_date
            if getattr(req, "end_date", None):
                where.append("`work_date` < DATE_ADD(:end_date, INTERVAL 1 DAY)")
                params["end_date"] = req.end_date
            if not where:
                where.append("1=1")
            where_sql = " AND ".join(where)
            sql = f"""
                SELECT DISTINCT `plant` AS v
                FROM {self.TABLE}
                WHERE {where_sql} AND `plant` IS NOT NULL AND `plant` <> ''
                ORDER BY v
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [r["v"] for r in rows]
        finally:
            db.close()

    def list_processes(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DISTINCT `process` AS v
                FROM {self.TABLE}
                WHERE {where_sql} AND `process` IS NOT NULL AND `process` <> ''
                ORDER BY v
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [r["v"] for r in rows]
        finally:
            db.close()

    def list_equipments(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DISTINCT `equipment` AS v
                FROM {self.TABLE}
                WHERE {where_sql} AND `equipment` IS NOT NULL AND `equipment` <> ''
                ORDER BY v
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [r["v"] for r in rows]
        finally:
            db.close()

    def list_parts(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where(req)
            sql = f"""
                SELECT DISTINCT `자재번호` AS v
                FROM {self.TABLE}
                WHERE {where_sql} AND `자재번호` IS NOT NULL AND `자재번호` <> ''
                ORDER BY v
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [r["v"] for r in rows]
        finally:
            db.close()

    def list_items(self, req):
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

    def list_years(self, req):
        db: Session = next(get_db())
        try:
            where, params = [], {}
            if getattr(req, "factory", None):
                where.append("`plant` = :factory")
                params["factory"] = req.factory
            if getattr(req, "process", None):
                where.append("`process` = :process")
                params["process"] = req.process
            if getattr(req, "partNo", None):
                where.append("`자재번호` LIKE :partNo")
                params["partNo"] = f"%{req.partNo.strip()}%"
            if getattr(req, "inspType", None):
                where.append("`검사구분` = :inspType")
                params["inspType"] = req.inspType
            if getattr(req, "workType", None):
                where.append("`작업구분` = :workType")
                params["workType"] = req.workType
            pnm = getattr(req, "partName", None) or getattr(req, "item", None)
            if pnm:
                params["partName"] = f"%{pnm.strip()}%"
                where.append("`자재명` LIKE :partName")
            if getattr(req, "inspectItem", None):
                where.append("`검사항목명` LIKE :inspectItem")
                params["inspectItem"] = f"%{req.inspectItem.strip()}%"

            where_sql = " AND ".join(where) if where else "1=1"
            sql = f"""
                SELECT DISTINCT YEAR(`work_date`) AS y
                FROM {self.TABLE}
                WHERE {where_sql}
                ORDER BY y DESC
            """
            rows = db.execute(text(sql), params).mappings().all()
            return [int(r["y"]) for r in rows if r["y"] is not None]
        finally:
            db.close()

    # ✅ 최신 보고일의 년/월 및 범위를 반환 (날짜 조건 제외, 나머지 필터는 적용)
    def latest_month(self, req):
        db: Session = next(get_db())
        try:
            where_sql, params = self._build_where_without_dates(req)
            sql = f"""
                SELECT MAX(DATE(`work_date`)) AS d
                FROM {self.TABLE}
                WHERE {where_sql}
            """
            row = db.execute(text(sql), params).mappings().first()
            if not row or not row["d"]:
                return {
                    "latestDate": None,
                    "year": None,
                    "month": None,
                    "start": None,
                    "end": None
                }
            latest_date: date = row["d"]
            y, m = latest_date.year, latest_date.month
            start = date(y, m, 1)
            last_day = calendar.monthrange(y, m)[1]
            end = date(y, m, last_day)
            return {
                "latestDate": latest_date.isoformat(),
                "year": y,
                "month": m,
                "start": start.isoformat(),
                "end": end.isoformat(),
            }
        finally:
            db.close()


inspection_chart_service = InspectionChartService()
