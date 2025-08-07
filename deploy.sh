#!/bin/bash

echo "🚀 개발 환경을 시작합니다..."

# Docker 컨테이너 실행
echo "🐳 Docker 컨테이너를 실행합니다..."
docker-compose down
docker-compose up -d

echo "✅ 개발 환경이 시작되었습니다!"
echo "🌐 React 앱: http://localhost:3000"
echo "🔧 Django 백엔드: http://localhost:8000"
echo "📊 관리자 페이지: http://localhost:8000/admin"
echo ""
echo "📝 로그 확인: docker-compose logs -f"

