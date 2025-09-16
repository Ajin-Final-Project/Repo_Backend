"""
RAG 챗봇 컨트롤러
AJIN 스마트팩토리 RAG 챗봇 API 엔드포인트를 제공합니다.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.rag_service import search_rag_collections, generate_llm_response

router = APIRouter()

# Pydantic 모델
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@router.get("/health")
async def health_check():
    return {"ok": True, "message": "AJIN RAG 챗봇 API가 정상 작동 중입니다."}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        print("=" * 50)
        print(f" 받은 질문: {request.question}")
        print("=" * 50)
        
        # RAG 검색
        rag_results = search_rag_collections(request.question)
        
        if not rag_results:
            return ChatResponse(answer="해당 정보를 찾을 수 없습니다.")
        
        # LLM으로 최종 답변 생성
        answer = generate_llm_response(request.question, rag_results)
        
        return ChatResponse(answer=answer)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 처리 중 오류가 발생했습니다: {str(e)}")

@router.get("/")
async def root():
    """RAG 챗봇 루트 엔드포인트"""
    return {
        "message": "AJIN RAG 챗봇 API",
        "description": "AJIN 스마트팩토리 RAG 기반 챗봇 API",
        "endpoints": {
            "health": "GET /chat/health",
            "chat": "POST /chat/chat"
        }
    }
