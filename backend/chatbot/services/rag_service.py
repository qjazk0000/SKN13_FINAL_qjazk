import os
import re
from typing import List, Dict, Tuple
from django.conf import settings
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI

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

# 시스템 프롬프트 로드
try:
    prompt_path = '/app/config/system_prompt.md'
    SYSTEM_PROMPT = load_prompt(prompt_path, 
                                default="당신은 한국인터넷진흥원의 규정 전문가입니다.")
except FileNotFoundError:
    SYSTEM_PROMPT = "당신은 한국인터넷진흥원의 규정 전문가입니다."
    print("WARNING: system_prompt.md not found, using default prompt")

# QdrantClient를 전역으로 생성 (연결 재사용)
_qdrant_client = None
_embedder = None

def _get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _qdrant_client

def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("nlpai-lab/KoE5")
    return _embedder

def _extract_keywords(query: str) -> List[str]:
    """질문에서 키워드 추출"""
    # 한국어 키워드 추출 (규정, 조항, 절차 등)
    keywords = re.findall(r'[가-힣]+', query)
    # 불용어 제거
    stopwords = ['이', '가', '을', '를', '에', '에서', '로', '으로', '의', '와', '과', '도', '는', '은']
    keywords = [kw for kw in keywords if kw not in stopwords and len(kw) > 1]
    return keywords[:5]  # 상위 5개 키워드만 사용

def _extract_document_type(query: str) -> str:
    """질문에서 문서 유형 추출"""
    query_lower = query.lower()
    
    # 문서 유형 매핑
    type_mapping = {
        '정관': ['정관', '기본법', '근본법'],
        '규정': ['규정', '운영규정', '관리규정'],
        '규칙': ['규칙', '세부규칙', '실행규칙'],
        '지침': ['지침', '가이드라인', '운영지침'],
        '인사': ['인사', '채용', '급여', '휴가', '육아휴직', '연차'],
        '회계': ['회계', '예산', '감사', '재정'],
        '보안': ['보안', '정보보호', '개인정보'],
        '기술': ['기술', 'IT', '정보화', '시스템']
    }
    
    for doc_type, keywords in type_mapping.items():
        if any(keyword in query_lower for keyword in keywords):
            return doc_type
    
    return "일반"

