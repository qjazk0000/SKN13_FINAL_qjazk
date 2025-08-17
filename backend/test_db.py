#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 연결 테스트 스크립트
"""

import os
import sys
from pathlib import Path

# Django 프로젝트 루트 경로 추가
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv(BASE_DIR.parent / '.env')

def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        import psycopg2
        
        # 환경변수에서 데이터베이스 정보 가져오기
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        
        print("=== 데이터베이스 연결 정보 ===")
        print(f"DB_NAME: {db_name}")
        print(f"DB_USER: {db_user}")
        print(f"DB_HOST: {db_host}")
        print(f"DB_PORT: {db_port}")
        print(f"DB_PASSWORD: {'*' * len(db_password) if db_password else 'None'}")
        print("=============================")
        
        if not all([db_name, db_user, db_password, db_host, db_port]):
            print("❌ 환경변수가 완전하지 않습니다!")
            return False
        
        # PostgreSQL 연결 테스트
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            sslmode='require'
        )
        
        print("✅ PostgreSQL 연결 성공!")
        
        # 커서 생성 및 테스트 쿼리 실행
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL 버전: {version[0]}")
        
        # 테이블 목록 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"📋 테이블 개수: {len(tables)}")
        if tables:
            print("📋 테이블 목록:")
            for table in tables[:10]:  # 처음 10개만 표시
                print(f"  - {table[0]}")
            if len(tables) > 10:
                print(f"  ... 외 {len(tables) - 10}개")
        
        # 사용자 테이블 확인 및 사용자 수 조회
        print("\n=== 사용자 정보 확인 ===")
        
        # user_info 테이블이 있는지 확인
        user_table_exists = any('user_info' in table[0] for table in tables)
        
        if user_table_exists:
            try:
                # 사용자 수 조회
                cursor.execute("SELECT COUNT(*) FROM user_info;")
                user_count = cursor.fetchone()[0]
                print(f"👥 총 사용자 수: {user_count}")
                
                if user_count > 0:
                    # user_info 테이블의 컬럼 구조 확인
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'user_info' 
                        ORDER BY ordinal_position;
                    """)
                    
                    columns = cursor.fetchall()
                    print(f"\n📋 user_info 테이블 구조:")
                    for col in columns:
                        print(f"  - {col[0]}: {col[1]}")
                    
                    # 사용자 목록 조회 (처음 5명만)
                    cursor.execute("SELECT * FROM user_info LIMIT 5;")
                    users = cursor.fetchall()
                    
                    print(f"\n📋 사용자 목록 (최대 5명):")
                    for i, user in enumerate(users):
                        print(f"  - 사용자 {i+1}:")
                        for j, col in enumerate(columns):
                            if j < len(user):
                                print(f"    {col[0]}: {user[j]}")
                        print("    ---")
                        
                else:
                    print("❌ 등록된 사용자가 없습니다!")
                    
            except Exception as e:
                print(f"⚠️ 사용자 정보 조회 중 오류: {e}")
        else:
            print("❌ user_info 테이블을 찾을 수 없습니다!")
            print("📋 사용 가능한 테이블:")
            for table in tables:
                if 'user' in table[0].lower():
                    print(f"  - {table[0]} (사용자 관련 테이블일 수 있음)")
        
        cursor.close()
        conn.close()
        print("\n✅ 데이터베이스 연결 테스트 완료!")
        return True
        
    except ImportError:
        print("❌ psycopg2가 설치되지 않았습니다.")
        print("pip install psycopg2-binary")
        return False
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_database_connection() 