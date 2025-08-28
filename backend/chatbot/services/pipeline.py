"""
RAG 시스템 통합 파이프라인
전체 RAG 워크플로우를 관리합니다.
새로운 메타데이터 구조를 활용한 향상된 검색과 답변 생성
"""

from typing import List, Dict, Any, Optional
from django.conf import settings
from .keyword_extractor import extract_keywords
from .filters import guess_domains_from_keywords
from .rag_search import RagSearcher
from .answerer import make_answer, format_context_for_display, validate_answer_quality
import datetime
import re
import os
import sys
import time
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 프롬프트 로더 직접 구현
def load_prompt(path: str, *, default: str = "") -> str:
    """프롬프트 파일을 로드하는 함수"""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"WARNING: Failed to load prompt from {path}: {e}")
        return default

# 전역 프롬프트 변수
_SYSTEM_PROMPT = None
_USER_PROMPT = None

def _init_prompts():
    """프롬프트 초기화 함수"""
    global _SYSTEM_PROMPT, _USER_PROMPT
    if _SYSTEM_PROMPT is None:
        try:
            system_prompt_path = '/app/config/system_prompt.md'
            _SYSTEM_PROMPT = load_prompt(system_prompt_path,
                                         default="당신은 업무 가이드를 제공하는 전문가입니다.")
        except FileNotFoundError:
            _SYSTEM_PROMPT = "당신은 업무 가이드를 제공하는 전문가입니다."
            print("WARNING: system_prompt.md not found, using default prompt")
    
    if _USER_PROMPT is None:
        try:
            user_prompt_path = '/app/config/user_prompt.md'
            _USER_PROMPT = load_prompt(user_prompt_path, default="")
        except FileNotFoundError:
            _USER_PROMPT = ""
            print("WARNING: user_prompt.md not found, using default prompt")
    
    return _SYSTEM_PROMPT, _USER_PROMPT

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
    start_time = time.time()
    
    try:
        logger.info(f"RAG 파이프라인 시작 - 질문: {query}")
        print(f"DEBUG: RAG 파이프라인 시작 - 질문: {query}")
        
        # 1단계: 키워드 추출 (타임아웃 방지)
        logger.info("1단계: 키워드 추출 시작")
        keywords_start = time.time()
        try:
            keywords = extract_keywords(query, openai_api_key)
            logger.info(f"키워드 추출 완료 (소요시간: {time.time() - keywords_start:.2f}초)")
            print(f"DEBUG: 추출된 키워드: {keywords}")
        except Exception as e:
            logger.error(f"키워드 추출 실패: {e}")
            keywords = []
            print(f"WARNING: 키워드 추출 실패, 빈 리스트 사용: {e}")
        
        # 2단계: 도메인 추정
        logger.info("2단계: 도메인 추정 시작")
        domain_start = time.time()
        try:
            if explicit_domain:
                # 명시적으로 지정된 도메인 우선
                estimated_domains = [explicit_domain]
                logger.info(f"명시적 도메인 사용: {explicit_domain}")
                print(f"DEBUG: 명시적 도메인 사용: {explicit_domain}")
            else:
                # 키워드 기반 도메인 추정
                estimated_domains = guess_domains_from_keywords(keywords)
                logger.info(f"도메인 추정 완료 (소요시간: {time.time() - domain_start:.2f}초)")
                print(f"DEBUG: 추정된 도메인: {estimated_domains}")
        except Exception as e:
            logger.error(f"도메인 추정 실패: {e}")
            estimated_domains = []
            print(f"WARNING: 도메인 추정 실패, 빈 리스트 사용: {e}")
        
        # 3단계: 향상된 RAG 검색 (새로운 메타데이터 구조 활용)
        logger.info("3단계: RAG 검색 시작")
        search_start = time.time()
        
        try:
            # 검색 전략 결정
            search_strategy = _determine_search_strategy(query, keywords, estimated_domains)
            logger.info(f"검색 전략 결정: {search_strategy}")
            print(f"DEBUG: 검색 전략: {search_strategy}")
            
            # 전략에 따른 검색 실행
            if search_strategy['type'] == 'domain_specific':
                search_results = RagSearcher().search_by_domain(
                    query=query, 
                    domain=search_strategy['domain'], 
                    top_k=10
                )
            elif search_strategy['type'] == 'file_type_specific':
                search_results = RagSearcher().search_by_file_type(
                    query=query, 
                    file_type=search_strategy['file_type'], 
                    top_k=10
                )
            elif search_strategy['type'] == 'recency_aware':
                search_results = RagSearcher().search_by_recency(
                    query=query, 
                    min_recency=search_strategy['min_recency'], 
                    top_k=10
                )
            else:
                # 하이브리드 검색 (기본)
                searcher = RagSearcher()
                search_results = searcher.hybrid_search(
                    query=query,
                    domain_list=estimated_domains if estimated_domains else None,
                    file_types=search_strategy.get('file_types'),
                    min_recency=search_strategy.get('min_recency'),
                    top_k=10
                )
            
            logger.info(f"검색 완료 (소요시간: {time.time() - search_start:.2f}초, 결과 수: {len(search_results)})")
            print(f"DEBUG: 검색 결과 수: {len(search_results)}")
            
        except Exception as e:
            logger.error(f"RAG 검색 실패: {e}")
            search_results = []
            print(f"ERROR: RAG 검색 실패: {e}")
        
        # 4단계: 답변 생성
        logger.info("4단계: 답변 생성 시작")
        answer_start = time.time()
        
        try:
            if search_results:
                # 검색 결과가 3개 미만인 경우 사용자 친화적 메시지 생성
                if len(search_results) < 3:
                    result = {
                        'success': True,
                        'answer': "질문을 조금 더 명확하게 해주시면 감사합니다.",
                        'used_domains': estimated_domains,
                        'search_strategy': search_strategy,
                        'top_docs': [],
                        'sources': []
                    }
                    logger.info("검색 결과 부족으로 기본 메시지 반환")
                    return result
                
                # 컨텍스트 포맷팅 및 답변 생성
                contexts = [result['text'] for result in search_results[:5]]
                
                # 시스템 및 사용자 프롬프트 로드
                system_prompt, user_prompt = _init_prompts()
                
                # 답변 생성 (올바른 인자로 호출)
                answer = make_answer(
                    query=query,
                    contexts=search_results[:5],  # 전체 결과 객체 전달
                    api_key=None  # 환경변수에서 자동으로 가져옴
                )
                
                # 답변 품질 검증
                if not validate_answer_quality(answer, query):
                    logger.warning("답변 품질이 낮습니다. 기본 메시지로 대체합니다.")
                    print("WARNING: 답변 품질이 낮습니다. 기본 메시지로 대체합니다.")
                    answer = "죄송합니다. 질문에 대한 적절한 답변을 생성하지 못했습니다. 다른 방식으로 질문해 주시거나, 관련 도메인을 명시해 주세요."
                
                # 참고 문서 정보 생성 (새로운 메타데이터 활용)
                sources = _format_sources_with_metadata(search_results[:5])
                
                result = {
                    'success': True,
                    'answer': answer,
                    'used_domains': estimated_domains,
                    'search_strategy': search_strategy,
                    'top_docs': search_results[:5],
                    'sources': sources
                }
                
                logger.info(f"답변 생성 완료 (소요시간: {time.time() - answer_start:.2f}초)")
                
            else:
                # 검색 결과가 없는 경우
                result = {
                    'success': True,
                    'answer': "질문을 조금 더 명확하게 해주시면 감사합니다.",
                    'used_domains': estimated_domains,
                    'search_strategy': search_strategy,
                    'top_docs': [],
                    'sources': []
                }
                logger.info("검색 결과 없음으로 기본 메시지 반환")
            
            total_time = time.time() - start_time
            logger.info(f"RAG 파이프라인 완료 (총 소요시간: {total_time:.2f}초)")
            
            return result
            
        except Exception as e:
            logger.error(f"답변 생성 실패: {e}")
            print(f"ERROR: 답변 생성 실패: {e}")
            raise
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"RAG 파이프라인 오류 (소요시간: {total_time:.2f}초): {e}")
        print(f"RAG 파이프라인 오류: {e}")
        return {
            'success': False,
            'error': str(e),
            'answer': "죄송합니다. 시스템 오류가 발생했습니다."
        }

