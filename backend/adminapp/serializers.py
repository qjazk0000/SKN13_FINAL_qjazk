# adminapp/serializers.py
from rest_framework import serializers
from .models import ReportedConversation, Receipt

class UserSearchSerializer(serializers.Serializer):
    """
    회원 검색 요청 데이터 검증 시리얼라이저
    - FFU-21: 검색구분 selectbox [전체, 부서, 이름, ID, 직급, 이메일]
    - FFU-22: 검색입력 필드
    """
    search_type = serializers.ChoiceField(
        choices=['all', 'dept', 'name', 'id', 'rank', 'email'],
        default='all',
        help_text="검색 유형: 전체, 부서, 이름, ID, 직급, 이메일 중 선택"
    )
    search_keyword = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="검색할 키워드 입력"
    )

class ConversationSearchSerializer(serializers.Serializer):
    """
    대화 신고 내역 검색 요청 데이터 검증 시리얼라이저
    - FFU-23: 기간선택 selectbox [전체, 오늘, 일주일, 직접입력]
    - FFU-24: 기간입력필드 (직접입력 시 사용)
    - FFU-25: 검색구분 selectbox [채팅ID, 사용자ID, 세션ID]
    - FFU-26: 검색입력필드
    """
    period = serializers.ChoiceField(
        choices=['all', 'today', 'week', 'custom'],
        default='all',
        help_text="검색 기간: 전체, 오늘, 일주일, 직접입력 중 선택"
    )
    start_date = serializers.DateField(
        required=False,
        help_text="시작일 (직접입력 시 필수)"
    )
    end_date = serializers.DateField(
        required=False,
        help_text="종료일 (직접입력 시 필수)"
    )
    search_type = serializers.ChoiceField(
        choices=['chat_id', 'user_id', 'session_id'],
        default='chat_id',
        help_text="검색 유형: 채팅ID, 사용자ID, 세션ID 중 선택"
    )
    search_keyword = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="검색할 키워드 입력"
    )

class ReportedConversationSerializer(serializers.ModelSerializer):
    """
    신고된 대화 내역 응답 데이터 시리얼라이저
    - FFC-11: 대화목록 출력
    - ReportedConversation 모델의 모든 필드를 JSON으로 변환
    """
    class Meta:
        model = ReportedConversation
        fields = '__all__'  # 모든 모델 필드 포함
        read_only_fields = ['report_id', 'created_at']  # 자동 생성 필드는 읽기 전용

class ReceiptSerializer(serializers.ModelSerializer):
    """
    영수증 목록 응답 데이터 시리얼라이저
    - FFC-13: 영수증 이미지 목록 출력
    - 목록 조회 시 필요한 기본 정보 포함
    """
    # 프론트엔드가 요구하는 필드들 - 실제 DB 테이블 구조에 맞춤
    name = serializers.CharField(read_only=True)
    dept = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)
    file_path = serializers.CharField(read_only=True)
    receipt_id = serializers.UUIDField(read_only=True)
    user_login_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Receipt
        fields = [
            'receipt_id',    # 영수증 고유 ID
            'name',          # 사용자 이름
            'dept',          # 사용자 부서
            'created_at',    # 생성일
            'amount',        # 금액
            'status',        # 상태
            'file_path',     # 파일 경로
            'user_login_id'  # 사용자 로그인 ID
        ]
        read_only_fields = fields  # 모든 필드 읽기 전용

class ReceiptDetailSerializer(serializers.ModelSerializer):
    """
    영수증 상세 정보 응답 데이터 시리얼라이저
    - FFC-12: 영수증 이미지 출력 (미리보기)
    - FFC-13: 추출텍스트 목록 출력
    """
    image_url = serializers.SerializerMethodField(
        help_text="영수증 이미지 URL (미리보기용)"
    )
    user_name = serializers.CharField(read_only=True)
    user_dept = serializers.CharField(read_only=True)
    file_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Receipt
        fields = [
            'receipt_id',        # 영수증 고유 ID
            'user_id',           # 사용자 ID
            'user_name',         # 사용자 이름
            'user_dept',         # 사용자 부서
            'image_url',         # 이미지 URL (FFC-12)
            'file_name',         # 파일명
            'payment_date',      # 결제일
            'amount',            # 금액
            'currency',          # 통화
            'store_name',        # 상점명
            'extracted_text',    # 추출된 텍스트 (FFC-13)
            'status',            # 상태
            'created_at'         # 생성일
        ]
    
    def get_image_url(self, obj):
        """파일 경로를 기반으로 이미지 URL 생성"""
        # 실제 DB에서 file_path를 직접 가져오므로 source 제거
        return getattr(obj, 'file_path', None)