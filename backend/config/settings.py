# config/settings.py
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# logs 폴더 생성
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Upstage api key
UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

# 운영 기본값은 안전하게 False
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# --- ALLOWED_HOSTS 보강 ---
env_allowed = os.getenv('ALLOWED_HOSTS', '')
if env_allowed:
    ALLOWED_HOSTS = [h.strip() for h in env_allowed.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = []
# 필수 도메인 보강
for host in ['api.growing.ai.kr', 'growing.ai.kr', 'www.growing.ai.kr']:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'storages',  # S3 파일 스토리지
    'chatbot',
    'receipt',
    'authapp',
    'qdrant',
    'adminapp',
    # 'django_celery_results',
    # 'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- CORS (prod에서는 비활성, dev에서만 활성) ---
# 개발일 때만 corsheaders 사용
if DEBUG:
    if 'corsheaders' not in INSTALLED_APPS:
        INSTALLED_APPS += ['corsheaders']
    if 'corsheaders.middleware.CorsMiddleware' not in MIDDLEWARE:
        MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE

    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ['authorization', 'content-type', 'x-requested-with', 'accept', 'origin']
    CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
else:
    # 운영에서는 Django가 CORS 헤더를 내보내지 않게 함
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = []
    CORS_ALLOW_CREDENTIALS = False

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', 5432),
        'OPTIONS': {
            'sslmode': os.getenv('DB_SSLMODE', 'disable'),  # 필요 시 'require'
        }
    }
}

# Qdrant Vector Database 설정
QDRANT_HOST = os.getenv('QDRANT_HOST', 'qdrant')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'regulations_final')
QDRANT_VECTOR_SIZE = int(os.getenv('QDRANT_VECTOR_SIZE', 1024))
RAG_TOP_K = int(os.getenv('RAG_TOP_K', 5))

# S3 버킷 설정
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_REGION')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_S3_CUSTOM_DOMAIN = (
    f'{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    if AWS_S3_BUCKET_NAME and AWS_S3_REGION_NAME else None
)
# 추가된 부분  
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', AWS_S3_BUCKET_NAME)

# OpenAI 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Password hashers - Argon2 우선
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]
ARGON2_DEFAULT_MEMORY_COST = 102400  # 100MB
ARGON2_DEFAULT_TIME_COST = 2
ARGON2_DEFAULT_PARALLELISM = 8

# i18n
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = False  # 로컬 시간 직접 사용

# Static files (for django admin pages)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # 운영 전환 시 적절히 조정
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# --- CSRF_TRUSTED_ORIGINS 보강 (https 스킴 누락 방지) ---
CSRF_TRUSTED_ORIGINS = [
    'https://growing.ai.kr',
    'https://www.growing.ai.kr',
    'https://api.growing.ai.kr',
    'https://skn13-final-6team.vercel.app',
]

# 로깅 (중복 제거하여 한 번만 정의)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {'format': '{levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django.log',
            'formatter': 'verbose',
            'mode': 'a',
            'encoding': 'utf-8',
        },
    },
    'root': {'handlers': ['console', 'file'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
        'chatbot.services': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': False},
        'chatbot.views': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': False},
        'adminapp': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': False},
    },
}

# 프록시/HTTPS 인지 (ALB 뒤)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 리다이렉트는 ALB에서 처리
SECURE_SSL_REDIRECT = False

# 운영 시 권장(HTTPS 쿠키)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