def _determine_search_strategy(query: str, keywords: List[str], estimated_domains: List[str]) -> Dict[str, Any]:
    """
    질문과 키워드를 분석하여 최적의 검색 전략 결정
    
    Args:
        query: 사용자 질문
        keywords: 추출된 키워드
        estimated_domains: 추정된 도메인
    
    Returns:
        검색 전략 딕셔너리
    """
    query_lower = query.lower()
    
    # 1. 도메인 특정 검색 전략
    if estimated_domains and len(estimated_domains) == 1:
        return {
            'type': 'domain_specific',
            'domain': estimated_domains[0],
            'confidence': 'high'
        }
    
    # 2. 문서 타입 특정 검색 전략
    doc_type_keywords = {
        '정관': ['정관', '기본법', '조직법'],
        '규정': ['규정', '운영규정', '관리규정'],
        '규칙': ['규칙', '세부규칙', '실행규칙'],
        '지침': ['지침', '업무지침', '운영지침']
    }
    
    for doc_type, type_keywords in doc_type_keywords.items():
        if any(keyword in query_lower for keyword in type_keywords):
            return {
                'type': 'file_type_specific',
                'file_type': doc_type,
                'confidence': 'medium'
            }
    
    # 3. 최신성 인식 검색 전략
    recency_keywords = ['최신', '최근', '새로운', '업데이트', '변경', '수정']
    if any(keyword in query_lower for keyword in recency_keywords):
        return {
            'type': 'recency_aware',
            'min_recency': 2,  # 최신성 점수 2 이상
            'confidence': 'medium'
        }
    
    # 4. 복합 검색 전략 (기본)
    return {
        'type': 'hybrid',
        'domain_list': estimated_domains,
        'file_types': None,
        'min_recency': None,
        'confidence': 'low'
    }

