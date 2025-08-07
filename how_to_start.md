# 개발 환경 시작 가이드

## 사전 요구사항

1. **Python 3.8+** 설치
2. **Node.js 14+** 설치
3. **PostgreSQL** 설치 (또는 Docker 사용)

## 방법 1: 개별 실행 (개발용)

### 1. React 앱 빌드

```bash
# 1. React 의존성 설치 및 빌드
cd frontend
npm install
npm run build
cd ..
```

### 2. Django 백엔드 실행 (React 앱 포함)

```bash
# 1. 가상환경 생성 및 활성화 (선택사항)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 2. Django 의존성 설치
cd backend
pip install -r requirements.txt

# 3. 환경변수 설정 (.env 파일 생성)
# .env 파일에 다음 내용 추가:
# SECRET_KEY=your-secret-key
# DEBUG=True
# DB_NAME=postgres
# DB_USER=superuser
# DB_PASSWORD=1111
# DB_HOST=localhost

# 4. 데이터베이스 마이그레이션
python manage.py makemigrations
python manage.py migrate

# 5. Django 정적 파일 수집
python manage.py collectstatic --noinput

# 6. Django 서버 실행
python manage.py runserver
```

## 방법 2: Docker로 실행

```bash
# Docker Desktop 실행 후
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## 접속 방법

### 개별 실행 시
- **메인 웹사이트 (React + Django)**: http://localhost:8000
- **Django 관리자**: http://localhost:8000/admin
- **API 엔드포인트**: http://localhost:8000/api

### Docker 실행 시
- **메인 웹사이트 (React + Django)**: http://localhost:8000
- **Django 관리자**: http://localhost:8000/admin
- **API 엔드포인트**: http://localhost:8000/api

## 주요 특징

- **첫 페이지**: React 로그인 페이지 (`/src/pages/Login.jsx`)
- **API 요청**: `/api/` 경로로 Django 백엔드에 전달
- **통합 서빙**: Django에서 React 앱을 직접 서빙 (포트 8000)
- **개발 환경**: React 빌드 후 Django에서 서빙

## 문제 해결

### 포트 충돌 문제

```bash
# Windows에서 포트 사용 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# 사용 중인 프로세스 종료
taskkill /PID [프로세스ID] /F
```

### React 앱이 로드되지 않는 경우

1. React 앱이 빌드되었는지 확인:
   ```bash
   cd frontend
   npm run build
   ```

2. Django에서 React 빌드 파일을 찾을 수 있는지 확인:
   ```bash
   ls -la frontend/build/
   ```

3. Django 정적 파일이 수집되었는지 확인:
   ```bash
   cd backend
   python manage.py collectstatic --noinput
   ```

4. 브라우저에서 http://localhost:8000 접속 확인

5. 콘솔 에러 확인 (F12 → Console)

### Django 백엔드 문제

1. Django 서버가 실행 중인지 확인:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. 데이터베이스 연결 확인:
   ```bash
   python manage.py dbshell
   ```

3. 마이그레이션 상태 확인:
   ```bash
   python manage.py showmigrations
   ```

### 데이터베이스 문제

1. PostgreSQL이 실행 중인지 확인
2. 데이터베이스 생성:
   ```sql
   CREATE DATABASE postgres;
   CREATE USER superuser WITH PASSWORD '1111';
   GRANT ALL PRIVILEGES ON DATABASE postgres TO superuser;
   ```

## 개발 팁

1. **React 개발**: 코드 변경 후 `npm run build`로 다시 빌드해야 합니다.
2. **Django 개발**: `python manage.py runserver`로 실행하면 코드 변경 시 자동으로 재시작됩니다.
3. **API 테스트**: Postman이나 브라우저에서 http://localhost:8000/api/ 접속하여 테스트 가능합니다.
4. **빠른 개발**: React 개발 시에는 별도로 `npm start`로 3000번 포트에서 개발하고, 배포 시에만 빌드하여 Django에서 서빙하는 방식을 사용할 수 있습니다.
