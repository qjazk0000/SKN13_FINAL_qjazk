# receipt/views.py

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import FileInfo, ReceiptInfo
from .serializers import FileInfoSerializer, ReceiptInfoSerializer

class FileUploadView(generics.CreateAPIView):
    serializer_class = FileInfoSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        f = request.FILES.get('file')
        if not f:
            return Response({"error": "파일이 필요합니다."}, status=400)

        file_obj = FileInfo.objects.create(
            file_origin_name=f.name,
            file=f,
            file_size=f.size,
            file_ext=f.name.split('.')[-1].lower()
        )
        ReceiptInfo.objects.create(file=file_obj, user=request.user, status='pending')

        # TODO: Celery OCR 태스크 실행 (tasks.py 구현 후 활성화)
        # process_receipt_file.delay(str(file_obj.file_id))

        return Response(FileInfoSerializer(file_obj).data, status=status.HTTP_201_CREATED)

class ReceiptListView(generics.ListAPIView):
    serializer_class = ReceiptInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReceiptInfo.objects.filter(user=self.request.user).order_by('-created_at')

class ReceiptDetailView(generics.RetrieveAPIView):
    serializer_class = ReceiptInfoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'receipt_id'

    def get_queryset(self):
        return ReceiptInfo.objects.filter(user=self.request.user)
