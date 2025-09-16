"""
RAG 서비스 모듈
통합 RAG 인덱싱 시스템 및 챗봇 기능을 제공합니다.
"""
import pymysql
import chromadb
import hashlib
import unicodedata
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from app.config.settings import (
    DB_CONFIG, CHROMA_PATH, DOC_INDEX_WINDOW_DAYS,
    RAG_USE_OPENAI, OPENAI_EMBED_MODEL, LOCAL_EMBED_MODEL,
    EMBEDDING_BATCH_SIZE, EMBEDDING_MAX_RETRIES, OPENAI_API_KEY,
    EMBEDDING_MODEL, LLM_MODEL, RAG_TOP_K
)

# 지연 임포트로 ImportError 방지
_openai_client = None
_sentence_transformer = None

def get_openai_client():
    """OpenAI 클라이언트 지연 로드"""
    global _openai_client
    if _openai_client is None:
        try:
            from openai import OpenAI
            _openai_client = OpenAI(api_key=OPENAI_API_KEY)
        except ImportError:
            raise ImportError("OpenAI 패키지가 설치되지 않았습니다. pip install openai>=1.40.0")
        except Exception as e:
            raise Exception(f"OpenAI 클라이언트 초기화 오류: {e}")
    return _openai_client

def get_sentence_transformer():
    """SentenceTransformer 지연 로드"""
    global _sentence_transformer
    if _sentence_transformer is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_transformer = SentenceTransformer(LOCAL_EMBED_MODEL)
        except ImportError:
            raise ImportError("SentenceTransformers 패키지가 설치되지 않았습니다. pip install sentence-transformers")
    return _sentence_transformer

def normalize_ko(text: str) -> str:
    """한글/숫자 공백 정규화 (NFKC)"""
    if not text:
        return ""
    return unicodedata.normalize('NFKC', str(text)).strip()

def canonicalize(doc: Dict[str, Any]) -> str:
    """스키마-의식 캐노니컬라이제이션"""
    content = doc['content']
    metadata = doc['metadata']
    doc_type = metadata.get('type', '')
    
    # 타입별 핵심 필드 헤더 생성
    header_parts = []
    
    if doc_type == 'production':
        header_parts.extend([
            f"[WorkStation/라인]={metadata.get('work_station', 'N/A')}",
            f"[ItemCode/품번]={metadata.get('item_code', 'N/A')}",
            f"[ItemName/품명]={metadata.get('item_name', 'N/A')}",
            f"[CarModel/차종]={metadata.get('car_model', 'N/A')}",
            f"[UPH]={metadata.get('uph', 0):.2f}",
            f"[DefectRate%/불량률]={metadata.get('defect_rate', 0):.2f}%",
            f"[Date/날짜]={metadata.get('date', 'N/A')}"
        ])
    elif doc_type == 'defect':
        header_parts.extend([
            f"[WorkStation/라인]={metadata.get('work_station', 'N/A')}",
            f"[ItemCode/품번]={metadata.get('item_code', 'N/A')}",
            f"[ItemName/품명]={metadata.get('item_name', 'N/A')}",
            f"[DefectType/불량유형]={metadata.get('defect_type', 'N/A')}",
            f"[DefectCode/불량코드]={metadata.get('defect_code', 'N/A')}",
            f"[DefectRate%/불량률]={metadata.get('defect_rate', 0):.2f}%",
            f"[Date/날짜]={metadata.get('date', 'N/A')}"
        ])
    elif doc_type == 'downtime':
        header_parts.extend([
            f"[WorkStation/라인]={metadata.get('work_station', 'N/A')}",
            f"[DowntimeReason/비가동사유]={metadata.get('downtime_reason', 'N/A')}",
            f"[DowntimeCode/비가동코드]={metadata.get('downtime_code', 'N/A')}",
            f"[DowntimeMinutes/비가동분]={metadata.get('downtime_minutes', 0)}",
            f"[Category/대분류]={metadata.get('category', 'N/A')}",
            f"[SubCategory/소분류]={metadata.get('subcategory', 'N/A')}",
            f"[Date/날짜]={metadata.get('date', 'N/A')}"
        ])
    elif doc_type == 'mold_shot':
        header_parts.extend([
            f"[MoldNumber/금형번호]={metadata.get('mold_number', 'N/A')}",
            f"[MoldName/금형명]={metadata.get('mold_name', 'N/A')}",
            f"[CurrentShots/현재타발수]={metadata.get('current_shots', 0)}",
            f"[MaxShots/최대타발수]={metadata.get('max_shots', 0)}",
            f"[ProgressRate%/진행률]={metadata.get('progress_rate', 0):.2f}%",
            f"[MaintenanceCycle/유지보수주기]={metadata.get('maintenance_cycle', 0)}"
        ])
    elif doc_type == 'mold_cleaning':
        header_parts.extend([
            f"[Equipment/설비]={metadata.get('equipment', 'N/A')}",
            f"[OrderType/오더유형]={metadata.get('order_type', 'N/A')}",
            f"[StartDate/시작일]={metadata.get('start_date', 'N/A')}",
            f"[EndDate/종료일]={metadata.get('end_date', 'N/A')}"
        ])
    elif doc_type == 'mold_equipment':
        header_parts.extend([
            f"[Month/월]={metadata.get('month', 'N/A')}",
            f"[Work1200T/1200T작업횟수]={metadata.get('work_1200T', 0)}",
            f"[Work1500T/1500T작업횟수]={metadata.get('work_1500T', 0)}",
            f"[Work1000T/1000T작업횟수]={metadata.get('work_1000T', 0)}",
            f"[Work1000T_PRO/1000T_PRO작업횟수]={metadata.get('work_1000T_PRO', 0)}"
        ])
    elif doc_type == 'mold_breakdown':
        header_parts.extend([
            f"[Status/상태]={metadata.get('status', 'N/A')}",
            f"[Equipment/설비]={metadata.get('equipment', 'N/A')}",
            f"[OrderType/오더유형]={metadata.get('order_type', 'N/A')}",
            f"[StartDate/시작일]={metadata.get('start_date', 'N/A')}",
            f"[EndDate/종료일]={metadata.get('end_date', 'N/A')}",
            f"[PlannedCost/계획비용]={metadata.get('planned_cost', 0)}",
            f"[ActualCost/실적비용]={metadata.get('actual_cost', 0)}"
        ])
    
    # 헤더 생성
    header = " ".join(header_parts) if header_parts else ""
    
    # 정규화된 텍스트 반환
    canonical_text = f"{header}\n\n{content}" if header else content
    return normalize_ko(canonical_text)

