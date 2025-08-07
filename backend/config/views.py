import os
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

# Serve React App
index = never_cache(TemplateView.as_view(template_name='index.html'))

def serve_react(request, path=''):
    """React 앱의 모든 라우트를 처리하는 뷰"""
    try:
        # React build 디렉토리에서 index.html 파일을 찾습니다
        react_build_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'build', 'index.html')
        print(f"React build path: {react_build_path}")  # 디버깅용 출력
        
        if os.path.exists(react_build_path):
            with open(react_build_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HttpResponse(content, content_type='text/html')
        else:
            # React 빌드 파일이 없는 경우 기본 메시지 반환
            return HttpResponse("React 앱이 빌드되지 않았습니다. 'npm run build'를 실행해주세요.", status=404)
    except Exception as e:
        return HttpResponse(f"오류가 발생했습니다: {str(e)}", status=500)

