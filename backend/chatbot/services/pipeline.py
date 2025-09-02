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
import openai
import hashlib

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
            system_prompt_path = '/app/prompts/system_prompt.md'
            _SYSTEM_PROMPT = load_prompt(system_prompt_path,
                                         default="당신은 업무 가이드를 제공하는 전문가입니다.")
        except FileNotFoundError:
            _SYSTEM_PROMPT = "당신은 업무 가이드를 제공하는 전문가입니다."
            print("WARNING: system_prompt.md not found, using default prompt")
    
    if _USER_PROMPT is None:
        try:
            user_prompt_path = '/app/prompts/user_prompt.md'
            _USER_PROMPT = load_prompt(user_prompt_path,
                                       default="위 문서들을 바탕으로 질문에 대한 정확한 답변을 제공해주세요.")
        except FileNotFoundError:
            _USER_PROMPT = "위 문서들을 바탕으로 질문에 대한 정확한 답변을 제공해주세요."
            print("WARNING: user_prompt.md not found, using default prompt")
    
    return _SYSTEM_PROMPT, _USER_PROMPT

def is_simple_greeting(query: str, openai_api_key: str = None) -> bool:
    """
    LLM을 사용하여 간단한 인사말/질문인지 판단
    
    Args:
        query: 사용자 질문
        openai_api_key: OpenAI API 키
    
    Returns:
        True if simple greeting, False if complex question
    """
    try:
        # OpenAI 클라이언트 설정
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API 키가 없어 간단한 질문 판단 불가, 복잡한 질문으로 처리")
            return False
        
        client = openai.OpenAI(api_key=api_key)
        
        # 간단한 질문 판단용 프롬프트
        system_prompt = """당신은 질문의 복잡도를 판단하는 전문가입니다.
사용자의 질문이 '간단한 인사말이나 짧은 대화'인지, '구체적인 업무 관련 질문'인지 판단해주세요.

간단한 인사말/대화 예시:
- 안녕, 안녕하세요, Hi, Hello
- 좋은 아침, 좋은 저녁, 잘 가
- 감사합니다, 고마워요, 땡큐
- 네, 예, 응, 오케이
- 짧은 감정 표현 (ㅎㅎ, ㅋㅋ, 우와 등)

복잡한 업무 질문 예시:
- 휴가 신청 방법은?
- 급여 규정이 어떻게 되나요?
- 회의실 예약은 어떻게 하나요?
- 프로젝트 관련 문의

답변은 반드시 'YES' 또는 'NO'로만 해주세요.
- YES: 간단한 인사말/대화
- NO: 복잡한 업무 질문"""

        user_prompt = f"다음 질문을 분석해주세요: '{query}'"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().upper()
        is_simple = result == "YES"
        
        logger.info(f"간단한 질문 판단 결과: {query} -> {result} ({'간단' if is_simple else '복잡'})")
        return is_simple
        
    except Exception as e:
        logger.error(f"간단한 질문 판단 실패: {e}")
        # 오류 시 복잡한 질문으로 처리 (안전한 기본값)
        return False

def answer_query(query: str, openai_api_key: str = None, explicit_domain: str = None) -> Dict[str, Any]:
    """
    질문에 대한 완전한 RAG 답변 생성
    
    Args:
        query: 사용자 질문
        openai_api_key: OpenAI API 키 (선택사항)
        explicit_domain: 명시적 도메인 (선택사항)
    
    Returns:
        답변, 메타데이터, 참고문서를 포함한 딕셔너리
    """
    start_time = time.time()
    
    try:
        logger.info(f"RAG 파이프라인 시작 - 질문: {query}")
        print(f"DEBUG: RAG 파이프라인 시작 - 질문: {query}")
        
        # 🚀 간단한 질문 감지 (간단한 인사말은 빠른 처리)
        is_simple_query = is_simple_greeting(query, openai_api_key)
        
        if is_simple_query:
            logger.info(f"⚡ 간단한 질문 감지, LLM으로 직접 응답 생성: {query}")
            print(f"DEBUG: ⚡ 간단한 질문 감지, LLM으로 직접 응답 생성")
            
            # LLM에게 간단한 응답 생성 요청
            try:
                api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
                if not api_key:
                    # API 키가 없는 경우에만 기본 응답 사용
                    response = "안녕하세요! 업무 관련 궁금한 사항이 있으시면 언제든 문의해 주세요."
                else:
                    client = openai.OpenAI(api_key=api_key)
                    
                    simple_response_prompt = f"""사용자가 간단한 인사말이나 짧은 대화를 했습니다: "{query}"

다음 역할을 수행해주세요:
- 한국인터넷진흥원(KISA)의 업무 가이드 챗봇으로서 친근하고 전문적으로 응답
- 사용자의 톤에 맞춰 자연스럽게 인사
- 업무 관련 도움을 제공할 준비가 되어 있음을 알림
- 2-3문장으로 간결하게 작성

예시:
- "안녕" → "안녕하세요! 업무 관련 궁금한 사항이 있으시면 언제든 문의해 주세요."
- "좋은 아침" → "좋은 아침입니다! 오늘도 업무에 도움이 되는 정보를 제공해드리겠습니다."
- "고마워" → "천만에요! 다른 궁금한 사항이 있으시면 언제든 말씀해 주세요."
"""
                    
                    response_result = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "user", "content": simple_response_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=100
                    )
                    
                    response = response_result.choices[0].message.content.strip()
                    
            except Exception as e:
                logger.error(f"간단한 응답 생성 실패: {e}")
                # 오류 시 기본 응답 사용
                response = "안녕하세요! 업무 관련 궁금한 사항이 있으시면 언제든 문의해 주세요."
            
            total_time = time.time() - start_time
            logger.info(f"⚡ 간단한 질문 처리 완료 (총 소요시간: {total_time:.2f}초)")
            
            return {
                'answer': response,
                'contexts': [],
                'sources': [],
                'keywords': [],
                'domains': [],
                'search_strategy': 'simple_response',
                'total_time': total_time,
                'search_time': 0,
                'answer_time': total_time
            }
        
        # 🔥 복잡한 질문 처리 (통합된 system_prompt가 보안 검증 포함)
        logger.info("복잡한 질문 감지, 전체 RAG 파이프라인 실행")
        print(f"DEBUG: 복잡한 질문 감지, 전체 RAG 파이프라인 실행")
        
        # 1단계: 키워드 추출
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
        
        # answer_query는 항상 answer를 반환하므로 success 체크 불필요
        search_strategy = result.get('search_strategy', '')
        
        return {
            'answer': result.get('answer', '죄송합니다. 답변을 생성할 수 없습니다.'),
            'sources': result.get('sources', []),
            'rag_used': search_strategy != 'simple_response',  # 간단한 응답이 아니면 RAG 사용
            'metadata': {
                'domains': result.get('domains', []),
                'search_strategy': search_strategy,
                'keywords': result.get('keywords', []),
                'total_time': result.get('total_time', 0),
                'search_time': result.get('search_time', 0),
                'answer_time': result.get('answer_time', 0)
            }
        }
            
    except Exception as e:
        logger.error(f"향상된 RAG 답변 생성 오류: {e}")
        print(f"향상된 RAG 답변 생성 오류: {e}")
        return {
            'answer': '죄송합니다. 시스템 오류가 발생했습니다.',
            'sources': [],
            'rag_used': False,
            'metadata': {'error': str(e)}
        }