def _format_sources_with_metadata(search_results: List[Dict[str, Any]]) -> List[str]:
    """
    새로운 메타데이터를 활용하여 참고 문서 정보 포맷팅
    
    Args:
        search_results: 검색 결과 리스트
    
    Returns:
        포맷팅된 참고 문서 리스트
    """
    sources = []
    
    for result in search_results:
        # 파일명에서 날짜 패턴 제거
        file_name = result.get('file_name', '')
        if file_name:
            # 날짜 패턴 (YYYYMMDD) 제거
            file_name = re.sub(r'\(\d{6}\)', '', file_name).strip()
            file_name = file_name.replace('_', ' ')
        
        # 페이지 정보
        page_info = result.get('pages', '')
        if page_info:
            page_str = f"p.{page_info}"
        else:
            page_str = ""
        
        # 도메인 정보
        domain_info = result.get('domain_primary', '')
        if domain_info and domain_info != '일반':
            domain_str = f" ({domain_info})"
        else:
            domain_str = ""
        
        # 최신성 정보
        recency_score = result.get('recency_score', 1)
        if recency_score >= 3:
            recency_str = " [최신]"
        elif recency_score >= 2:
            recency_str = " [최근]"
        else:
            recency_str = ""
        
        # 최종 소스 문자열 조합
        source_parts = [part for part in [file_name, page_str, domain_str, recency_str] if part]
        source_str = " ".join(source_parts).strip()
        
        if source_str:
            sources.append(source_str)
    
    return sources

def quick_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    빠른 검색 (답변 생성 없이)
    
    Args:
        query: 검색 질문
        top_k: 반환할 결과 수
    
    Returns:
        검색 결과 리스트
    """
    try:
        searcher = RagSearcher()
        results = searcher.search(query, top_k=top_k)
        return results
    except Exception as e:
        logger.error(f"빠른 검색 오류: {e}")
        print(f"빠른 검색 오류: {e}")
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
        suggestions = guess_domains_from_keywords(keywords)
        return suggestions
    except Exception as e:
        logger.error(f"도메인 제안 오류: {e}")
        print(f"도메인 제안 오류: {e}")
        return []

def health_check() -> Dict[str, Any]:
    """
    RAG 시스템 상태 확인
    
    Returns:
        시스템 상태 정보
    """
    try:
        searcher = RagSearcher()
        
        # Qdrant 연결 상태 확인
        qdrant_health = searcher.health_check()
        
        # 컬렉션 정보 조회
        collection_info = searcher.get_collection_info()
        
        # 키워드 추출 테스트
        keyword_test = extract_keywords("테스트 질문")
        
        return {
            'status': 'healthy' if all([qdrant_health, collection_info, keyword_test]) else 'degraded',
            'qdrant_connection': qdrant_health,
            'collection_info': collection_info,
            'keyword_extraction': bool(keyword_test),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"상태 확인 오류: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }

def rag_answer_enhanced(user_query: str) -> Dict[str, Any]:
    """
    향상된 RAG 답변 생성 (기존 rag_answer와 호환)
    
    Args:
        user_query: 사용자 질문
    
    Returns:
        답변과 메타데이터를 포함한 결과
    """
    try:
        # OpenAI API 키는 환경변수에서 자동으로 가져옴
        result = answer_query(user_query)
        
        if result['success']:
            # 기존 rag_answer와 호환되는 형식으로 변환
            return {
                'answer': result['answer'],
                'sources': result['sources'],
                'metadata': {
                    'domains': result.get('used_domains', []),
                    'search_strategy': result.get('search_strategy', {}),
                    'result_count': len(result.get('top_docs', []))
                }
            }
        else:
            return {
                'answer': result.get('answer', '죄송합니다. 답변을 생성할 수 없습니다.'),
                'sources': [],
                'metadata': {'error': result.get('error', 'Unknown error')}
            }
            
    except Exception as e:
        logger.error(f"향상된 RAG 답변 생성 오류: {e}")
        print(f"향상된 RAG 답변 생성 오류: {e}")
        return {
            'answer': '죄송합니다. 시스템 오류가 발생했습니다.',
            'sources': [],
            'metadata': {'error': str(e)}
        } 