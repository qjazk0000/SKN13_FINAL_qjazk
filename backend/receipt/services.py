import os
import uuid
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class S3ReceiptService:
    """영수증 파일을 S3에 업로드하는 서비스"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    def generate_s3_key(self, file_name, folder_prefix='receipts'):
        """
        S3에 저장될 키(경로) 생성
        
        Args:
            file_name (str): 원본 파일명
            folder_prefix (str): 폴더 접두사
            
        Returns:
            str: S3 키
        """
        # 파일 확장자 추출
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # 고유한 파일명 생성 (UUID + 타임스탬프)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        # S3 키 생성: folder_prefix/YYYYMMDD_HHMMSS_uuid.ext
        s3_key = f"{folder_prefix}/{timestamp}_{unique_id}{file_ext}"
        
        return s3_key
    
    def upload_receipt_file(self, file_obj, user_id):
        """
        영수증 파일을 S3에 업로드
        
        Args:
            file_obj: 업로드된 파일 객체
            user_id: 사용자 ID
            
        Returns:
            dict: 업로드 결과 정보
        """
        try:
            # 원본 파일명
            original_name = file_obj.name if hasattr(file_obj, 'name') else 'unknown'
            
            # S3 키 생성 (사용자별 폴더)
            s3_key = self.generate_s3_key(original_name, f'receipts/user_{user_id}')
            
            # MIME 타입 자동 감지
            content_type = getattr(file_obj, 'content_type', None)
            
            # S3에 업로드
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # 파일 URL 생성
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
            
            logger.info(f"영수증 파일 S3 업로드 성공: {s3_key}")
            
            return {
                'success': True,
                's3_key': s3_key,
                'file_url': file_url,
                'original_name': original_name,
                'content_type': content_type,
                'file_size': file_obj.size if hasattr(file_obj, 'size') else 0
            }
            
        except ClientError as e:
            logger.error(f"S3 업로드 실패: {e}")
            return {
                'success': False,
                'error': f'S3 업로드 실패: {str(e)}'
            }
        except Exception as e:
            logger.error(f"파일 업로드 중 오류 발생: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_receipt_file(self, s3_key):
        """
        S3에서 영수증 파일 삭제
        
        Args:
            s3_key (str): 삭제할 S3 키
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"영수증 파일 S3 삭제 성공: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 삭제 실패: {e}")
            return False
        except Exception as e:
            logger.error(f"파일 삭제 중 오류: {e}")
            return False
    
    def get_file_presigned_url(self, s3_key, operation='get_object', expires_in=3600):
        """
        영수증 파일의 Presigned URL 생성
        
        Args:
            s3_key (str): S3 키
            operation (str): 작업 타입 ('get_object', 'put_object')
            expires_in (int): 만료 시간(초)
            
        Returns:
            str: Presigned URL 또는 None
        """
        try:
            url = self.s3_client.generate_presigned_url(
                operation,
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            
            logger.info(f"Presigned URL 생성 성공: {s3_key}")
            return url
            
        except ClientError as e:
            logger.error(f"Presigned URL 생성 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"Presigned URL 생성 중 오류: {e}")
            return None
    
    def check_file_exists(self, s3_key):
        """
        S3에 파일이 존재하는지 확인
        
        Args:
            s3_key (str): 확인할 S3 키
            
        Returns:
            bool: 파일 존재 여부
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"파일 존재 확인 실패: {e}")
                return False
        except Exception as e:
            logger.error(f"파일 존재 확인 중 오류: {e}")
            return False

# 전역 S3 서비스 인스턴스
s3_receipt_service = S3ReceiptService()
