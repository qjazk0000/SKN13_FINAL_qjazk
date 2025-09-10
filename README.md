# NAVI: 사내 업무 어시스턴트

## 팀 명 : 💊💊Dopamine
| 팀장 | 팀원 | 팀원 | 팀원 | 팀원 |
|------|------|------|------|------|
| <img src="./images/1.png" width="100" height="100"> <br> 최성장 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/GrowingChoi) | <img src="./images/2.png" width="100" height="100"> <br> 고범석 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/qjazk0000) | <img src="./images/3.png" width="100" height="100"> <br> 지형우 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/JI0617) | <img src="./images/4.png" width="100" height="100"> <br> 김동욱 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/boogiewooki02) | <img src="./images/5.png" width="100" height="100"> <br> 안수민 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/tnalsdk111) | 

---

# 프로젝트 개요

## 📖 소개
<img width="444" height="312" alt="image" src="https://github.com/user-attachments/assets/6b6ea757-34b7-46e3-91b7-1476c9d2b9ae" />


**NAVI**는 사내 임직원들을 위한 **문서 기반 업무 지원 LLM 챗봇 서비스**입니다.  
사내 내규 질문, 영수증 처리와 같이 반복적인 사무 업무를 자동화하여  
**편의성과 조직 전체의 생산성**을 높이는 것을 목표로 합니다.  

NAVI는 텍스트, 이미지, 문서 파일 등 다양한 입력 형식을 지원하며,  
LLM 기반 자연어 처리 기술과 벡터 데이터베이스를 활용하여  
정확하고 신속한 업무 지원을 제공합니다.

---

## 💡 주제 선정 배경
<img width="513" height="313" alt="image" src="https://github.com/user-attachments/assets/e5162ca5-9959-432d-b43f-30cc288d01ca" />

1. **업무 효율성 및 생산성 향상 필요성**
→ 신속한 정보 제공을 통한 업무 시간 단축

2. **일관된 정보 제공의 중요성**
→ 정확한 정보 제공을 통한 업무 처리 일관성 유지
 
3. **24시간 지속적인 업무 지원 필요**
→ 근무 시간 외 긴급한 업무 문의에 대한 대처

4. **신규 입사자 온보딩 과정 효율화**
→ 기존 신입 사원 교육 과정에서 모든 내규와 업무 프로세스를 전수하는 데 한계

---

## 🎯 목표
- **사내 문서 기반 LLM 챗봇** 구축
- **임직원 지원형 비용 처리(영수증 등록) 서비스** 구현
- 반복적인 사무 업무의 효율성 향상

---

## 기술 스택 구성
<img width="844" height="406" alt="image" src="https://github.com/user-attachments/assets/2e8209d2-226a-40dd-8474-d5bc21bd6e23" />

## 🛠 시스템 구성

### 🖥️ 인터페이스 (Frontend)
- 단일 채팅창 기반 UI 제공  
- 텍스트 입력 및 파일 업로드(이미지, 문서 등) 지원  
- 응답 텍스트 및 파일(PDF 등) 제공  
- **기술 스택:** React.js, Tailwind CSS  



### 서버 (Backend)
- 입력 데이터 분기 및 체인 라우팅 (텍스트 / 이미지 / 문서)  
- 사용자 요청 처리 및 데이터베이스 저장  
- 인증 및 권한 관리  
- **기술 스택:** Django, LangChain, Uvicorn, Gunicorn, Nginx  

### 관계형 데이터베이스
- 사용자 정보 저장  
- 대화 내용 저장  
- 대화방 메타데이터 저장 (제목, 생성 시간 등)  
- 영수증 파일 저장  
- **기술 스택:** PostgreSQL (AWS RDS)  

### 벡터 데이터베이스
- 사내 문서 임베딩 벡터 저장  
- 유사 문서 검색 수행  
- **기술 스택:** Qdrant (Docker 기반 실행)  

### AI 모델
- **GPT-4o (LLM)** – 사용자 입력에 대한 자연어 응답 생성  
- **Upstage A.X-4.0-VL-Light (OCR)** – 이미지 내 텍스트 추출  
- **nlpai-lab/KoE5 (임베딩)** – 문서 벡터화 및 Qdrant 저장  

### 배포 환경
- AWS EC2 – Backend 및 DB 서비스 운영  
- Vercel – Frontend 배포 및 CI/CD  
- Docker – Qdrant 및 서버 컨테이너 실행  

---

## 시연 영상
![middle_video](https://github.com/user-attachments/assets/9e90b412-9a4a-466f-bd70-dcb94a0ad040)





## 🚨 데이터 보존 주의사항

**절대 `docker compose down -v` 사용하지 말 것!** 이 옵션은 볼륨을 삭제하여 Qdrant 데이터가 영구 손실됩니다.

데이터는 `./qdrant_storage`(스토리지) / `./qdrant_snapshots`(스냅샷)에 보관됩니다.

## 🚀 기동/중단

- **기동**: `make up`  
- **중단(데이터 보존)**: `make down`

## 📊 상태 확인

**Qdrant**: `curl -s http://localhost:6333/collections | jq .`

## 💾 스냅샷/복구

- **스냅샷**: `make snap`  
- **복구**: `make restore location=/qdrant/snapshots/<your-snapshot>.snapshot`

## 🔧 컬렉션 초기화

백엔드가 자동 보장(`python manage.py qdrant_init`), 필요 시 수동 실행 가능

---

## 📞 Q&A
- **문의**: LLM과 RAG 기반 NAVI에 대한 궁금증은 GitHub Issues로 남겨주세요.
