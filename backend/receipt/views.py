# receipt/views.py

import uuid
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import RecJob, RecResultSummary
from .services.s3_client import presign_upload, presign_download
from .tasks import run_rec_job

class TestUploadView(AllowAny, APIView):
    """
    테스트용 업로드 뷰 (권한 없이 접근 가능)
    """
    def post(self, request):
        try:
            # 파일 업로드를 위한 presigned URL 생성
            filename = request.data.get('filename')
            content_type = request.data.get('content_type')
            
            if not filename or not content_type:
                return Response(
                    {'error': 'filename과 content_type이 필요합니다.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # S3 업로드용 presigned URL 생성 (올바른 S3 키 사용)
            s3_key = f"uploads/test/{filename}"
            upload_url = presign_upload(s3_key, content_type)
            
            return Response({
                'upload_url': upload_url,
                's3_key': s3_key,
                'filename': filename,
                'content_type': content_type
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CreateJobView(APIView):
    """
    영수증 처리 작업 생성 뷰
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user_id = request.user.id
            filename = request.data.get('filename')
            content_type = request.data.get('content_type')
            
            if not filename or not content_type:
                return Response(
                    {'error': 'filename과 content_type이 필요합니다.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 작업 ID 생성
            job_id = uuid.uuid4()
            
            # S3 키 생성
            input_s3_key = f"uploads/receipts/{job_id}/{filename}"
            
            # RecJob 모델에 작업 정보 저장
            job = RecJob.objects.create(
                job_id=job_id,
                user_id=user_id,  # UUID 값 직접 전달
                input_s3_key=input_s3_key,
                original_filename=filename
            )
            
            # S3 업로드용 presigned URL 생성
            upload_url = presign_upload(input_s3_key, content_type)
            
            return Response({
                'job_id': str(job_id),
                'upload_url': upload_url,
                's3_key': input_s3_key,
                'status': job.status
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommitJobView(APIView):
    """
    업로드 완료 후 작업 시작 뷰
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            job_id = request.data.get('job_id')
            
            if not job_id:
                return Response(
                    {'error': 'job_id가 필요합니다.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                job = RecJob.objects.get(job_id=job_id)
            except RecJob.DoesNotExist:
                return Response(
                    {'error': '작업을 찾을 수 없습니다.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 작업 상태를 QUEUED로 변경하고 queued_at 설정
            job.status = RecJob.Status.QUEUED
            job.queued_at = timezone.now()
            job.save(update_fields=["status", "queued_at", "updated_at"])
            
            # Celery 작업 실행
            run_rec_job.delay(str(job_id))
            
            return Response({
                'job_id': str(job_id),
                'status': job.status,
                'queued_at': job.queued_at,
                'message': '작업이 큐에 추가되었습니다.'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class JobDetailView(APIView):
    """
    작업 상세 정보 조회 뷰
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id):
        try:
            job = RecJob.objects.get(job_id=job_id)
            
            # 결과가 있으면 다운로드 URL도 제공
            download_url = None
            if job.result_s3_key:
                download_url = presign_download(job.result_s3_key)
            
            return Response({
                'job_id': str(job.job_id),
                'status': job.status,
                'original_filename': job.original_filename,
                'created_at': job.created_at,
                'updated_at': job.updated_at,
                'queued_at': job.queued_at,
                'started_at': job.started_at,
                'processed_at': job.processed_at,
                'download_url': download_url,
                'error_message': job.error_message
            })
            
        except RecJob.DoesNotExist:
            return Response(
                {'error': '작업을 찾을 수 없습니다.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class JobListView(APIView):
    """
    사용자의 작업 목록 조회 뷰
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user_id = request.user.id
            jobs = RecJob.objects.filter(user_id=user_id).order_by('-created_at')
            
            job_list = []
            for job in jobs:
                job_data = {
                    'job_id': str(job.job_id),
                    'status': job.status,
                    'original_filename': job.original_filename,
                    'created_at': job.created_at,
                    'updated_at': job.updated_at,
                    'queued_at': job.queued_at,
                    'started_at': job.started_at,
                    'processed_at': job.processed_at
                }
                
                # 결과가 있으면 다운로드 URL도 제공
                if job.result_s3_key:
                    job_data['download_url'] = presign_download(job.result_s3_key)
                
                job_list.append(job_data)
            
            return Response({
                'jobs': job_list,
                'total_count': len(job_list)
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