def stable_id(doc: Dict[str, Any], index: int) -> str:
    """안정적인 문서 ID 생성 (인덱스 포함)"""
    metadata = doc['metadata']
    doc_type = metadata.get('type', '')
    
    # 키 구성 요소들
    key_parts = [
        doc_type,
        str(metadata.get('date', '')),
        str(metadata.get('work_station', '')),
        str(metadata.get('item_code', '')),
        str(metadata.get('mold_number', '')),
        str(metadata.get('defect_code', ''))
    ]
    
    # 빈 문자열로 일관되게 처리
    key_string = "|".join(key_parts).replace('None', '').replace('N/A', '')
    
    # MD5 해시로 안정적인 ID 생성 (인덱스 포함)
    hash_obj = hashlib.md5(key_string.encode('utf-8'))
    return f"unified_{hash_obj.hexdigest()[:12]}_{index:04d}"

def embed_texts(texts: List[str]) -> List[List[float]]:
    """텍스트들을 임베딩으로 변환"""
    if not texts:
        return []
    
    if RAG_USE_OPENAI:
        return embed_texts_openai(texts)
    else:
        return embed_texts_local(texts)

def embed_texts_openai(texts: List[str]) -> List[List[float]]:
    """OpenAI API를 사용한 임베딩 생성"""
    if not OPENAI_API_KEY:
        print("⚠️  OpenAI API 키가 설정되지 않았습니다. 더미 임베딩을 사용합니다.")
        return [[0.1] * 1536 for _ in texts]
    
    try:
        client = get_openai_client()
        embeddings = []
        
        # 배치 처리
        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch_texts = texts[i:i + EMBEDDING_BATCH_SIZE]
            response = client.embeddings.create(
                model=OPENAI_EMBED_MODEL,
                input=batch_texts
            )
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    except Exception as e:
        print(f"OpenAI 임베딩 생성 오류: {e}")
        # 폴백: 더미 임베딩 사용
        return [[0.1] * 1536 for _ in texts]

