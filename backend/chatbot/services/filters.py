"""
메타데이터 필터
도메인 분류와 Qdrant 필터 생성을 담당합니다.
기존 컬렉션 구조에 맞게 수정되었습니다.
"""

from typing import List, Optional, Dict, Any
from .constants import DOMAIN_CLASSIFICATION, DOMAIN_HINTS, DOCUMENT_TYPE_PATTERNS

def guess_domains_from_keywords(keywords: List[str]) -> List[str]:
    """
    키워드 기반으로 도메인 후보를 추정
    
    Args:
        keywords: 추출된 키워드 리스트
    
    Returns:
        추정된 도메인 리스트 (중복 제거, 빈도순 정렬)
    """
    domain_scores = {}
    
    for keyword in keywords:
        if keyword in DOMAIN_HINTS:
            domain = DOMAIN_HINTS[keyword]
            domain_scores[domain] = domain_scores.get(domain, 0) + 1
    
    # 점수 순으로 정렬
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    
    # 도메인만 반환
    return [domain for domain, score in sorted_domains]

def get_domain_keywords(domain: str) -> List[str]:
    """
    특정 도메인의 키워드 리스트 반환
    
    Args:
        domain: 도메인명
    
    Returns:
        해당 도메인의 키워드 리스트
    """
    return DOMAIN_CLASSIFICATION.get(domain, {}).get('keywords', [])

def build_qdrant_filter(domain_list: Optional[List[str]] = None, 
                        file_type: Optional[str] = None,
                        version: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Qdrant 검색용 필터 생성 (기존 컬렉션 구조에 맞게 수정)
    
    Args:
        domain_list: 도메인 리스트
        file_type: 파일 타입 (정관, 규정, 규칙, 지침)
        version: 버전 (기존 컬렉션에는 사용하지 않음)
    
    Returns:
        Qdrant 필터 딕셔너리
    """
    filter_conditions = []
    
    # 도메인 필터 (기존 컬렉션에는 domain_primary가 없으므로 source 필드로 검색)
    if domain_list:
        if len(domain_list) == 1:
            # 단일 도메인 - source 필드에서 키워드 검색
            domain_keywords = []
            for domain in domain_list:
                if domain in DOMAIN_CLASSIFICATION:
                    domain_keywords.extend(DOMAIN_CLASSIFICATION[domain]['keywords'])
            
            if domain_keywords:
                # 키워드 중 하나라도 포함된 문서 검색
                keyword_conditions = []
                for keyword in domain_keywords:
                    keyword_conditions.append({
                        "key": "source",
                        "match": {"text": {"contains": keyword}}
                    })
                filter_conditions.append({
                    "should": keyword_conditions
                })
    
    # 파일 타입 필터 (source 필드의 prefix로 검색)
    if file_type:
        prefix_conditions = []
        for prefix, info in DOCUMENT_TYPE_PATTERNS.items():
            if info['type'] == file_type:
                prefix_conditions.append({
                    "key": "source",
                    "match": {"text": {"contains": prefix}}
                })
                break
        
        if prefix_conditions:
            filter_conditions.append({
                "should": prefix_conditions
            })
    
    # 버전 필터는 기존 컬렉션에 없으므로 제거
    
    # 필터가 있으면 must 조건으로 묶기
    if filter_conditions:
        return {"must": filter_conditions}
    
    return None

def build_advanced_filter(domain_list: Optional[List[str]] = None,
                         file_type: Optional[str] = None,
                         min_recency: Optional[str] = None,
                         include_secondary: bool = False) -> Optional[Dict[str, Any]]:
    """
    고급 필터 생성 (보조 도메인 포함)
    
    Args:
        domain_list: 도메인 리스트
        file_type: 파일 타입
        min_recency: 최소 최신성 (기존 컬렉션에는 사용하지 않음)
        include_secondary: 보조 도메인 포함 여부
    
    Returns:
        고급 Qdrant 필터
    """
    base_filter = build_qdrant_filter(domain_list, file_type)
    
    if not base_filter:
        return None
    
    # 최신성 필터는 기존 컬렉션에 없으므로 제거
    
    # 보조 도메인 포함 옵션 (기존 컬렉션에는 domain_secondary가 없으므로 제거)
    
    return base_filter

def get_filter_description(filter_dict: Optional[Dict[str, Any]]) -> str:
    """
    필터를 사람이 읽기 쉬운 설명으로 변환
    
    Args:
        filter_dict: Qdrant 필터 딕셔너리
    
    Returns:
        필터 설명 문자열
    """
    if not filter_dict:
        return "필터 없음 (전체 검색)"
    
    descriptions = []
    
    if 'must' in filter_dict:
        for condition in filter_dict['must']:
            if 'key' in condition and 'match' in condition:
                key = condition['key']
                if key == 'source':
                    descriptions.append("파일명 기반 검색")
    
    return " | ".join(descriptions) if descriptions else "필터 없음" 