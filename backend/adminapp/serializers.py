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
    class Meta:
        model = Receipt
        fields = [
            'receipt_id',    # 영수증 고유 ID
            'user_id',       # 사용자 ID
            'file_name',     # 파일명 (FFC-13: 파일제목)
            'uploaded_at',   # 업로드 일시
            'is_verified'    # 검증 상태
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
    
    class Meta:
        model = Receipt
        fields = [
            'receipt_id',        # 영수증 고유 ID
            'user_id',           # 사용자 ID
            'image_url',         # 이미지 URL (FFC-12)
            'extracted_text',    # 추출된 텍스트 (FFC-13)
            'uploaded_at'        # 업로드 일시
        ]
        read_only_fields = fields  # 모든 필드 읽기 전용

    def get_image_url(self, obj):
        """
        영수증 이미지 URL 생성 메서드
        - file_path를 기반으로 미디어 URL 생성
        - FFC-12: 이미지 미리보기 기능 지원
        """
        if obj.file_path:
            return f"/media/receipts/{obj.file_path}"
        return None