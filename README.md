# NAVI: 사내 업무 어시스턴트

## 팀 명 : 💊💊Dopamine

| 팀장                                                                                                                                                                                                  | 팀원                                                                                                                                                                                                | 팀원                                                                                                                                                                                             | 팀원                                                                                                                                                                                                    | 팀원                                                                                                                                                                                                 |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| <img src="./images/1.png" width="100" height="100"> <br> 최성장 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/GrowingChoi) | <img src="./images/2.png" width="100" height="100"> <br> 고범석 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/qjazk0000) | <img src="./images/3.png" width="100" height="100"> <br> 지형우 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/JI0617) | <img src="./images/4.png" width="100" height="100"> <br> 김동욱 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/boogiewooki02) | <img src="./images/5.png" width="100" height="100"> <br> 안수민 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/tnalsdk111) |

---

# 프로젝트 개요

## 📖 소개

<img width="444" height="312" alt="image" src="https://github.com/user-attachments/assets/6b6ea757-34b7-46e3-91b7-1476c9d2b9ae" />

**NAVI**는 사내 임직원들을 위한 **문서 기반 업무 지원 챗봇 서비스**입니다.  
**최신 AI 기술을 통해** 사내 내규 질문, 영수증 처리와 같이 반복적인 사무 업무를 자동화하여  
**편의성과 조직 전체의 생산성**을 높이는 것을 목표로 합니다.

---

## 💡 주제 선정 배경

### 신속·정확한 업무 지원
- **신속**한 정보 제공 → 업무 효율성 향상
- **정확**한 정보 제공 → 업무 일관성 유지

### 안정적인 지원 체계
- 24시간 **상시 지원** → 근무 시간 외 대응
- **온보딩** 효율화 → 신입 사원 교육 보완

---

## 🎯 목표

- **RAG 기반 챗봇** 구현
- **임직원을 위한 비용 처리 자동화 서비스** 구현
- **관리자 기능**을 통한 서비스 모니터링 및 유지 보수 실현

---

## 기술 스택 구성