def _classify_document_by_domain(filename: str) -> Dict[str, str]:
    """파일명 기반으로 업무 도메인을 정교하게 분류"""
    
    filename_lower = filename.lower()
    
    # 1차 분류: 문서 계층
    if filename_lower.startswith('1_'):
        document_level = '정관'
        level_description = '기본법령'
    elif filename_lower.startswith('2_'):
        document_level = '규정'
        if '운영' in filename_lower:
            level_description = '운영규정'
        elif '관리' in filename_lower:
            level_description = '관리규정'
        else:
            level_description = '일반규정'
    elif filename_lower.startswith('3_'):
        document_level = '규칙'
        if '인사' in filename_lower:
            level_description = '인사규칙'
        elif '급여' in filename_lower:
            level_description = '급여규칙'
        elif '취업' in filename_lower:
            level_description = '취업규칙'
        elif '출장' in filename_lower:
            level_description = '출장규칙'
        elif '계약' in filename_lower:
            level_description = '계약규칙'
        elif '보안' in filename_lower:
            level_description = '보안규칙'
        elif '기술' in filename_lower:
            level_description = '기술규칙'
        else:
            level_description = '일반규칙'
    elif filename_lower.startswith('4_'):
        document_level = '지침'
        if '운영' in filename_lower:
            level_description = '운영지침'
        elif '업무' in filename_lower:
            level_description = '업무지침'
        else:
            level_description = '일반지침'
    else:
        document_level = '기타'
        level_description = '기타'
    
    # 2차 분류: 업무 도메인 (상세)
    domain = '일반업무'
    subdomain = '기타'
    
    # 인사관리 도메인
    if any(keyword in filename_lower for keyword in ['인사', '급여', '취업', '출장', '채용', '복무', '교육', '훈련']):
        domain = '인사관리'
        if '인사' in filename_lower:
            subdomain = '인사정책'
        elif '급여' in filename_lower:
            subdomain = '급여관리'
        elif '취업' in filename_lower:
            subdomain = '취업관리'
        elif '출장' in filename_lower:
            subdomain = '출장관리'
        elif '채용' in filename_lower:
            subdomain = '채용관리'
        elif '복무' in filename_lower:
            subdomain = '복무관리'
        elif '교육' in filename_lower or '훈련' in filename_lower:
            subdomain = '교육훈련'
    
    # 재무관리 도메인
    elif any(keyword in filename_lower for keyword in ['회계', '감사', '자산', '계약', '수수료', '예산', '재정']):
        domain = '재무관리'
        if '회계' in filename_lower:
            subdomain = '회계관리'
        elif '감사' in filename_lower:
            subdomain = '감사관리'
        elif '자산' in filename_lower:
            subdomain = '자산관리'
        elif '계약' in filename_lower:
            subdomain = '계약관리'
        elif '수수료' in filename_lower:
            subdomain = '수수료관리'
    
    # 보안관리 도메인
    elif any(keyword in filename_lower for keyword in ['보안', '정보보호', '개인정보', '민원', '신고']):
        domain = '보안관리'
        if '보안' in filename_lower:
            subdomain = '보안정책'
        elif '정보보호' in filename_lower:
            subdomain = '정보보호'
        elif '개인정보' in filename_lower:
            subdomain = '개인정보보호'
        elif '민원' in filename_lower or '신고' in filename_lower:
            subdomain = '민원신고'
    
    # 기술관리 도메인
    elif any(keyword in filename_lower for keyword in ['기술', 'IT', '정보화', '전자서명', '시스템']):
        domain = '기술관리'
        if '기술' in filename_lower:
            subdomain = '기술정책'
        elif 'IT' in filename_lower or '정보화' in filename_lower:
            subdomain = '정보화관리'
        elif '전자서명' in filename_lower:
            subdomain = '전자서명관리'
        elif '시스템' in filename_lower:
            subdomain = '시스템관리'
    
    # 행정관리 도메인
    elif any(keyword in filename_lower for keyword in ['문서', '자료', '기록', '홍보']):
        domain = '행정관리'
        if '문서' in filename_lower:
            subdomain = '문서관리'
        elif '자료' in filename_lower:
            subdomain = '자료관리'
        elif '기록' in filename_lower:
            subdomain = '기록관리'
        elif '홍보' in filename_lower:
            subdomain = '홍보관리'
    
    # 경영관리 도메인
    elif any(keyword in filename_lower for keyword in ['경영', '성과', '내부통제', '이해충돌', '조직', '직제']):
        domain = '경영관리'
        if '경영' in filename_lower:
            subdomain = '경영정책'
        elif '성과' in filename_lower:
            subdomain = '성과관리'
        elif '내부통제' in filename_lower:
            subdomain = '내부통제'
        elif '이해충돌' in filename_lower:
            subdomain = '이해충돌방지'
        elif '조직' in filename_lower or '직제' in filename_lower:
            subdomain = '조직관리'
    
    # 3차 분류: 최신성 (등록일자 추출)
    try:
        # 파일명에서 날짜 추출 (예: 240715, 221222)
        date_match = re.search(r'(\d{6})', filename)
        if date_match:
            date_str = date_match.group(1)
            year = int(date_str[:2])
            if year >= 24:  # 2024년
                recency = '최신'
                recency_score = 3
            elif year >= 22:  # 2022-2023년
                recency = '최근'
                recency_score = 2
            else:  # 2021년 이전
                recency = '기존'
                recency_score = 1
        else:
            recency = '기존'
            recency_score = 1
    except:
        recency = '기존'
        recency_score = 1
    
    return {
        'document_level': document_level,
        'level_description': level_description,
        'domain': domain,
        'subdomain': subdomain,
        'recency': recency,
        'recency_score': recency_score,
        'filename': filename
    }

