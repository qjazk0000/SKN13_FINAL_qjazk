# backend/Dockerfile
FROM python:3.10-slim

# 운영 기본 런타임
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 필요한 시스템 패키지 최소 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 먼저 설치(캐시 최적화)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip cache purge

# (선택) GPU 안 쓰면 torch를 CPU 휠로 대체해 용량↓
# RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 앱 코드만 복사 (대용량은 .dockerignore로 제외)
COPY config/ /app/config/
COPY chatbot/ /app/chatbot/
COPY receipt/ /app/receipt/
COPY authapp/ /app/authapp/
COPY adminapp/ /app/adminapp/
COPY manage.py /app/

EXPOSE 8000

# 운영: 서버만 실행 (requirements에 gunicorn이 없다 했으므로 uvicorn 단독)
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

# (개발용) 자동 리로드가 필요하면 compose/dev에서만 아래로 덮어쓰기
# CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]
