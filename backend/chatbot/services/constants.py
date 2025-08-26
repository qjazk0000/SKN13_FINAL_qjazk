"""
한국인터넷진흥원 규정 문서 도메인 분류 상수
기존 구조를 보존하면서 도메인 분류 기능을 추가합니다.
"""

# 도메인 분류 체계
DOMAIN_CLASSIFICATION = {
    '인사관리': {
        'keywords': ['인사', '채용', '급여', '휴가', '육아휴직', '연차', '출장', '복무', '교육', '훈련'],
        'description': '인사 정책, 급여, 복무, 교육 등 인적자원 관리'
    },
    '재무관리': {
        'keywords': ['회계', '예산', '감사', '재정', '계약', '수수료', '자산'],
        'description': '회계, 예산, 감사, 계약, 자산 등 재무 관련'
    },
    '보안관리': {
        'keywords': ['보안', '정보보호', '개인정보', '민원', '신고'],
        'description': '보안 정책, 정보보호, 개인정보 관리'
    },
    '기술관리': {
        'keywords': ['기술', 'IT', '정보화', '전자서명', '시스템'],
        'description': '기술 정책, IT 시스템, 정보화'
    },
    '행정관리': {
        'keywords': ['문서', '자료', '기록', '홍보'],
        'description': '문서 관리, 자료 관리, 홍보 업무'
    },
    '경영관리': {
        'keywords': ['경영', '성과', '내부통제', '이해충돌', '조직', '직제'],
        'description': '경영 정책, 성과 관리, 조직 관리'
    }
}

# 파일명 패턴 기반 문서 타입 분류
DOCUMENT_TYPE_PATTERNS = {
    '1_': {
        'type': '정관',
        'description': '기본법령',
        'level': 1
    },
    '2_': {
        'type': '규정',
        'description': '운영규정, 관리규정',
        'level': 2
    },
    '3_': {
        'type': '규칙',
        'description': '세부규칙, 실행규칙',
        'level': 3
    },
    '4_': {
        'type': '지침',
        'description': '업무지침, 운영지침',
        'level': 4
    }
}

# 도메인 힌트 (키워드 → 도메인 매핑)
DOMAIN_HINTS = {}
for domain, info in DOMAIN_CLASSIFICATION.items():
    for keyword in info['keywords']:
        DOMAIN_HINTS[keyword] = domain

# 최신성 기준 (등록일자 기반)
RECENCY_THRESHOLDS = {
    '최신': {'year': 24, 'score': 3, 'description': '2024년 이후'},
    '최근': {'year': 22, 'score': 2, 'description': '2022-2023년'},
    '기존': {'year': 21, 'score': 1, 'description': '2021년 이전'}
}

# RAG 시스템 설정
RAG_CONFIG = {
    'CHUNK_SIZE': 1000,
    'CHUNK_OVERLAP': 200,
    'MIN_DOC_CHARS': 1200,
    'MIN_PAGE_CHARS': 600,
    'MIN_CHUNK_CHARS': 400,
    'BATCH_SIZE': 256,
    'VERSION': 2
}

# 기존 컬렉션 이름 (보존)
EXISTING_COLLECTION = 'regulations_final' 