def _smart_search(query: str, top_k: int = 10) -> List[Dict]:
    """스마트 검색 (메타데이터 기반 정확한 필터링)"""
    client = _get_qdrant_client()
    
    # 질문에서 도메인 추출
    query_lower = query.lower()
    target_domain = None
    
    if any(keyword in query_lower for keyword in ['인사', '채용', '급여', '휴가', '육아휴직', '연차', '출장']):
        target_domain = '인사관리'
    elif any(keyword in query_lower for keyword in ['회계', '예산', '감사', '재정', '계약', '수수료']):
        target_domain = '재무관리'
    elif any(keyword in query_lower for keyword in ['보안', '정보보호', '개인정보', '보안업무']):
        target_domain = '보안관리'
    elif any(keyword in query_lower for keyword in ['기술', 'IT', '정보화', '시스템', '전자서명']):
        target_domain = '기술관리'
    elif any(keyword in query_lower for keyword in ['문서', '기록', '자료', '관리']):
        target_domain = '행정관리'
    
    try:
        if target_domain:
            # 도메인 기반 필터링 (파일명 패턴으로)
            domain_keywords = {
                '인사관리': ['인사', '급여', '취업', '출장', '휴가'],
                '재무관리': ['회계', '예산', '감사', '계약', '수수료'],
                '보안관리': ['보안', '정보보호', '개인정보'],
                '기술관리': ['기술', 'IT', '정보화', '전자서명'],
                '행정관리': ['문서', '기록', '자료', '관리']
            }
            
            keywords = domain_keywords.get(target_domain, [])
            if keywords:
                # 여러 키워드 중 하나라도 포함된 문서 검색
                filter_conditions = []
                for keyword in keywords:
                    filter_conditions.append({
                        "key": "source",
                        "match": {"text": keyword}
                    })
                
                results = client.scroll(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    scroll_filter={
                        "should": filter_conditions  # OR 조건으로 검색
                    },
                    limit=top_k
                )[0]
                return results
        
        # 도메인을 특정할 수 없는 경우 빈 결과 반환
        return []
        
    except Exception as e:
        print(f"스마트 검색 오류: {e}")
        return []

def _keyword_search(query: str, top_k: int = 10) -> List[Dict]:
    """키워드 기반 검색"""
    keywords = _extract_keywords(query)
    if not keywords:
        return []
    
    client = _get_qdrant_client()
    
    # 키워드가 포함된 문서 검색
    keyword_results = []
    for keyword in keywords:
        try:
            # payload에서 text 필드에 키워드가 포함된 문서 검색
            results = client.scroll(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                scroll_filter={
                    "must": [
                        {
                            "key": "text",
                            "match": {"text": keyword}
                        }
                    ]
                },
                limit=top_k // len(keywords)
            )[0]
            keyword_results.extend(results)
        except Exception as e:
            print(f"키워드 검색 오류 ({keyword}): {e}")
            continue
    
    return keyword_results

def _vector_search(query: str, top_k: int = 10) -> List[Dict]:
    """벡터 기반 검색"""
    client = _get_qdrant_client()
    embedder = _get_embedder()
    qvec = embedder.encode([query])[0].tolist()

    try:
        results = client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=qvec,
            limit=top_k,
        )
        return results
    except Exception as e:
        print(f"벡터 검색 오류: {e}")
        return []

