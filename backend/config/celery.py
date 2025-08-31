import os
from celery import Celery
from django.conf import settings

# Django 설정 모듈 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Celery 앱 생성
app = Celery('config')

# Django 설정에서 Celery 설정 가져오기
app.config_from_object('django.conf:settings', namespace='CELERY')

# 자동으로 tasks.py 파일들을 발견
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery 설정
app.conf.update(
    # Redis를 broker로 사용
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    
    # Redis를 result backend로 사용
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    
    # 작업 결과 저장 설정
    result_expires=3600,  # 1시간 후 결과 만료
    
    # 작업 시리얼라이저 설정
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # 시간대 설정
    timezone='Asia/Seoul',
    enable_utc=False,
    
    # 작업 실행 설정
    task_always_eager=False,  # 개발 환경에서는 False, 테스트에서는 True
    
    # 작업 큐 설정
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    
    # Worker 설정
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # 재시도 설정
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # 모니터링 설정
    worker_send_task_events=True,
    task_send_sent_event=True,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
