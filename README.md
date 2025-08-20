# NAVI

## 팀 명 : 💊💊Dopamine
## 👥 팀원소개
| 팀장 | 팀원 | 팀원 | 팀원 | 팀원 |
|------|------|------|------|------|
| <img src="./images/1.png" width="100" height="100"> <br> 최성장 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/GrowingChoi) | <img src="./images/2.png" width="100" height="100"> <br> 고범석 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/qqqppma) | <img src="./images/3.png" width="100" height="100"> <br> 지형우 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/subin0821) | <img src="./images/4.png" width="100" height="100"> <br> 김동욱 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/oowwixxj819) | <img src="./images/5.png" width="100" height="100"> <br> 안수민 [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/oowwixxj819) | 


# 프로젝트 개요

## 📖 소개
<img width="444" height="312" alt="image" src="https://github.com/user-attachments/assets/6b6ea757-34b7-46e3-91b7-1476c9d2b9ae" />


**NAVI**는 사내 임직원들을 위한 **문서 기반 업무 지원 LLM 챗봇 서비스**입니다.  
회의록 요약, 업무 가이드 제공, 이미지·문서 처리 등 반복적인 사무 업무를 자동화하여  
**편의성과 조직 전체의 생산성**을 높이는 것을 목표로 합니다.  

NAVI는 텍스트, 이미지, 문서 파일 등 다양한 입력 형식을 지원하며,  
LLM 기반 자연어 처리 기술과 벡터 데이터베이스를 활용하여  
정확하고 신속한 업무 지원을 제공합니다.

---

## 💡 주제 선정 배경
<img width="513" height="313" alt="image" src="https://github.com/user-attachments/assets/e5162ca5-9959-432d-b43f-30cc288d01ca" />

사내 구성원들은 업무 매뉴얼 확인, 회의 요약, 문서 작성 등을 위해  
반복적인 질의응답과 수작업을 수행하고 있습니다.  
특히 신입 직원이나 부서 간 협업 시에는 필요한 업무 가이드라인을 파악하기 어려워,  
매번 담당자에게 문의하거나 문서를 직접 찾아야 하는 비효율이 발생합니다.

최근에는 텍스트뿐만 아니라 이미지(화이트보드, 스캔 문서 등),  
문서 파일 등 다양한 입력이 공존하는 환경 속에서 이를 유연하게 처리할 수 있는 **스마트한 시스템**의 필요성이 높아지고 있습니다.

또한, LLM 기반 자연어 이해 및 생성 기술의 발전은  
업무 가이드 제공과 반복 업무 자동화를 통해  
조직의 능률을 극대화할 수 있는 새로운 기회를 제공합니다.  
이에 따라 **다양한 입력 형태에 대응하고, 업무 가이드와 문서 자동화를 통합적으로 지원하는 챗봇 시스템**을 기획하게 되었습니다.

---

## 🎯 목표
- **사내 문서 기반 LLM 챗봇** 구축
- **임직원 지원형 비용 처리(영수증 등록) 서비스** 구현
- 반복적인 사무 업무의 효율성 향상

---

## 기술 스택 구성
<img width="844" height="406" alt="image" src="https://github.com/user-attachments/assets/2e8209d2-226a-40dd-8474-d5bc21bd6e23" />

## 🛠 시스템 구성
### **인터페이스 (Frontend)**
- 단일 채팅창 기반 UI
- 텍스트 입력 및 파일 업로드 (이미지, 문서 등)
- 응답 텍스트 및 파일(PDF 등) 제공
- **기술 스택**: React


### **서버 (Backend)**
- 입력 분기 및 체인 라우팅 (텍스트 / 이미지 / 문서)
- 사용자 요청 처리 및 DB 저장
- 인증 및 권한 관리
- **기술 스택**: Django

### **벡터 데이터베이스 (Vector DB)**
- 사내 문서 임베딩 벡터 저장
- 유사 문서 검색
- **기술 스택**: Qdrant

### **AI 모델**
- gpt-4o (LLM)
- A.X-4.0-VL-Light (OCR)
- nlpai-lab/KoE5 (문서 임베딩)

### **데이터베이스 (RDB)**
- 사용자 정보 저장
- 대화 내용 저장
- 대화방 메타데이터 저장 (제목, 생성 시간 등)
- 영수증 파일 저장
- **기술 스택**: PostgreSQL

### **배포 환경**
- **기술 스택**: AWS EC2, Vercel, Docker

### 시연영상
![middle_video](https://github.com/user-attachments/assets/9e90b412-9a4a-466f-bd70-dcb94a0ad040)

---

## 📅 향후 계획
- 영수증 처리 등록 시스템 구축
- Qdrant의 메타필터링 기능을 적용하여, RAG시스템기반의 검색 성능향상.

---

## 🚨 데이터 보존 주의사항

**절대 `docker compose down -v` 사용하지 말 것!** 이 옵션은 볼륨을 삭제하여 Qdrant 데이터가 영구 손실됩니다.

데이터는 `./qdrant_storage`(스토리지) / `./qdrant_snapshots`(스냅샷)에 보관됩니다.

## 🚀 기동/중단

**기동**: `make up`  
**중단(데이터 보존)**: `make down`

## 📊 상태 확인

**Qdrant**: `curl -s http://localhost:6333/collections | jq .`

## 💾 스냅샷/복구

**스냅샷**: `make snap`  
**복구**: `make restore location=/qdrant/snapshots/<your-snapshot>.snapshot`

## 🔧 컬렉션 초기화

백엔드가 자동 보장(`python manage.py qdrant_init`), 필요 시 수동 실행 가능

---

## 📞 Q&A
- **문의**: LLM과 RAG 기반 NAVI에 대한 궁금증은 GitHub Issues로 남겨주세요.
