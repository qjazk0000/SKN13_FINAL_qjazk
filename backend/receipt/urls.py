# receipt/urls.py

from django.urls import path
from .views import CreateJobView, CommitJobView, JobDetailView, JobListView, TestUploadView, ReceiptUploadView

urlpatterns = [
    # 테스트용 업로드 (권한 없이 접근 가능)
    path('test-upload/', TestUploadView.as_view(), name='test-upload'),
    
    # 영수증 업로드 (로그인 필요)
    path('upload/', ReceiptUploadView.as_view(), name='receipt-upload'),
    
    # Job 생성 및 S3 업로드 URL 획득
    path('jobs/', CreateJobView.as_view(), name='create-job'),
    
    # Job 목록 조회
    path('jobs/list/', JobListView.as_view(), name='job-list'),
    
    # Job 상태 조회 및 결과 다운로드
    path('jobs/<uuid:job_id>/', JobDetailView.as_view(), name='job-detail'),
    
    # 업로드 완료 후 작업 시작
    path('jobs/<uuid:job_id>/commit/', CommitJobView.as_view(), name='commit-job'),
]
