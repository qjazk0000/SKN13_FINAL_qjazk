#!/usr/bin/env python3
"""
서식 PDF 파일들을 S3의 company_policy 디렉토리에 업로드하는 스크립트
"""

import os
import sys
import django
from pathlib import Path
import logging
from datetime import datetime

# Django 설정
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class S3FormUploadService:
    """서식 PDF 파일들을 S3에 업로드하는 서비스"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.folder_prefix = 'company_policy'
    
    def upload_form_file(self, file_path, s3_key):
        """
        개별 서식 파일을 S3에 업로드
        
        Args:
            file_path (str): 로컬 파일 경로
            s3_key (str): S3에 저장될 키
            
        Returns:
            dict: 업로드 결과
        """
        try:
            # 파일 크기 확인
            file_size = os.path.getsize(file_path)
            
            # MIME 타입 설정
            content_type = 'application/pdf'
            
            # S3에 업로드
            with open(file_path, 'rb') as file_obj:
                self.s3_client.upload_fileobj(
                    file_obj,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'Metadata': {
                            'upload_date': datetime.now().isoformat(),
                            'file_size': str(file_size)
                        }
                    }
                )
            
            # 파일 URL 생성
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
            
            logger.info(f"서식 파일 S3 업로드 성공: {s3_key}")
            
            return {
                'success': True,
                's3_key': s3_key,
                'file_url': file_url,
                'file_size': file_size,
                'original_name': os.path.basename(file_path)
            }
            
        except ClientError as e:
            logger.error(f"S3 업로드 실패 ({file_path}): {e}")
            return {
                'success': False,
                'error': f'S3 업로드 실패: {str(e)}'
            }
        except Exception as e:
            logger.error(f"파일 업로드 중 오류 발생 ({file_path}): {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_s3_key(self, file_name):
        """
        S3에 저장될 키(경로) 생성
        
        Args:
            file_name (str): 원본 파일명
            
        Returns:
            str: S3 키
        """
        # 파일명에서 특수문자 제거 및 정리
        clean_name = file_name.replace(' ', '_').replace('(', '').replace(')', '')
        
        # S3 키 생성: company_policy/파일명.pdf
        s3_key = f"{self.folder_prefix}/{clean_name}"
        
        return s3_key
    
    def upload_all_forms(self, forms_dir):
        """
        forms_extracted_v6 디렉토리의 모든 PDF 파일을 S3에 업로드
        
        Args:
            forms_dir (str): 서식 파일들이 있는 디렉토리 경로
            
        Returns:
            dict: 업로드 결과 요약
        """
        forms_path = Path(forms_dir)
        
        if not forms_path.exists():
            logger.error(f"서식 디렉토리가 존재하지 않습니다: {forms_dir}")
            return {
                'success': False,
                'error': f'디렉토리가 존재하지 않습니다: {forms_dir}'
            }
        
        # PDF 파일 목록 가져오기
        pdf_files = list(forms_path.glob('*.pdf'))
        
        if not pdf_files:
            logger.warning(f"PDF 파일을 찾을 수 없습니다: {forms_dir}")
            return {
                'success': False,
                'error': 'PDF 파일을 찾을 수 없습니다'
            }
        
        logger.info(f"총 {len(pdf_files)}개의 PDF 파일을 업로드합니다.")
        
        # 업로드 결과 저장
        results = {
            'total_files': len(pdf_files),
            'success_count': 0,
            'failed_count': 0,
            'success_files': [],
            'failed_files': [],
            'upload_details': []
        }
        
        # 각 파일 업로드
        for pdf_file in pdf_files:
            file_name = pdf_file.name
            s3_key = self.generate_s3_key(file_name)
            
            logger.info(f"업로드 중: {file_name}")
            
            upload_result = self.upload_form_file(str(pdf_file), s3_key)
            
            if upload_result['success']:
                results['success_count'] += 1
                results['success_files'].append(file_name)
                logger.info(f"✓ 성공: {file_name}")
            else:
                results['failed_count'] += 1
                results['failed_files'].append({
                    'file_name': file_name,
                    'error': upload_result['error']
                })
                logger.error(f"✗ 실패: {file_name} - {upload_result['error']}")
            
            results['upload_details'].append({
                'file_name': file_name,
                's3_key': s3_key,
                'success': upload_result['success'],
                'file_url': upload_result.get('file_url', ''),
                'error': upload_result.get('error', '')
            })
        
        # 결과 요약 출력
        logger.info("=" * 60)
        logger.info("업로드 완료 요약")
        logger.info("=" * 60)
        logger.info(f"총 파일 수: {results['total_files']}")
        logger.info(f"성공: {results['success_count']}")
        logger.info(f"실패: {results['failed_count']}")
        
        if results['failed_files']:
            logger.info("\n실패한 파일들:")
            for failed_file in results['failed_files']:
                logger.error(f"  - {failed_file['file_name']}: {failed_file['error']}")
        
        return results

def main():
    """메인 실행 함수"""
    try:
        # 서비스 인스턴스 생성
        upload_service = S3FormUploadService()
        
        # 서식 파일 디렉토리 경로
        forms_dir = "/app/documents/kisa_pdf/forms_extracted_v6"
        
        logger.info("서식 PDF 파일 S3 업로드를 시작합니다.")
        logger.info(f"업로드 대상 디렉토리: {forms_dir}")
        logger.info(f"S3 버킷: {upload_service.bucket_name}")
        logger.info(f"S3 폴더: {upload_service.folder_prefix}")
        
        # 모든 서식 파일 업로드
        results = upload_service.upload_all_forms(forms_dir)
        
        if results['success'] or results['success_count'] > 0:
            logger.info(f"\n업로드 완료! 성공: {results['success_count']}, 실패: {results['failed_count']}")
            
            # 성공한 파일들의 S3 URL 출력
            if results['success_files']:
                logger.info("\n업로드된 파일들의 S3 URL:")
                for detail in results['upload_details']:
                    if detail['success']:
                        logger.info(f"  {detail['file_name']}")
                        logger.info(f"    S3 Key: {detail['s3_key']}")
                        logger.info(f"    URL: {detail['file_url']}")
                        logger.info("")
        else:
            logger.error("업로드 실패!")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"스크립트 실행 중 오류 발생: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
