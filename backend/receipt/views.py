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
from django.db import transaction
import os
import boto3
from authapp.utils import extract_token_from_header, get_user_from_token
import logging

logger = logging.getLogger(__name__)

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

class ReceiptUploadView(APIView):
    """
    영수증 파일 업로드 API
    - 파일을 S3에 업로드하고 Celery 작업을 시작
    """
    
    def post(self, request):
        try:
            # 인증 확인
            token = extract_token_from_header(request)
            if not token:
                return Response({
                    'success': False,
                    'message': '인증 토큰이 필요합니다.',
                    'error': 'MISSING_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 토큰 검증 및 사용자 정보 조회
            user_data = get_user_from_token(token)
            if not user_data:
                return Response({
                    'success': False,
                    'message': '유효하지 않은 토큰입니다.',
                    'error': 'INVALID_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 파일 확인
            if 'file' not in request.FILES:
                return Response({
                    'success': False,
                    'message': '업로드할 파일이 없습니다.',
                    'error': 'NO_FILE'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            uploaded_file = request.FILES['file']
            
            # 파일 유효성 검사
            if not self._validate_file(uploaded_file):
                return Response({
                    'success': False,
                    'message': '지원하지 않는 파일 형식입니다.',
                    'error': 'INVALID_FILE_TYPE'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 파일 크기 검사 (10MB 제한)
            if uploaded_file.size > 10 * 1024 * 1024:
                return Response({
                    'success': False,
                    'message': '파일 크기는 10MB 이하여야 합니다.',
                    'error': 'FILE_TOO_LARGE'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 고유한 job_id 생성
            job_id = str(uuid.uuid4())
            
            # S3에 파일 업로드
            s3_key = self._upload_to_s3(uploaded_file, job_id)
            
            # 데이터베이스에 작업 정보 저장
            with transaction.atomic():
                job = RecJob.objects.create(
                    job_id=job_id,
                    user_id=user_data[0],  # user_id
                    input_s3_key=s3_key,
                    status=RecJob.Status.PENDING,
                    created_at=timezone.now()
                )
            
            # Celery 작업 시작
            run_rec_job.delay(job_id)
            
            logger.info(f"영수증 업로드 완료: job_id={job_id}, user_id={user_data[0]}")
            
            return Response({
                'success': True,
                'message': '영수증이 성공적으로 업로드되었습니다. 처리 중입니다.',
                'data': {
                    'job_id': job_id,
                    'status': 'pending',
                    'uploaded_at': timezone.now().isoformat(),
                    'file_name': uploaded_file.name,
                    'file_size': uploaded_file.size
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"영수증 업로드 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '업로드 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _validate_file(self, file):
        """파일 유효성 검사"""
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        file_extension = os.path.splitext(file.name)[1].lower()
        return file_extension in allowed_extensions
    
    def _upload_to_s3(self, file, job_id):
        """S3에 파일 업로드"""
        try:
            # S3 클라이언트 생성
            s3 = boto3.client(
                's3',
                region_name=os.getenv('AWS_REGION'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
            
            # S3 키 생성: uploads/{job_id}/{original_filename}
            s3_key = f"uploads/{job_id}/{file.name}"
            
            # 파일을 S3에 업로드
            s3.upload_fileobj(
                file,
                bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'Metadata': {
                        'original_filename': file.name,
                        'job_id': job_id,
                        'uploaded_at': timezone.now().isoformat()
                    }
                }
            )
            
            logger.info(f"S3 업로드 완료: {s3_key}")
            return s3_key
            
        except Exception as e:
            logger.error(f"S3 업로드 오류: {str(e)}")
            raise Exception(f"S3 업로드 실패: {str(e)}")
