import boto3
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 AWS 설정 가져오기
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "skn.dopamine-navi.bucket")
AWS_S3_REGION_NAME = os.getenv("AWS_REGION", "ap-northeast-2")

# AWS 키가 설정되어 있는지 확인
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    print("AWS 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    exit(1)

s3_client = boto3.client('s3', 
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        region_name=AWS_S3_REGION_NAME)

response = s3_client.list_buckets()

print(response)