def _rerank_results(vector_results: List[Dict], keyword_results: List[Dict], query: str) -> List[Dict]:
    """검색 결과 재순위화"""
    all_results = {}
    
    # 벡터 검색 결과 처리
    for i, result in enumerate(vector_results):
        doc_id = result.payload.get("path", "") + "_" + str(result.payload.get("page", ""))
        if doc_id not in all_results:
            all_results[doc_id] = {
                "result": result,
                "vector_score": result.score,
                "keyword_score": 0,
                "combined_score": result.score
            }
    
    # 키워드 검색 결과 처리
    for result in keyword_results:
        doc_id = result.payload.get("path", "") + "_" + str(result.payload.get("page", ""))
        if doc_id in all_results:
            all_results[doc_id]["keyword_score"] = 1.0
            all_results[doc_id]["combined_score"] += 1.0
        else:
            all_results[doc_id] = {
                "result": result,
                "vector_score": 0,
                "keyword_score": 1.0,
                "combined_score": 1.0
            }
    
    # 통합 점수로 재정렬
    reranked = sorted(all_results.values(), key=lambda x: x["combined_score"], reverse=True)
    return [item["result"] for item in reranked]

def _estimate_tokens(text: str) -> int:
    """한국어 텍스트의 대략적인 토큰 수 추정"""
    # 한국어는 보통 단어당 1.3 토큰 정도
    words = text.split()
    return int(len(words) * 1.3)

def _optimize_context(documents: List[Dict], max_tokens: int = 4000, query: str = "") -> List[Dict]:
    """컨텍스트 길이 최적화 (질문 기반 우선순위)"""
    if not documents:
        return []
    
    # 질문과의 관련성 점수 계산
    scored_docs = []
    for doc in documents:
        text = doc.payload.get("text", "")
        relevance_score = 0
        
        # 질문 키워드가 문서에 포함된 정도로 점수 계산
        if query:
            query_keywords = _extract_keywords(query)
            for keyword in query_keywords:
                if keyword in text:
                    relevance_score += 1
        
        # 벡터 점수도 고려
        if hasattr(doc, 'score'):
            relevance_score += doc.score * 0.5
        
        scored_docs.append({
            'doc': doc,
            'relevance_score': relevance_score,
            'estimated_tokens': _estimate_tokens(text)
        })
    
    # 관련성 점수로 정렬
    scored_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # 토큰 제한 내에서 최적의 문서 선택
    optimized_docs = []
    current_tokens = 0
    
    for scored_doc in scored_docs:
        doc_tokens = scored_doc['estimated_tokens']
        
        if current_tokens + doc_tokens <= max_tokens:
            # 텍스트 길이 제한 (너무 긴 문서는 자르기)
            doc = scored_doc['doc']
            text = doc.payload.get("text", "")
            if len(text) > 800:  # 800자 제한
                doc.payload["text"] = text[:800] + "..."
            
            optimized_docs.append(doc)
            current_tokens += doc_tokens
        else:
            break
    
    return optimized_docs

def _build_context(chunks: List[Dict]) -> str:
    """개선된 컨텍스트 구축"""
    if not chunks:
        return "관련 문서를 찾을 수 없습니다."
    
    lines = []
    for i, c in enumerate(chunks, start=1):
        src = c.payload.get("source", "알 수 없음")
        page = c.payload.get("page", "알 수 없음")
        text = c.payload.get("text", "내용 없음")
        
        # 텍스트 길이 제한 (너무 긴 텍스트는 자르기)
        if len(text) > 500:
            text = text[:500] + "..."
        
        lines.append(f"[{i}] ({src} p.{page}) {text}")
    
    return "\n\n".join(lines)

