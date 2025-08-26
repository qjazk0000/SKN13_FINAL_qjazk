from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.http import HttpResponse
from authapp.decorators import require_auth
from .serializers import (
    ReceiptUploadSerializer,
    ReceiptSaveSerializer,
    ReceiptDownloadSerializer
)
from .utils import extract_receipt_info
import csv
import io
import uuid
import logging

logger = logging.getLogger(__name__)


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
            logger.error(f"CSV 다운로드 오류: {str(e)}")
            return Response({
                'success': False,
                'message': 'CSV 다운로드 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