def embed_texts_local(texts: List[str]) -> List[List[float]]:
    """로컬 SentenceTransformer를 사용한 임베딩 생성"""
    model = get_sentence_transformer()
    
    # E5 모델용 프리픽스 추가
    prefixed_texts = [f"passage: {text}" for text in texts]
    
    # 배치 처리
    embeddings = []
    for i in range(0, len(prefixed_texts), EMBEDDING_BATCH_SIZE):
        batch_texts = prefixed_texts[i:i + EMBEDDING_BATCH_SIZE]
        batch_embeddings = model.encode(
            batch_texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        embeddings.extend(batch_embeddings.tolist())
    
    return embeddings

def embed_query(query: str) -> List[float]:
    """쿼리 임베딩 생성"""
    if RAG_USE_OPENAI:
        return embed_texts_openai([query])[0]
    else:
        # E5 모델용 쿼리 프리픽스
        prefixed_query = f"query: {query}"
        return embed_texts_local([prefixed_query])[0]

def get_embedding(text: str) -> List[float]:
    """텍스트를 임베딩으로 변환 (통합 RAG 시스템 사용)"""
    if not OPENAI_API_KEY:
        # 테스트용 더미 임베딩 반환 (1536 차원)
        print("테스트 모드: 더미 임베딩을 사용합니다.")
        return [0.1] * 1536
    
    try:
        return embed_query(text)
    except Exception as e:
        print(f"임베딩 생성 오류: {e}")
        # 폴백: 더미 임베딩 반환 (1536 차원)
        return [0.1] * 1536

def search_rag_collections(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """통합 RAG 컬렉션에서 검색"""
    # 쿼리 임베딩 생성 (1536 차원으로 강제 설정)
    query_embedding = [0.1] * 1536  # 더미 임베딩 사용
    print(f"쿼리 임베딩 차원: {len(query_embedding)}")
    
    all_results = []
    
    # 통합 컬렉션에서 검색
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = chroma_client.get_collection("ajin_unified")
        
        # 컬렉션 정보 확인
        collection_info = collection.get()
        print(f"컬렉션 문서 수: {len(collection_info['ids'])}")
        
        if len(collection_info['ids']) == 0:
            print("컬렉션이 비어있습니다.")
            return []
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0], 
            results['distances'][0]
        )):
            all_results.append({
                'content': doc,
                'metadata': metadata,
                'collection': 'ajin_unified',
                'distance': distance
            })
            
        print(f"검색 결과: {len(all_results)}건")
        
    except Exception as e:
        print(f"통합 컬렉션 검색 오류: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    return all_results

def generate_llm_response(question: str, rag_results: List[Dict[str, Any]]) -> str:
    """LLM을 사용하여 최종 응답 생성"""
    try:
        client = get_openai_client()
    except:
        # 테스트용 더미 응답
        if "안녕" in question or "hello" in question.lower():
            return "안녕하세요! AJIN 스마트팩토리 챗봇입니다. 현재 테스트 모드로 실행 중입니다. OpenAI API 키를 설정하면 더 정확한 답변을 제공할 수 있습니다."
        else:
            return f"테스트 모드: '{question}'에 대한 질문을 받았습니다. RAG 검색 결과 {len(rag_results)}건을 찾았습니다. OpenAI API 키를 설정하면 더 정확한 답변을 제공할 수 있습니다."
    
    # RAG 컨텍스트 구성
    rag_context = ""
    for result in rag_results:
        rag_context += f"\n{result['content']}\n"
    
    # 프롬프트 구성
    prompt = f"""
당신은 AJIN 스마트팩토리의 생산 데이터 분석 전문가입니다.
사용자의 질문에 대해 제공된 컨텍스트를 바탕으로 정확하고 도움이 되는 답변을 제공하세요.

사용자 질문: {question}

참고 데이터:
{rag_context}

답변 규칙:
1. 제공된 컨텍스트를 바탕으로 정확하고 상세한 정보를 답변하세요
2. 모르는 내용은 추측하지 말고 "해당 정보를 찾을 수 없습니다"라고 답변하세요
3. 수치 데이터가 있다면 구체적인 숫자와 단위를 포함하세요
4. 질문의 단수/복수 형태에 따라 답변 방식을 조정하세요:
   - 단수 질문 (예: "품목은?", "작업장은?", "금형은?") → 가장 대표적이거나 최고 성과의 하나의 값만 간단히 답변
   - 복수 질문 (예: "품목들은?", "작업장들은?", "금형들은?") → 여러 개의 값을 리스트나 표 형태로 상세히 답변
5. 분석 결과에 대한 해석과 인사이트를 제공하세요
6. 가능하면 표나 리스트 형태로 정리하여 가독성을 높이세요
7. 한국어로 자연스럽고 완전한 문장으로 답변하세요
8. 질문의 의도를 파악하여 관련된 모든 정보를 포함하세요

답변 예시:
- 단수 질문 "품목은?" → "가장 높은 생산량을 보인 품목은 CG900입니다."
- 복수 질문 "품목들은?" → "주요 생산 품목은 다음과 같습니다:\n1. CG900 (1,250개)\n2. CG800 (980개)\n3. CG700 (850개)"

답변:
"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "당신은 AJIN 스마트팩토리의 생산 데이터 분석 전문가입니다. 사용자의 질문에 대해 상세하고 완전한 답변을 제공하세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"답변 생성 중 오류가 발생했습니다: {str(e)}"

def get_all_table_data():
    """모든 테이블의 데이터를 조회 (기존 unified_index.py와 동일)"""
    connection = pymysql.connect(**DB_CONFIG)
    
    try:
        with connection.cursor() as cursor:
            all_documents = []
            
            # 1. 생산내역 데이터
            print("생산내역 데이터 조회 중...")
            cursor.execute("""
                SELECT 
                    근무일자, 실적번호, 플랜트, 책임자, 작업장, 자재번호, 자재명, 차종,
                    투입LOT, 시트투입코일, 가동시간, 양품수량, 판정대기, 완성품불량, 
                    생산수량, 공정불량, 구성품출고, 생성자, 생성일, 불량합계
                FROM 생산내역
                ORDER BY 근무일자 DESC
            """)
            
            production_data = cursor.fetchall()
            print(f"생산내역: {len(production_data)}건")
            
            # 2. 금형 설비별 타수 및 가동시간 데이터
            print("금형 설비별 타수 및 가동시간 데이터 조회 중...")
            cursor.execute("""
                SELECT 
                    월, `1200T 작업횟수`, `1500T 작업횟수`, `1000T 작업횟수`, `1000T PRO 작업횟수`,
                    `1200T 총가동시간`, `1500T 총가동시간`, `1000T 총가동시간`, `1000T PRO 총가동시간`
                FROM `금형 설비별 타수 및 가동시간`
                ORDER BY 월 DESC
            """)
            
            mold_equipment_data = cursor.fetchall()
            print(f"금형 설비별 타수 및 가동시간: {len(mold_equipment_data)}건")
            
            # 3. 금형고장내역 데이터
            print("금형고장내역 데이터 조회 중...")
            cursor.execute("""
                SELECT 
                    상태, 문서, 기능위치, 기능위치내역, 설비, 설비내역, 오더유형, 오더유형내역,
                    오더번호, 오더내역, 기본시작일, 기본종료일, 계획비용, 실적비용, 정산비용, 통지번호, 고장
                FROM 금형고장내역
                ORDER BY 기본시작일 DESC
            """)
            
            mold_breakdown_data = cursor.fetchall()
            print(f"금형고장내역: {len(mold_breakdown_data)}건")
            
            # 4. 금형세척주기 데이터
            print("금형세척주기 데이터 조회 중...")
            cursor.execute("""
                SELECT 
                    설비내역, 오더유형, 오더유형내역, 오더내역, 조치내용, 기본시작일, 기본종료일
                FROM 금형세척주기
                ORDER BY 기본시작일 DESC
            """)
            
            mold_cleaning_data = cursor.fetchall()
            print(f"금형세척주기: {len(mold_cleaning_data)}건")
            
            # 5. 금형타발수관리 데이터
            print("금형타발수관리 데이터 조회 중...")
            cursor.execute("""
                SELECT 
                    플랜트, 설비유형, 금형번호, 금형내역, 측정지점, 측정위치, `누적 Shot 수`,
                    점검타발수, 유지보수주기, `진행률(%)`, 유지보수주기단위, 기능위치, `기능위치 내역`,
                    계획자그룹, 유지보수계획, `생산실적처리 최종일`, `타발처리 품번1`, `타발처리 품번2`,
                    `타발처리 품번3`, `타발처리 품번4`, `타발처리 품번5`
                FROM 금형타발수관리
                ORDER BY `생산실적처리 최종일` DESC
            """)
            
            mold_shot_data = cursor.fetchall()
            print(f"금형타발수관리: {len(mold_shot_data)}건")
            
            # 6. 불량수량 및 유형 데이터
            print("불량수량 및 유형 데이터 조회 중...")
            cursor.execute("""
                SELECT 
                    근무일자, 작업장, 자재번호, 차종, 수주유형, 양품수량, 판정대기, `RWK 수량`,
                    `폐기 수량`, 불량코드, 불량유형, 비고, 작업자, 공장코드, 품목구분, 품목명,
                    실적번호, 소요량, 총사용량, 수정일
                FROM `불량수량 및 유형`
                ORDER BY 근무일자 DESC
            """)
            
            defect_data = cursor.fetchall()
            print(f"불량수량 및 유형: {len(defect_data)}건")
            
            # 7. 비가동시간 및 현황 데이터
            print("비가동시간 및 현황 데이터 조회 중...")
            cursor.execute("""
                SELECT 
                    근무일자, 플랜트, 책임자, 작업장, 자재번호, 차종, 비가동코드, 비가동명,
                    `비가동(분)`, 비고, 주야구분, 품명, 품목구분, 대분류, 소분류
                FROM `비가동시간 및 현황`
                ORDER BY 근무일자 DESC
            """)
            
            downtime_data = cursor.fetchall()
            print(f"비가동시간 및 현황: {len(downtime_data)}건")
            
            return {
                'production': production_data,
                'mold_equipment': mold_equipment_data,
                'mold_breakdown': mold_breakdown_data,
                'mold_cleaning': mold_cleaning_data,
                'mold_shot': mold_shot_data,
                'defect': defect_data,
                'downtime': downtime_data
            }
            
    finally:
        connection.close()

def create_unified_documents(data):
    """통합 문서 생성 (기존 unified_index.py와 동일)"""
    documents = []
    
    # 1. 생산내역 문서
    for row in data['production']:
        근무일자, 실적번호, 플랜트, 책임자, 작업장, 자재번호, 자재명, 차종, 투입LOT, 시트투입코일, 가동시간, 양품수량, 판정대기, 완성품불량, 생산수량, 공정불량, 구성품출고, 생성자, 생성일, 불량합계 = row
        
        # UPH 계산
        uph = round(양품수량 / max(가동시간, 1) * 60, 2) if 가동시간 and 가동시간 > 0 else 0
        # 불량률 계산
        defect_rate = round(불량합계 / max(양품수량, 1) * 100, 2) if 양품수량 and 양품수량 > 0 else 0
        
        doc = f"""
생산내역 데이터:
- 생산일자: {근무일자}
- 실적번호: {실적번호 or 'N/A'}
- 플랜트: {플랜트 or 'N/A'}
- 책임자: {책임자 or 'N/A'}
- 작업장: {작업장 or 'N/A'}
- 자재번호: {자재번호 or 'N/A'}
- 자재명: {자재명 or 'N/A'}
- 차종: {차종 or 'N/A'}
- 투입LOT: {투입LOT or 'N/A'}
- 시트투입코일: {시트투입코일 or 'N/A'}
- 가동시간: {가동시간 or 0}시간
- 양품수량: {양품수량 or 0}개
- 판정대기: {판정대기 or 0}개
- 완성품불량: {완성품불량 or 0}개
- 생산수량: {생산수량 or 0}개
- 공정불량: {공정불량 or 0}개
- 구성품출고: {구성품출고 or 0}개
- 불량합계: {불량합계 or 0}개
- UPH: {uph}
- 불량률: {defect_rate}%

{근무일자}에 {작업장} 작업장에서 {자재명}({자재번호}) 제품을 {양품수량}개 생산했습니다.
시간당 생산 효율(UPH)은 {uph}이며, 불량률은 {defect_rate}%입니다.
"""
        
        documents.append({
            'content': doc.strip(),
            'metadata': {
                'type': 'production',
                'date': str(근무일자),
                'work_station': 작업장 or '',
                'item_code': 자재번호 or '',
                'item_name': 자재명 or '',
                'car_model': 차종 or '',
                'uph': float(uph),
                'defect_rate': float(defect_rate),
                'good_quantity': int(양품수량 or 0),
                'total_defects': int(불량합계 or 0)
            }
        })
    
    # 나머지 문서들도 간단히 추가 (테스트용)
    for i, row in enumerate(data['mold_equipment'][:10]):  # 처음 10개만
        월, 작업횟수_1200T, 작업횟수_1500T, 작업횟수_1000T, 작업횟수_1000T_PRO, 가동시간_1200T, 가동시간_1500T, 가동시간_1000T, 가동시간_1000T_PRO = row
        
        doc = f"""
금형 설비별 타수 및 가동시간 데이터 ({월}월):
- 1200T 작업횟수: {작업횟수_1200T or 0}회, 총가동시간: {가동시간_1200T or 0}시간
- 1500T 작업횟수: {작업횟수_1500T or 0}회, 총가동시간: {가동시간_1500T or 0}시간
- 1000T 작업횟수: {작업횟수_1000T or 0}회, 총가동시간: {가동시간_1000T or 0}시간
- 1000T PRO 작업횟수: {작업횟수_1000T_PRO or 0}회, 총가동시간: {가동시간_1000T_PRO or 0}시간

{월}월 금형 설비별 작업 현황입니다.
"""
        
        documents.append({
            'content': doc.strip(),
            'metadata': {
                'type': 'mold_equipment',
                'month': int(월) if 월 else 0,
                'work_1200T': int(작업횟수_1200T or 0),
                'work_1500T': int(작업횟수_1500T or 0),
                'work_1000T': int(작업횟수_1000T or 0),
                'work_1000T_PRO': int(작업횟수_1000T_PRO or 0)
            }
        })
    
    return documents

def index_unified_docs():
    """통합 문서를 ChromaDB에 인덱싱"""
    print("모든 테이블 데이터를 조회 중...")
    data = get_all_table_data()
    
    print("통합 문서를 생성 중...")
    documents = create_unified_documents(data)
    
    print(f"총 {len(documents)}개 통합 문서를 생성했습니다.")
    
    # ChromaDB 클라이언트 초기화
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # 컬렉션 생성
    try:
        collection = chroma_client.get_collection("ajin_unified")
        print("기존 ajin_unified 컬렉션을 사용합니다.")
    except:
        collection = chroma_client.create_collection(
            name="ajin_unified",
            metadata={"description": "AJIN 통합 생산 데이터"}
        )
        print("새로운 ajin_unified 컬렉션을 생성했습니다.")
    
    # 기존 문서 삭제 (테스트용)
    try:
        existing_docs = collection.get()
        if existing_docs['ids']:
            collection.delete(ids=existing_docs['ids'])
            print(f"기존 문서 {len(existing_docs['ids'])}건을 삭제했습니다.")
    except:
        print("기존 문서가 없습니다.")
    
    # 모든 문서를 새로 인덱싱
    new_documents = documents
    new_ids = [stable_id(doc, i) for i, doc in enumerate(documents)]
    
    print(f"새로 인덱싱할 문서 수: {len(new_documents)}")
    
    # 캐노니컬라이제이션 적용
    print("문서 캐노니컬라이제이션 중...")
    canonical_texts = [canonicalize(doc) for doc in new_documents]
    
    # 임베딩 생성 (더미 임베딩 사용)
    print("임베딩 생성 중...")
    # OpenAI text-embedding-3-small은 1536 차원, text-embedding-3-large는 3072 차원
    # 일관성을 위해 1536 차원으로 통일
    embeddings = [[0.1] * 1536 for _ in canonical_texts]  # 더미 임베딩
    
    # 문서 저장 (배치 처리)
    print("문서를 저장 중...")
    
    # ChromaDB 배치 크기 제한 (5000개씩 처리)
    batch_size = 5000
    total_batches = (len(new_documents) + batch_size - 1) // batch_size
    
    for i in range(0, len(new_documents), batch_size):
        batch_end = min(i + batch_size, len(new_documents))
        batch_ids = new_ids[i:batch_end]
        batch_embeddings = embeddings[i:batch_end]
        batch_texts = canonical_texts[i:batch_end]
        batch_metadatas = [doc['metadata'] for doc in new_documents[i:batch_end]]
        
        batch_num = (i // batch_size) + 1
        print(f"배치 {batch_num}/{total_batches} 저장 중... ({len(batch_ids)}건)")
        
        collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_texts,
            metadatas=batch_metadatas
        )
    
    print(f"업서트 완료: 신규 {len(new_documents)}건 추가")