def _enhance_search_with_domain_classification(query: str, documents: List[Dict]) -> List[Dict]:
    """도메인 분류를 활용하여 검색 결과 품질 향상"""
    if not documents:
        return documents
    
    enhanced_docs = []
    
    for doc in documents:
        # 메타데이터에서 문서 분류 정보 추출
        source = doc.payload.get("source", "")
        doc_title = doc.payload.get("doc_title", "")
        
        # 파일명 기반 도메인 분류
        domain_classification = _classify_document_by_domain(source)
        
        # 질문과의 관련성 점수 계산
        relevance_score = 0
        
        # 1. 도메인 일치 점수 (높은 가중치)
        query_lower = query.lower()
        
        # 인사 관련 질문
        if any(keyword in query_lower for keyword in ['인사', '채용', '급여', '휴가', '육아휴직', '연차', '출장']):
            if domain_classification['domain'] == '인사관리':
                relevance_score += 5
                if any(keyword in query_lower for keyword in ['급여', '수당']):
                    if domain_classification['subdomain'] == '급여관리':
                        relevance_score += 3
                elif any(keyword in query_lower for keyword in ['육아휴직', '휴가']):
                    if domain_classification['subdomain'] in ['인사정책', '복무관리']:
                        relevance_score += 3
        
        # 재무 관련 질문
        elif any(keyword in query_lower for keyword in ['회계', '예산', '감사', '재정', '계약', '수수료']):
            if domain_classification['domain'] == '재무관리':
                relevance_score += 5
                if '감사' in query_lower and domain_classification['subdomain'] == '감사관리':
                    relevance_score += 3
        
        # 보안 관련 질문
        elif any(keyword in query_lower for keyword in ['보안', '정보보호', '개인정보']):
            if domain_classification['domain'] == '보안관리':
                relevance_score += 5
        
        # 기술 관련 질문
        elif any(keyword in query_lower for keyword in ['기술', 'IT', '정보화', '시스템']):
            if domain_classification['domain'] == '기술관리':
                relevance_score += 5
        
        # 2. 문서 계층 점수
        if '규정' in query_lower or '규칙' in query_lower:
            if domain_classification['document_level'] in ['규정', '규칙']:
                relevance_score += 2
        
        # 3. 최신성 점수
        relevance_score += domain_classification['recency_score']
        
        # 4. 벡터 점수 (기존 점수 유지)
        if hasattr(doc, 'score'):
            relevance_score += doc.score
        
        # 향상된 문서 객체 생성
        enhanced_doc = {
            'doc': doc,
            'domain_classification': domain_classification,
            'relevance_score': relevance_score
        }
        
        enhanced_docs.append(enhanced_doc)
    
    # 관련성 점수로 정렬
    enhanced_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # 원본 문서 형태로 반환
    return [item['doc'] for item in enhanced_docs]

