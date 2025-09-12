FROM python:3.10-slim

# 캐시 관리를 위해 패키지 설치와 pip 설치를 분리
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*
    
WORKDIR /app

# 시스템 패키지 업데이트 및 정리
RUN apt-get update && apt-get clean && rm -rf /var/lib/apt/lists/*

# pip 캐시 정리 및 최적화
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

COPY . /app

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload"]
