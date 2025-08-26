"""
답변 생성기
OpenAI를 사용하여 컨텍스트 기반 답변을 생성합니다.
기존 OpenAI SDK 방식을 유지합니다.
"""

from typing import List, Dict, Any, Optional
from django.conf import settings

def make_answer(query: str, contexts: List[Dict[str, Any]], api_key: Optional[str] = None) -> str:
    """
    컨텍스트를 기반으로 질문에 대한 답변 생성
    
    Args:
        query: 사용자 질문
        contexts: 검색된 컨텍스트 리스트
        api_key: OpenAI API 키 (None이면 settings에서 가져옴)
    
    Returns:
        생성된 답변 문자열
    """
    if not contexts:
        return "죄송합니다. 질문과 관련된 문서를 찾을 수 없습니다."
    
    # 컨텍스트 포맷팅
    formatted_contexts = []
    for i, ctx in enumerate(contexts, 1):
        file_name = ctx.get('file_name', '알 수 없음')
        pages = ctx.get('pages', '알 수 없음')
        domain = ctx.get('domain_primary', '알 수 없음')
        text = ctx.get('text', '내용 없음')
        
        # 텍스트 길이 제한
        if len(text) > 500:
            text = text[:500] + "..."
        
        formatted_contexts.append(f"[{i}] file={file_name}, pages={pages}, domain={domain}\n{text}")
    
    context_text = "\n\n".join(formatted_contexts)
    
    # 시스템 프롬프트
    system_prompt = """당신은 한국인터넷진흥원 규정/지침/규칙 RAG 보조자입니다.

답변 시 다음을 준수하세요:
1. 아래 컨텍스트를 근거로만 답변
2. 컨텍스트에 없는 내용은 추측하지 말고 "해당 근거를 찾지 못했습니다"라고 답변
3. 근거가 되는 파일명과 페이지를 함께 표기
4. 한국어로 간결하고 정확하게 답변
5. 문서 인용 기반 안내이며 법적 해석/자문 아님

답변 형식:
[답변 내용]

참고 문서:
- [파일명] p.[페이지]
- [파일명] p.[페이지]"""

    # 사용자 프롬프트
    user_prompt = f"""컨텍스트:
{context_text}

질문:
{query}

위 컨텍스트를 근거로 답변해주세요."""

    try:
        # OpenAI SDK import (기존 방식 유지)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)
            model = "gpt-4o-mini"
        except ImportError:
            # 구버전 OpenAI SDK 지원
            import openai
            openai.api_key = api_key or settings.OPENAI_API_KEY
            model = "gpt-4o-mini"
        
        try:
            # OpenAI 1.x 방식
            response = client.chat.completions.create(
                model=model,
                temperature=0.1,
                max_tokens=1500,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            answer = response.choices[0].message.content.strip()
        except AttributeError:
            # OpenAI 0.x 방식
            response = openai.ChatCompletion.create(
                model=model,
                temperature=0.1,
                max_tokens=1500,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            answer = response.choices[0].message.content.strip()
        
        return answer
        
    except Exception as e:
        print(f"OpenAI 답변 생성 실패: {e}")
        return f"죄송합니다. AI 답변 생성 중 오류가 발생했습니다: {str(e)}"

def format_context_for_display(contexts: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    컨텍스트를 프론트엔드 표시용으로 포맷팅
    
    Args:
        contexts: 원본 컨텍스트 리스트
    
    Returns:
        포맷팅된 컨텍스트 리스트
    """
    formatted = []
    
    for ctx in contexts:
        formatted.append({
            'file_name': ctx.get('file_name', '알 수 없음'),
            'pages': ctx.get('pages', '알 수 없음'),
            'domain': ctx.get('domain_primary', '알 수 없음'),
            'score': ctx.get('score', 0.0),
            'text_preview': ctx.get('text', '')[:200] + '...' if len(ctx.get('text', '')) > 200 else ctx.get('text', '')
        })
    
    return formatted

def validate_answer_quality(answer: str, query: str) -> Dict[str, Any]:
    """
    답변 품질 검증
    
    Args:
        answer: 생성된 답변
        query: 원본 질문
    
    Returns:
        품질 검증 결과
    """
    quality_score = 0
    issues = []
    
    # 답변 길이 검증
    if len(answer) < 50:
        issues.append("답변이 너무 짧습니다")
        quality_score -= 2
    elif len(answer) > 2000:
        issues.append("답변이 너무 깁니다")
        quality_score -= 1
    
    # 근거 문서 포함 여부
    if "참고 문서" in answer or "p." in answer:
        quality_score += 2
    else:
        issues.append("근거 문서 정보가 부족합니다")
        quality_score -= 1
    
    # 질문과의 관련성
    query_keywords = set(query.lower().split())
    answer_keywords = set(answer.lower().split())
    common_keywords = query_keywords.intersection(answer_keywords)
    
    if len(common_keywords) >= 2:
        quality_score += 1
    else:
        issues.append("질문과 답변의 관련성이 낮습니다")
        quality_score -= 1
    
    # 최종 점수 정규화 (0-10)
    final_score = max(0, min(10, quality_score + 5))
    
    return {
        'score': final_score,
        'issues': issues,
        'common_keywords': list(common_keywords),
        'quality_level': '우수' if final_score >= 8 else '양호' if final_score >= 6 else '보통' if final_score >= 4 else '미흡'
    } 