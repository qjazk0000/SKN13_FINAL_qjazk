# adminapp/serializers.py
from rest_framework import serializers
from .models import ReportedConversation
import logging

logger = logging.getLogger(__name__)

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

    def validate(self, attrs):
        """
        사용자 정의 유효성 검사
        - 직접입력(period='custom') 선택 시 시작일과 종료일 필수 확인
        """
        period = attrs.get('period')
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if period == 'custom':
            if not start_date:
                raise serializers.ValidationError({
                    'start_date': '직접입력 시 시작일은 필수입니다.'
                })
            if not end_date:
                raise serializers.ValidationError({
                    'end_date': '직접입력 시 종료일은 필수입니다.'
                })
            if start_date > end_date:
                raise serializers.ValidationError({
                    'start_date': '시작일은 종료일보다 클 수 없습니다.'
                })
        
        return attrs

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

class AdminReceiptSerializer(serializers.Serializer):
    """
    관리자용 영수증 목록 응답 시리얼라이저 (Raw SQL 결과용)
    - FFC-13: 영수증 이미지 목록 출력
    """
    receipt_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    name = serializers.CharField(allow_null=True)  # 사용자 이름
    dept = serializers.CharField(allow_null=True)  # 사용자 부서
    file_name = serializers.CharField(source='file_origin_name')  # file_info 테이블의 file_origin_name
    file_path = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    status = serializers.CharField()
    store_name = serializers.CharField(allow_null=True)
    payment_date = serializers.DateTimeField(allow_null=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    extracted_text = serializers.CharField(allow_null=True)
    items_info = serializers.ListField(child=serializers.CharField(), allow_empty=True)

class AdminReceiptDetailSerializer(serializers.Serializer):
    """
    관리자용 영수증 상세 정보 응답 시리얼라이저 (Raw SQL 결과용)
    - FFC-12: 영수증 이미지 출력 (미리보기)
    - FFC-13: 추출텍스트 목록 출력
    """
    # Raw SQL JOIN 결과에서 가져오는 필드들
    receipt_id = serializers.UUIDField(help_text="영수증 고유 ID")
    user_id = serializers.UUIDField(help_text="사용자 ID")
    user_name = serializers.CharField(help_text="사용자 이름")
    user_dept = serializers.CharField(help_text="사용자 부서")
    file_path = serializers.CharField(help_text="파일 경로 (이미지 URL)")
    file_name = serializers.CharField(help_text="파일명")
    payment_date = serializers.DateTimeField(help_text="결제일")
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, help_text="금액")
    currency = serializers.CharField(help_text="통화")
    store_name = serializers.CharField(help_text="상점명")
    extracted_text = serializers.CharField(help_text="추출된 텍스트")
    status = serializers.CharField(help_text="상태")
    created_at = serializers.DateTimeField(help_text="생성일")


class ReceiptPreviewSerializer(serializers.Serializer):
    """
    영수증 미리보기용 시리얼라이저 (Raw SQL 결과용)
    """
    receipt_id = serializers.UUIDField(help_text="영수증 고유 ID")
    user_name = serializers.CharField(help_text="사용자 이름")
    user_dept = serializers.CharField(help_text="사용자 부서")
    file_path = serializers.CharField(help_text="파일 경로")
    file_name = serializers.CharField(help_text="파일명")
    payment_date = serializers.DateTimeField(help_text="결제일")
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, help_text="금액")
    currency = serializers.CharField(help_text="통화")
    store_name = serializers.CharField(help_text="상점명")
    extracted_text = serializers.CharField(help_text="추출된 텍스트")
    status = serializers.CharField(help_text="상태")
    created_at = serializers.DateTimeField(help_text="생성일")