| **Frontend**                                                                                                                                                                                                                    | **Backend**                                                                                                                                                                                                                                                                                                                         | **Model**                                                                                                                                                                                                                                                                                                                                       | **DB & Storage**                                                                                                                                                                                                                                       | **Deployment**                                                                                                                                                                                                                                                                                                                                                      | **Collaboration Tool**                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ![React](https://img.shields.io/badge/-React-61DAFB?style=for-the-badge&logo=react&logoColor=20232A)<br>![Tailwind CSS](https://img.shields.io/badge/-Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white) | ![Python](https://img.shields.io/badge/-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)<br>![Django](https://img.shields.io/badge/-Django-092E20?style=for-the-badge&logo=django&logoColor=white)<br>![LangChain](https://img.shields.io/badge/-LangChain-1E90FF?style=for-the-badge&logo=chainlink&logoColor=white) | ![Upstage](https://img.shields.io/badge/-Upstage-20232A?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyBoZWlnaHQ9IjFlbSIgc3R5bGU9ImZsZXg6bm9uZTtsaW5lLWhlaWdodDoxIiB2aWV3Qm94PSIwIDAgMjQgMjQiIHdpZHRoPSIxZW0iIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHRpdGxlPlVwc2F0ZTwvdGl0bGU+PHBhdGggZD0iTTE5Ljc2MyAwbC0uMzczIDEuMjk3aDIuNTk0TDIyLjM1NCAwaC0yLjU5MXpNMTYuMTkyIDIuMjdsLS4zNzYgMS4yOThoNS41MmwuMzctMS4yOThoLTUuNTE0ek0xMi44OTcgNC41NGwtLjM3NiAxLjI5OGg4LjE2NmwuMzctMS4yOThoLTguMTZ6TTIuODUgNi44MWwtLjM3NyAxLjI5OGgxNy41NjVsLjM3LTEuMjk3SDIuODQ4ek0zLjg4NCA5LjA4MWwtLjM3NiAxLjI5N0gxOS4zOWwuMzctMS4yOTdIMy44ODJ6TTQuMDg4IDI0bC4zNzYtMS4yOTdIMS44NjZMMS41IDI0aDIuNTg4ek03LjY2MiAyMS43M2wuMzc2LTEuMjk3SDIuNTE1TDIuMTUgMjEuNzNoNS41MTN6TTEwLjk1NyAxOS40NTlsLjM3Ni0xLjI5N2gtOC4xN2wtLjM2NiAxLjI5N2g4LjE2ek0yMS4wMDUgMTcuMTg5bC4zNzYtMS4yOTdIMy44MTJsLS4zNjYgMS4yOTdoMTcuNTU5ek0xOS45NjcgMTQuOTE5bC4zNzYtMS4yOTdINC40NjFsLS4zNjYgMS4yOTdoMTUuODcyek0xOC43ODYgMTIuNjQ5bC4zNzYtMS4yOTdINC4yNmwtLjM2NiAxLjI5N2gxNC44OTN6IiBmaWxsPSJ1cmwoI2xvYmUtaWNvbnMtdXBzYXRlLWZpbGwpIj48L3BhdGg+PGRlZnM+PGxpbmVhckdyYWRpZW50IGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiBpZD0ibG9iZS1pY29ucy11cHNhdGUtZmlsbCIgeDE9IjExLjkyNyIgeDI9IjExLjkyNyIgeTI9IjI0Ij48c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiNBRUJDRkUiPjwvc3RvcD48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM4MDVERkEiPjwvc3RvcD48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48L3N2Zz4=)<br>![GPT-4o](https://img.shields.io/badge/-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)<br>![Hugging Face](https://img.shields.io/badge/-Hugging_Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black) | ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)<br>![Qdrant](https://img.shields.io/badge/-Qdrant-FF4D4D?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTYgMjU2IiByb2xlPSJpbWciIGFyaWEtbGFiZWw9IlFkcmFudCI+CiAgPHRpdGxlPlFkcmFudDwvdGl0bGU+CiAgPGRlZnM+CiAgICA8ZmlsdGVyIGlkPSJzaGFkb3ciIHg9Ii0yMCUiIHk9Ii0yMCUiIHdpZHRoPSIxNDAiIGhlaWdodD0iMTQwJSI+CiAgICAgIDxmZURyb3BTaGFkb3cgZHg9IjAiIGR5PSIyIiBzdGREZXZpYXRpb249IjIiIGZsb29kLWNvbG9yPSIjMDAwIiBmbG9vZC1vcGFjaXR5PSIwLjI1Ii8+CiAgICA8L2ZpbHRlcj4KICA8L2RlZnM+CiAgPCEtLSBXaGl0ZSBRIC0tPgogIDxnIGZpbGw9IiNGRkZGRkYiIGZpbHRlcj0idXJsKCNzaGFkb3cpIj4KICAgIDxjaXJjbGUgY3g9IjEyMCIgY3k9IjEyMCIgcj0iNzIiLz4KICAgIDwhLS0gSW5uZXIgY3V0IGZvciByaW5nIC0tPgogICAgPGNpcmNsZSBjeD0iMTIwIiBjeT0iMTIwIiByPSI0OCIgc3R5bGU9ImZpbGw6IzAwMDAwMCIvPgogICAgPCEtLSBUYWlsIG9mIFEgLS0+CiAgICA8cmVjdCB4PSIxNjgiIHk9IjE1NiIgd2lkdGg9IjUyIiBoZWlnaHQ9IjIwIiByeD0iMTAiIHRyYW5zZm9ybT0icm90YXRlKC0zNSAxNjggMTU2KSIvPgogIDwvZz4KICA8IS0tIE1hc2sgdG8ga25vY2sgb3V0IGlubmVyIGNpcmNsZSAoY2xlYW4gZmluZykgLS0+CiAgPG1hc2sgaWQ9InJpbmctbWFzayI+CiAgICA8cmVjdCB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgZmlsbD0iI2ZmZiIvPgogICAgPGNpcmNsZSBjeD0iMTIwIiBjeT0iMTIwIiByPSI0OCIgZmlsbD0iIzAwMCIvPgogIDwvbWFzaz4KICA8ZyBmaWxsPSIjRkZGRkZGIiBtYXNrPSJ1cmwoI3JpbmctbWFzaykiPgogICAgPGNpcmNsZSBjeD0iMTIwIiBjeT0iMTIwIiByPSI3MiIvPgogIDwvZz4KICA8IS0tIFFgdGFpbCBhZ2FpbiBvbiB0b3AgLS0+CiAgPHJlY3QgeD0iMTY4IiB5PSIxNTYiIHdpZHRoPSI1MiIgaGVpZ2h0PSIyMCIgcng9IjEwIiB0cmFuc2Zvcm09InJvdGF0ZSgtMzUgMTY4IDE1NikiIGZpbGw9IiNGRkZGRkYiLz4KPC9zdmc+)<br>![AWS S3](https://img.shields.io/badge/-AWS_S3-569A31?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTYgMTZMNDEgMTZMNDggMzJMMjMgMzJaIiBmaWxsPSJ3aGl0ZSIvPjxwYXRoIGQ9Ik0yMyAzMkw0OCAzMkw0OCA0OEwyMyA0OFoiIGZpbGw9IndoaXRlIi8+PHBhdGggZD0iTTE2IDE2TDIzIDMyTDIzIDQ4TDE2IDMyWk0zMiAzMkw0OCAzMkw0OCA0OEwzMiA0OFoiIGZpbGw9IndoaXRlIi8+PC9zdmc+) | ![Docker](https://img.shields.io/badge/-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)<br>![AWS EC2](https://img.shields.io/badge/-AWS_EC2-FF9900?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB4PSIxNiIgeT0iMTYiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgcng9IjQiIHJ5PSI0IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjQiIGZpbGw9Im5vbmUiLz48L3N2Zz4=)<br>![Nginx](https://img.shields.io/badge/-Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)<br>![Gunicorn](https://img.shields.io/badge/-Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)<br>![Vercel](https://img.shields.io/badge/-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white) | ![GitHub](https://img.shields.io/badge/-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)<br>![Discord](https://img.shields.io/badge/-Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)<br>![Notion](https://img.shields.io/badge/-Notion-000000?style=for-the-badge&logo=notion&logoColor=white) |

<br><br>

## 🛠 시스템 구성<br/>

```
SKN13-FINAL-6TEAM/
├── backend/                            # 백엔드 서버
│   ├── adminapp/                      # 관리자 기능 앱
│   ├── authapp/                       # 로그인, 권한 관련 앱
│   ├── chatbot/                       # RAG 앱
│   │   └── services/
│   │       ├── answerer.py           # LLM 기반 RAG 답변 생성 및 품질 평가 모듈
│   │       ├── api.py                # RAG 시스템용 Django REST API 엔드포인트
│   │       ├── constants.py          # RAG 시스템 전역 상수 및 메타데이터 정의
│   │       ├── filters.py            # 도메인/타입/최신성 기반 Qdrant 검색 필터
│   │       ├── keyword_extractor.py  # LLM 및 정규식 기반 질문 키워드 추출기
│   │       ├── pipeline.py           # RAG 전체 파이프라인 및 워크플로우 관리
│   │       ├── rag_indexer.py        # 문서 임베딩 및 Qdrant 인덱싱
│   │       ├── rag_search.py         # 고급 RAG 검색 및 하이브리드 검색 엔진
│   │       └── rag_service.py        # RAG 환경설정, 프롬프트, 클라이언트/임베딩 관리
│   ├── receipt/                       # 영수증 처리 앱
│   │       └── utils.py              # 이미지 전처리 / 텍스트 추출
│   ├── documents/kisa_pdf            # 한국인터넷진흥원 사내규정
│   └── Dockerfile
│
├── frontend/                           # 프론트엔드 클라이언트
│   ├── public/
│   └── src/
│       ├── pages/
│       │    ├── Admin/
│       │    ├── Chat/
│       │    ├── Login/
│       │    └── MyPage/
│       └── services/                  # API 서비스
└── docker-compose.yml                 # Docker Compose 설정
```

### 인터페이스 (Frontend)

- SPA 기반 웹 인터페이스 제공
- 텍스트 입력 및 이미지 파일 업로드
- 응답 텍스트 및 파일(Excel 등) 제공  

### 서버 (Backend)
- 사용자 요청 처리 및 데이터베이스 작업  
- 인증 및 권한 관리  


### 관계형 데이터베이스
- 사용자 정보 저장  
- 사용자 대화 관련 내용 저장  
- 영수증 파일 저장  


### 벡터 데이터베이스
- 사내 문서 임베딩 벡터 저장
- 청크 메타데이터 저장
- 유사 문서 검색 수행  


### AI 모델

- **GPT-4o (LLM)** – 사용자 입력 및 추출 문맥에 대한 자연어 응답 생성
- **Upstage Information Extract (OCR)** – 이미지 내 텍스트 추출
- **nlpai-lab/KoE5 (문서 임베딩)** – 문서 벡터화

### 배포 환경
- **AWS EC2** – Backend 운영
- **AWS RDS** – 관계형DB 운영
- **AWS S3** – 비정형 데이터 저장
- **Vercel** – Frontend 배포 및 CI/CD  
- **Docker** – Qdrant 및 서버 컨테이너 실행  

---

## 시스템 아키텍처
<img src="images\시스템 아키텍처.png" width="1000" >

---

## DB 구조와 역할
<img src="images\DB 구조와 역할.png" width="1000" >

---

## 서비스 구현 화면

#### 1. 업무 가이드 챗봇
![readme용 시연영상](https://github.com/user-attachments/assets/d7efef5e-a4bb-48df-b47a-0c65f9730340)

#### 2. 영수증 이미지 처리
![readme용 영수증처리 영상](https://github.com/user-attachments/assets/2ac17db3-7ebc-452f-8026-392ec6ae28de)

#### 3. 관리자 페이지
<img width="1919" height="903" alt="스크린샷 2025-09-15 102432" src="https://github.com/user-attachments/assets/c4607c08-99e9-4f94-9351-ea2f2e0ceba3" />
<img width="1918" height="903" alt="스크린샷 2025-09-15 102726" src="https://github.com/user-attachments/assets/4b3edac0-056a-4889-8727-4925a233d355" />

---

## 📞 Q&A

- **문의**: NAVI에 대해 궁금한 점은 GitHub Issues로 남겨주세요.
