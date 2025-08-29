# Upload API 인증 이슈 해결 가이드

## 개요
현재 receipt 업로드 API에서 발생하는 인증 및 권한 문제를 해결하기 위한 가이드입니다.

## 문제 상황
- 사용자 업로드 기능 구현 중 인증 문제 발생
- JWT 토큰 기반 인증이 필요한 상황
- 테스트용 API와 운영용 API의 권한 설정 차이

## 해결 방법

### 1. 환경변수 설정
#### 필요한 환경변수:
```bash
export AWS_S3_BUCKET=skn.dopamine-navi.bucket
export AWS_S3_BUCKET_NAME=skn.dopamine-navi.bucket
export AWS_REGION=ap-northeast-2
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

### 2. JWT 인증 구현
- JWT 토큰을 사용한 사용자 인증
- API 호출 시 Authorization 헤더에 토큰 포함
- 토큰 만료 시 자동 갱신

### 3. 권한 설정
- 모든 뷰에 `IsAuthenticated` 권한 적용
- 테스트용 뷰는 개발 환경에서만 사용
- 운영 환경에서는 보안 강화

## 사용 예시
```python
# JWT 토큰으로 API 호출
headers = {
    'Authorization': f'Bearer {jwt_token}',
    'Content-Type': 'application/json'
}

response = requests.post('/api/receipt/jobs/', 
                        json=data, 
                        headers=headers)
```

## 주의사항
- AWS 키는 절대 코드에 하드코딩하지 말 것
- 환경변수 파일(.env)은 Git에 추가하지 말 것
- 운영 환경에서는 모든 API에 인증 적용
