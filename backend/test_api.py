#!/usr/bin/env python
"""
로그인 API 테스트 스크립트
"""
import os
import sys
import django
import requests
import json

# Django 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_login_api():
    """로그인 API 테스트"""
    print("🔐 로그인 API 테스트 시작\n")
    
    # 실제 등록된 사용자 정보로 테스트
    test_user = {
        'user_login_id': 'waitingpark',  # 실제 등록된 사용자 ID
        'passwd': 'test1234!'            # 실제 등록된 비밀번호
    }
    
    print(f"📝 테스트 데이터: {test_user}")
    
    try:
        # Django 서버가 실행 중인지 확인
        response = requests.get('http://localhost:8000/api/auth/login/', timeout=5)
        print("✅ Django 서버가 실행 중입니다.")
    except requests.exceptions.ConnectionError:
        print("❌ Django 서버에 연결할 수 없습니다.")
        print("   Django 서버를 먼저 실행해주세요: python manage.py runserver")
        return
    except Exception as e:
        print(f"❌ 서버 연결 오류: {e}")
        return
    
    # POST 요청으로 로그인 테스트
    try:
        print("\n📤 로그인 요청 전송 중...")
        response = requests.post(
            'http://localhost:8000/api/auth/login/',
            json=test_user,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 응답 상태 코드: {response.status_code}")
        print(f"📥 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 로그인 성공!")
            data = response.json()
            print(f"📋 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # JWT 토큰 확인
            if 'data' in data and 'access_token' in data['data']:
                print("🎫 JWT 토큰이 정상적으로 생성되었습니다.")
                
                # 토큰을 사용해서 사용자 프로필 조회 테스트
                print("\n🔍 사용자 프로필 조회 테스트...")
                access_token = data['data']['access_token']
                headers = {'Authorization': f'Bearer {access_token}'}
                
                profile_response = requests.get(
                    'http://localhost:8000/api/auth/profile/',
                    headers=headers,
                    timeout=10
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("✅ 프로필 조회 성공!")
                    print(f"📋 프로필 데이터: {json.dumps(profile_data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ 프로필 조회 실패: {profile_response.status_code}")
                    print(f"📋 오류 내용: {profile_response.text}")
            else:
                print("⚠️  JWT 토큰이 생성되지 않았습니다.")
                
        elif response.status_code == 400:
            print("❌ 로그인 실패 (400 Bad Request)")
            try:
                error_data = response.json()
                print(f"📋 오류 내용: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📋 오류 내용: {response.text}")
                
        elif response.status_code == 500:
            print("❌ 서버 내부 오류 (500 Internal Server Error)")
            print(f"📋 오류 내용: {response.text}")
            
        else:
            print(f"❌ 예상치 못한 응답: {response.status_code}")
            print(f"📋 응답 내용: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 오류: {e}")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")

def test_with_real_user():
    """실제 사용자로 로그인 테스트"""
    print("\n🔍 실제 사용자 정보 확인")
    
    # Django ORM을 사용해서 실제 사용자 정보 가져오기
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_login_id, name, dept, rank, email, auth, use_yn
                FROM user_info 
                WHERE use_yn = 'Y' AND auth = 'Y'
                LIMIT 3
            """)
            
            users = cursor.fetchall()
            
            if users:
                print("📊 사용 가능한 사용자 목록:")
                for i, user in enumerate(users, 1):
                    print(f"  {i}. ID: {user[0]}, 이름: {user[1]}, 부서: {user[2]}, 직급: {user[3]}")
                
                # waitingpark 사용자 정보 확인
                print(f"\n🔍 waitingpark 사용자 상세 정보:")
                cursor.execute("""
                    SELECT user_login_id, name, dept, rank, email, auth, use_yn, created_dt
                    FROM user_info 
                    WHERE user_login_id = 'waitingpark'
                """)
                
                waitingpark_user = cursor.fetchone()
                if waitingpark_user:
                    print(f"  - 사용자 ID: {waitingpark_user[0]}")
                    print(f"  - 이름: {waitingpark_user[1]}")
                    print(f"  - 부서: {waitingpark_user[2]}")
                    print(f"  - 직급: {waitingpark_user[3]}")
                    print(f"  - 이메일: {waitingpark_user[4]}")
                    print(f"  - 인증상태: {waitingpark_user[5]}")
                    print(f"  - 사용상태: {waitingpark_user[6]}")
                    print(f"  - 생성일: {waitingpark_user[7]}")
                else:
                    print("❌ waitingpark 사용자를 찾을 수 없습니다.")
                
            else:
                print("❌ 사용 가능한 사용자가 없습니다.")
                
    except Exception as e:
        print(f"❌ 사용자 정보 조회 실패: {e}")

def main():
    """메인 함수"""
    print("🚀 로그인 API 테스트 시작\n")
    
    # 1. 로그인 API 테스트
    test_login_api()
    
    # 2. 실제 사용자 정보 확인
    test_with_real_user()
    
    print("\n✅ 모든 테스트가 완료되었습니다.")

if __name__ == "__main__":
    main() 