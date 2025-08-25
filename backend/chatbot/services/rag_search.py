"""
RAG 검색기
도메인 분류를 활용한 고급 검색을 담당합니다.
기존 검색 로직을 확장합니다.
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from django.conf import settings
from .constants import RAG_CONFIG, EXISTING_COLLECTION
from .filters import build_qdrant_filter, build_advanced_filter

class RagSearcher:
    """
    도메인 분류 기반 RAG 검색기
    """
    
    def __init__(self, qdrant_host: str = None, qdrant_port: int = None, collection_name: str = None):
        """
        RAG 검색기 초기화
        
        Args:
            qdrant_host: Qdrant 호스트 (기본값: settings에서 가져옴)
            qdrant_port: Qdrant 포트 (기본값: settings에서 가져옴)
            collection_name: 컬렉션 이름 (기본값: 기존 컬렉션)
        """
        # Qdrant 클라이언트 초기화
        self.qdrant_host = qdrant_host or getattr(settings, 'QDRANT_HOST', 'qdrant')
        self.qdrant_port = qdrant_port or getattr(settings, 'QDRANT_PORT', 6333)
        self.collection_name = collection_name or EXISTING_COLLECTION
        
        self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
        
        # 임베딩 모델 초기화
        self.embedder = SentenceTransformer("nlpai-lab/KoE5")
        
        # 검색 설정
        self.default_top_k = RAG_CONFIG.get('CHUNK_SIZE', 8)
    
    def search(self, query: str, flt: Optional[Dict[str, Any]] = None, top_k: int = None) -> List[Dict[str, Any]]:
        """
        질문에 대한 검색 수행
        
        Args:
            query: 검색 질문
            flt: Qdrant 필터
            top_k: 반환할 결과 수
        
        Returns:
            검색 결과 리스트
        """
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            # 질문 임베딩
            query_vector = self.embedder.encode([query])[0].tolist()
            
            # Qdrant 검색
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=flt,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )
            
            # 결과 포맷팅
            formatted_results = []
            for result in search_results:
                payload = result.payload
                # 기존 컬렉션 구조에 맞게 수정
                source = payload.get('source', '')
                file_path = payload.get('file_path', '')
                
                # 파일명에서 도메인과 타입 추출
                from .constants import DOMAIN_CLASSIFICATION, DOCUMENT_TYPE_PATTERNS
                
                # 파일 타입 분류
                file_type = '기타'
                for prefix, info in DOCUMENT_TYPE_PATTERNS.items():
                    if source.startswith(prefix):
                        file_type = info['type']
                        break
                
                # 도메인 분류 (파일명 기반)
                domain_primary = '일반'
                for domain, info in DOMAIN_CLASSIFICATION.items():
                    if any(keyword in source for keyword in info['keywords']):
                        domain_primary = domain
                        break
                
                formatted_result = {
                    'id': str(result.id),
                    'score': result.score,
                    'text': payload.get('text', ''),
                    'file_name': source,
                    'pages': payload.get('page', ''),
                    'domain_primary': domain_primary,
                    'domain_secondary': [],
                    'file_type': file_type,
                    'chunk_index': 0,
                    'chunk_char_len': len(payload.get('text', '')),
                    'version': 1
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            print(f"RAG 검색 실패: {e}")
            return []
    
    def search_by_domain(self, query: str, domain: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        특정 도메인으로 제한된 검색
        
        Args:
            query: 검색 질문
            domain: 도메인명
            top_k: 반환할 결과 수
        
        Returns:
            검색 결과 리스트
        """
        filter_dict = build_qdrant_filter(domain_list=[domain])
        return self.search(query, flt=filter_dict, top_k=top_k)
    
    def search_by_file_type(self, query: str, file_type: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        특정 파일 타입으로 제한된 검색
        
        Args:
            query: 검색 질문
            file_type: 파일 타입 (정관, 규정, 규칙, 지침)
            top_k: 반환할 결과 수
        
        Returns:
            검색 결과 리스트
        """
        filter_dict = build_qdrant_filter(file_type=file_type)
        return self.search(query, flt=filter_dict, top_k=top_k)
    
    def hybrid_search(self, query: str, domain_list: Optional[List[str]] = None, 
                     file_type: Optional[str] = None, top_k: int = None) -> List[Dict[str, Any]]:
        """
        하이브리드 검색 (도메인 + 파일타입 + 키워드)
        필터 문제로 인해 현재는 벡터 검색만 사용
        
        Args:
            query: 검색 질문
            domain_list: 도메인 리스트 (현재 사용하지 않음)
            file_type: 파일 타입 (현재 사용하지 않음)
            top_k: 반환할 결과 수
        
        Returns:
            검색 결과 리스트
        """
        # 필터 문제로 인해 현재는 필터 없이 검색
        # TODO: 필터 문제 해결 후 도메인 기반 검색 활성화
        
        # 벡터 검색만 수행
        results = self.search(query, flt=None, top_k=top_k)
        
        # 결과 재순위화 (도메인 관련성 + 벡터 점수)
        if results:
            results = self._rerank_results(query, results)
        
        return results
    
    def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        검색 결과 재순위화
        
        Args:
            query: 원본 질문
            results: 검색 결과
        
        Returns:
            재순위화된 결과
        """
        query_lower = query.lower()
        
        for result in results:
            # 도메인 관련성 점수 계산
            domain_score = 0
            domain_primary = result.get('domain_primary', '')
            
            # 질문에 도메인 키워드가 포함된 경우 점수 부여
            if domain_primary:
                from .constants import DOMAIN_CLASSIFICATION
                domain_keywords = DOMAIN_CLASSIFICATION.get(domain_primary, {}).get('keywords', [])
                
                for keyword in domain_keywords:
                    if keyword in query_lower:
                        domain_score += 1
            
            # 최종 점수 계산 (도메인 점수 + 벡터 점수)
            result['final_score'] = domain_score + result.get('score', 0)
        
        # 최종 점수로 정렬
        results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        컬렉션 정보 조회
        
        Returns:
            컬렉션 정보
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': self.collection_name,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': 'active'
            }
        except Exception as e:
            return {
                'name': self.collection_name,
                'error': str(e),
                'status': 'error'
            }
    
    def health_check(self) -> bool:
        """
        검색기 상태 확인
        
        Returns:
            정상 여부
        """
        try:
            # 간단한 검색 테스트
            test_results = self.search("테스트", top_k=1)
            return True
        except Exception:
            return False 