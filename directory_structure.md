# SKN13-FINAL-6Team 프로젝트 디렉토리 구조

## 📁 프로젝트 루트
```
SKN13-FINAL-6Team/
├── .git/                          # Git 버전 관리 디렉토리
├── backend/                       # 백엔드 (Django) 애플리케이션
├── frontend/                      # 프론트엔드 (React) 애플리케이션
├── documents/                     # 문서 및 자료
└── README.md                      # 프로젝트 README 파일
```

## 🐍 Backend (Django)
```
backend/
├── chatbot/                       # 챗봇 애플리케이션
│   ├── __init__.py               # Python 패키지 초기화
│   ├── models.py                 # 데이터 모델 정의
│   ├── serializers.py            # API 직렬화
│   ├── urls.py                   # URL 라우팅
│   └── views.py                  # 뷰 로직
├── config/                       # Django 설정 디렉토리
├── templates/                    # HTML 템플릿
│   ├── chatbot.html             # 챗봇 페이지 템플릿
│   └── login.html               # 로그인 페이지 템플릿
├── manage.py                     # Django 관리 스크립트
├── requirements.txt              # Python 의존성 목록
└── Dockerfile                    # Docker 컨테이너 설정
```

## ⚛️ Frontend (React)
```
frontend/
├── public/                       # 정적 파일
│   └── index.html               # 메인 HTML 파일
├── src/                         # 소스 코드
│   ├── pages/                   # 페이지 컴포넌트
│   │   ├── Chat.jsx            # 챗봇 페이지
│   │   ├── Login.jsx           # 로그인 페이지
│   │   └── MyPage.jsx          # 마이페이지
│   ├── App.jsx                 # 메인 앱 컴포넌트
│   └── index.js                # 앱 진입점
├── package.json                 # Node.js 의존성 및 스크립트
└── Dockerfile                   # Docker 컨테이너 설정
```

## 📚 Documents
```
documents/
└── kisa_pdf/                    # KISA 관련 PDF 문서들 (총 108개 파일)
    ├── 지침서류/                 # 4_XX 시리즈 (70개 파일)
    └── 규칙서류/                 # 3_XX 시리즈 (38개 파일)
```

## 📋 프로젝트 개요

이 프로젝트는 **SKN13-FINAL-6Team**으로, 다음과 같은 구조로 구성되어 있습니다:

### 🏗️ 아키텍처
- **Backend**: Django 기반의 Python 백엔드
- **Frontend**: React 기반의 JavaScript 프론트엔드
- **Containerization**: Docker를 통한 컨테이너화
- **Documentation**: KISA 관련 PDF 문서 보관

### 🎯 주요 기능
- **챗봇 시스템**: AI 기반 대화 시스템
- **사용자 인증**: 로그인/로그아웃 기능
- **마이페이지**: 사용자 개인 정보 관리
- **문서 관리**: KISA 관련 지침 및 규칙 문서 보관

### 📁 파일 설명
- `README.md`: 프로젝트 개요 및 사용법
- `requirements.txt`: Python 패키지 의존성
- `package.json`: Node.js 패키지 의존성 및 스크립트
- `Dockerfile`: 각각 백엔드와 프론트엔드용 Docker 설정

---

*마지막 업데이트: 2024년* 