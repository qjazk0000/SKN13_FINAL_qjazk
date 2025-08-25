"""
RAG 시스템 통합 파이프라인
전체 RAG 워크플로우를 관리합니다.
"""

from typing import List, Dict, Any, Optional
from django.conf import settings
from .keyword_extractor import extract_keywords
from .filters import guess_domains_from_keywords
from .rag_search import RagSearcher
from .answerer import make_answer, format_context_for_display, validate_answer_quality
import datetime
import re

def answer_query(query: str, openai_api_key: str = None, explicit_domain: str = None) -> Dict[str, Any]:
    """
    질문에 대한 완전한 RAG 답변 생성
    
    Args:
        query: 사용자 질문
        openai_api_key: OpenAI API 키 (선택사항)
        explicit_domain: 명시적으로 지정된 도메인 (선택사항)
    
    Returns:
        답변과 메타데이터를 포함한 결과
    """
    try:
        print(f"DEBUG: RAG 파이프라인 시작 - 질문: {query}")
        
        # 1단계: 키워드 추출
        keywords = extract_keywords(query, openai_api_key)
        print(f"DEBUG: 추출된 키워드: {keywords}")
        
        # 2단계: 도메인 추정
        if explicit_domain:
            # 명시적으로 지정된 도메인 우선
            estimated_domains = [explicit_domain]
            print(f"DEBUG: 명시적 도메인 사용: {explicit_domain}")
        else:
            # 키워드 기반 도메인 추정
            estimated_domains = guess_domains_from_keywords(keywords)
            print(f"DEBUG: 추정된 도메인: {estimated_domains}")
        
        # 3단계: RAG 검색
        searcher = RagSearcher()
        search_results = searcher.hybrid_search(
            query=query,
            domain_list=estimated_domains if estimated_domains else None,
            top_k=8
        )
        print(f"DEBUG: 검색 결과 수: {len(search_results)}")
        
        # 4단계: 답변 생성
        if search_results:
            # 검색 결과가 3개 미만인 경우 사용자 친화적 메시지 생성
            if len(search_results) < 3:
                result = {
                    'success': True,
                    'answer': "질문을 조금 더 명확하게 해주시면 감사합니다.",
                    'used_domains': estimated_domains,
                    'top_docs': [],  # 참고문서 출력 안함
                    'keywords': keywords,
                    'quality': {'score': 0, 'issues': ['검색 결과 부족'], 'quality_level': '미흡'},
                    'search_count': len(search_results)
                }
            else:
                answer = make_answer(query, search_results, openai_api_key)
                
                # 5단계: 답변 품질 검증
                quality_result = validate_answer_quality(answer, query)
                
                # 6단계: 프론트엔드용 컨텍스트 포맷팅
                formatted_contexts = format_context_for_display(search_results)
                
                result = {
                    'success': True,
                    'answer': answer,
                    'used_domains': estimated_domains,
                    'top_docs': formatted_contexts,
                    'keywords': keywords,
                    'quality': quality_result,
                    'search_count': len(search_results)
                }
        else:
            # 검색 결과가 없는 경우
            result = {
                'success': True,
                'answer': "질문을 조금 더 명확하게 해주시면 감사합니다.",
                'used_domains': estimated_domains,
                'top_docs': [],
                'keywords': keywords,
                'quality': {'score': 0, 'issues': ['검색 결과 없음'], 'quality_level': '미흡'},
                'search_count': 0
            }
        
        print(f"DEBUG: RAG 파이프라인 완료")
        return result
        
    except Exception as e:
        print(f"DEBUG: RAG 파이프라인 오류: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'answer': f"죄송합니다. 시스템 오류가 발생했습니다: {str(e)}",
            'used_domains': [],
            'top_docs': [],
            'keywords': [],
            'quality': {'score': 0, 'issues': [f'시스템 오류: {str(e)}'], 'quality_level': '오류'},
            'search_count': 0
        }

def quick_search(query: str, domain: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    빠른 검색 (답변 생성 없이 문서만 검색)
    
    Args:
        query: 검색 질문
        domain: 도메인 (선택사항)
        top_k: 반환할 결과 수
    
    Returns:
        검색 결과 리스트
    """
    try:
        searcher = RagSearcher()
        
        if domain:
            results = searcher.search_by_domain(query, domain, top_k)
        else:
            results = searcher.search(query, top_k=top_k)
        
        return results
        
    except Exception as e:
        print(f"빠른 검색 실패: {e}")
        return []

def get_domain_suggestions(query: str) -> List[str]:
    """
    질문에 대한 도메인 제안
    
    Args:
        query: 사용자 질문
    
    Returns:
        제안 도메인 리스트
    """
    try:
        keywords = extract_keywords(query)
        suggested_domains = guess_domains_from_keywords(keywords)
        return suggested_domains
    except Exception as e:
        print(f"도메인 제안 실패: {e}")
        return []

def health_check() -> Dict[str, Any]:
    """
    RAG 시스템 상태 확인
    
    Returns:
        시스템 상태 정보
    """
    try:
        searcher = RagSearcher()
        
        # Qdrant 연결 확인
        collection_info = searcher.get_collection_info()
        
        # 검색기 상태 확인
        searcher_healthy = searcher.health_check()
        
        # OpenAI API 키 확인
        openai_available = bool(getattr(settings, 'OPENAI_API_KEY', None))
        
        return {
            'status': 'healthy' if searcher_healthy and collection_info.get('status') == 'active' else 'unhealthy',
            'qdrant': collection_info,
            'searcher': 'healthy' if searcher_healthy else 'unhealthy',
            'openai': 'available' if openai_available else 'unavailable',
            'timestamp': str(datetime.datetime.now())
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': str(datetime.datetime.now())
        }

# 기존 rag_answer 함수와의 호환성을 위한 래퍼
def rag_answer_enhanced(question: str) -> Dict[str, Any]:
    """
    기존 rag_answer 함수를 대체하는 향상된 버전
    
    Args:
        question: 사용자 질문
    
    Returns:
        기존 rag_answer와 호환되는 응답 형식
    """
    result = answer_query(question)
    
    # 기존 형식으로 변환
    if result['success']:
        return {
            "answer": result['answer'],
            "sources": [
                {
                    "source": re.sub(r'\(\d{6}\)', '', doc['file_name'].replace('_', ' ')).strip(),  # 날짜 제거 및 언더스코어를 공백으로 변경
                    "page": f"p.{doc['pages']}" if doc['pages'] else "p.1",  # 페이지 형식 간소화
                    "path": doc['file_name']  # 기존 호환성
                }
                for doc in result['top_docs']
            ] if result['top_docs'] else [],  # top_docs가 비어있으면 빈 배열
            "question_type": {
                "type": "enhanced_rag",
                "confidence": "high" if result['quality']['score'] >= 7 else "medium"
            },
            "rag_used": True
        }
    else:
        return {
            "answer": result['answer'],
            "sources": [],
            "question_type": {"type": "error", "confidence": "low"},
            "rag_used": False
        } 