def hybrid_search(question: str, top_k: int = None) -> List[Dict]:
    """하이브리드 검색 (벡터 + 키워드 + 메타데이터 기반 스마트)"""
    top_k = top_k or settings.RAG_TOP_K
    
    # 스마트 검색 (메타데이터 기반)
    smart_results = _smart_search(question, top_k=top_k//2)
    
    # 벡터 검색
    vector_results = _vector_search(question, top_k=top_k)
    
    # 키워드 검색
    keyword_results = _keyword_search(question, top_k=top_k)
    
    # 모든 결과 통합
    all_results = smart_results + vector_results + keyword_results
    
    # 결과 재순위화
    combined_results = _rerank_results(vector_results, keyword_results, question)
    
    # 스마트 검색 결과를 우선순위로 추가
    if smart_results:
        # 스마트 검색 결과를 맨 앞에 배치
        final_results = smart_results + [r for r in combined_results if r not in smart_results]
    else:
        final_results = combined_results
    
    # 메타데이터 기반 검색 결과 품질 향상
    enhanced_results = _enhance_search_with_domain_classification(question, final_results)
    
    # 컨텍스트 최적화 (질문 기반)
    optimized_results = _optimize_context(enhanced_results, max_tokens=4000, query=question)
    
    return optimized_results

def generate_answer(question: str, retrieved: List[Dict]) -> Dict:
    """개선된 답변 생성"""
    if not retrieved:
        return {
            "answer": "질문을 조금 더 명확하게 해주시면 감사합니다.",
            "sources": []
        }
    
    ctx = _build_context(retrieved)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    user_prompt = f"""컨텍스트:
{ctx}

질문:
{question}

요구사항:
- 한국어로 답변
- 컨텍스트에서 근거가 되는 조항과 문서명을 간단히 명시
- 실무 적용 시 주의사항이나 절차를 포함
- 답변 후 참고한 문서명과 페이지를 명시
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,  # 더 일관된 답변을 위해 낮춤
            max_tokens=1500,  # 답변 길이 제한
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        answer = f"죄송합니다. AI 답변 생성 중 오류가 발생했습니다: {str(e)}"
    
    # 소스 정보 추출
    sources = [
        {
            "source": r.payload.get("source", "알 수 없음"),
            "page": r.payload.get("page", "알 수 없음"),
            "path": r.payload.get("path", "알 수 없음"),
        }
        for r in retrieved
    ]
    
    return {"answer": answer, "sources": sources}

def _classify_question_type(query: str) -> Dict[str, str]:
    """메타데이터 기반 하이브리드 질문 분류"""
    query_lower = query.lower()
    
    # 1단계: 명확한 인사말/감사인사 패턴 (빠른 처리)
    clear_greeting_patterns = [
        '안녕하세요', '반갑습니다', '만나서 반갑습니다', '처음 뵙겠습니다',
        '감사합니다', '고맙습니다', '수고하셨습니다', '힘내세요', '화이팅'
    ]
    
    if any(pattern in query_lower for pattern in clear_greeting_patterns):
        return {
            'type': 'greeting',
            'category': '명확한 인사말/감사인사',
            'needs_rag': False,
            'confidence': 'high',
            'response_type': 'friendly_greeting'
        }
    
    # 2단계: 메타데이터 기반 규정 관련성 분석
    regulation_keywords = [
        '규정', '규칙', '지침', '절차', '방법', '신청', '신고', '처리',
        '육아휴직', '연차', '급여', '출장', '회계', '감사', '보안', '정보보호',
        '채용', '인사', '계약', '수수료', '동호회', '교육', '훈련'
    ]
    
    regulation_score = sum(1 for keyword in regulation_keywords if keyword in query_lower)
    
    # 3단계: 질문 의도 분석 (의문사, 명령어 등)
    question_indicators = ['어떻게', '무엇', '언제', '어디서', '왜', '어떤', '몇', '얼마나']
    has_question_intent = any(indicator in query_lower for indicator in question_indicators)
    
    # 4단계: 메타데이터 기반 분류 결정
    if regulation_score >= 2 and has_question_intent:
        # 명확한 규정 질문
        return {
            'type': 'regulation',
            'category': '규정/제도 질문',
            'needs_rag': True,
            'confidence': 'high',
            'response_type': 'regulation_answer',
            'regulation_score': regulation_score
        }
    elif regulation_score >= 1 and has_question_intent:
        # 규정 관련 질문 가능성
        return {
            'type': 'regulation',
            'category': '규정 관련 질문',
            'needs_rag': True,
            'confidence': 'medium',
            'response_type': 'regulation_answer',
            'regulation_score': regulation_score
        }
    elif regulation_score == 0 and not has_question_intent:
        # 인사말/일반 대화
        return {
            'type': 'greeting',
            'category': '일반 인사말/대화',
            'needs_rag': False,
            'confidence': 'medium',
            'response_type': 'friendly_greeting'
        }
    else:
        # 모호한 경우 - RAG 검색 시도
        return {
            'type': 'ambiguous',
            'category': '모호한 질문',
            'needs_rag': True,
            'confidence': 'low',
            'response_type': 'general_answer',
            'regulation_score': regulation_score
        }

def _generate_smart_greeting_response(query: str, question_type: Dict) -> str:
    """메타데이터 기반 스마트 인사말 응답 생성"""
    query_lower = query.lower()
    
    # 기본 인사말
    base_greeting = "안녕하세요! 한국인터넷진흥원 규정에 대해 궁금한 점이 있으시면 언제든지 질문해 주세요."
    
    # 신입사원 관련 특별 응답
    if '신입' in query_lower:
        return f"{base_greeting}\n\n신입사원이시군요! 환영합니다! 😊\n\n궁금한 규정이나 제도가 있으시면 구체적으로 질문해 주세요. 예를 들어:\n• 육아휴직 신청 절차\n• 연차 사용 방법\n• 급여 지급 규정\n• 출장 신청 절차\n\n어떤 것이든 도와드리겠습니다!"
    
    # 감사인사
    elif any(word in query_lower for word in ['감사', '고맙']):
        return "천만에요! 언제든지 도움이 필요하시면 말씀해 주세요. 😊"
    
    # 일반 인사말
    else:
        return base_greeting

def _should_use_rag(query: str, question_type: Dict) -> bool:
    """RAG 사용 여부를 결정하는 스마트 로직"""
    
    # 1. 명확한 규정 질문
    if question_type['type'] == 'regulation' and question_type['confidence'] == 'high':
        return True
    
    # 2. 명확한 인사말
    if question_type['type'] == 'greeting' and question_type['confidence'] == 'high':
        return False
    
    # 3. 모호한 경우 - 추가 분석
    if question_type['confidence'] == 'low':
        # 질문 길이와 복잡성 분석
        query_length = len(query.strip())
        if query_length < 10:  # 너무 짧은 질문
            return False
        
        # 규정 관련 키워드 밀도 계산
        regulation_keywords = ['규정', '규칙', '지침', '절차', '방법', '신청', '신고', '처리']
        keyword_density = sum(1 for keyword in regulation_keywords if keyword in query.lower()) / len(query.split())
        
        if keyword_density > 0.1:  # 키워드 밀도가 높으면 RAG 사용
            return True
    
    # 4. 기본값
    return question_type['needs_rag']

def rag_answer(question: str) -> Dict:
    """메타데이터 기반 하이브리드 RAG 답변 생성"""
    print(f"DEBUG: RAG 시스템 시작 - 질문: {question}")
    
    # 1단계: 메타데이터 기반 질문 분류
    question_type = _classify_question_type(question)
    print(f"DEBUG: 질문 분류: {question_type['type']} - {question_type['category']} (신뢰도: {question_type['confidence']})")
    
    # 2단계: 스마트 RAG 사용 여부 결정
    use_rag = _should_use_rag(question, question_type)
    print(f"DEBUG: RAG 사용 여부: {use_rag}")
    
    # 3단계: RAG 검색이 불필요한 경우
    if not use_rag:
        print(f"DEBUG: RAG 검색 생략 - {question_type['response_type']} 응답 생성")
        response = _generate_smart_greeting_response(question, question_type)
        return {
            "answer": response,
            "sources": [],
            "question_type": question_type,
            "rag_used": False
        }
    
    # 4단계: RAG 검색이 필요한 경우
    try:
        print(f"DEBUG: RAG 검색 시작 - {question_type['response_type']}")
        # 하이브리드 검색으로 관련 문서 검색
        retrieved = hybrid_search(question)
        print(f"DEBUG: 검색된 문서 수: {len(retrieved)}")
        
        # 검색 결과가 부족한 경우 (3개 미만)
        if len(retrieved) < 3:
            print(f"DEBUG: 검색 결과 부족 - 사용자 친화적 메시지 생성")
            return {
                "answer": "질문을 조금 더 명확하게 해주시면 감사합니다.",
                "sources": [],
                "question_type": question_type,
                "rag_used": False
            }
        
        # 답변 생성
        result = generate_answer(question, retrieved)
        print(f"DEBUG: RAG 시스템 완료")
        
        # 메타데이터 정보 추가
        result['question_type'] = question_type
        result['rag_used'] = True
        
        return result
    except Exception as e:
        print(f"DEBUG: RAG 시스템 오류: {str(e)}")
        return {
            "answer": f"죄송합니다. RAG 시스템에서 오류가 발생했습니다: {str(e)}",
            "sources": [],
            "question_type": question_type,
            "rag_used": False
        }

# 기존 함수들 (하위 호환성 유지)
def retrieve(question: str, top_k: int = None) -> List[Dict]:
    """기존 retrieve 함수 (하위 호환성)"""
    return hybrid_search(question, top_k)
