from celery import shared_task
import os, io, csv, boto3, uuid, json, logging
from django.utils import timezone
from .models import RecJob, RecResultSummary, RecResultItem
from .services.model_client import infer_image_bytes

# 로깅 설정
logger = logging.getLogger(__name__)

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
BUCKET = os.getenv("AWS_S3_BUCKET_NAME")  # 환경변수 통일

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def run_rec_job(self, job_id: str):
    logger.info(f"Starting receipt processing job: {job_id}")
    
    try:
        job = RecJob.objects.get(job_id=job_id)  # pk 대신 job_id 사용
        
        # 상태 업데이트
        from django.db import transaction
        with transaction.atomic():
            job.status = RecJob.Status.RUNNING
            job.started_at = timezone.now()
            job.save(update_fields=["status","started_at","updated_at"])

        logger.info(f"Job {job_id} status updated to RUNNING")

        # 1) S3에서 이미지 로드
        logger.info(f"Downloading image from S3: {job.input_s3_key}")
        buf = io.BytesIO()
        s3.download_fileobj(BUCKET, job.input_s3_key, buf)
        image_bytes = buf.getvalue()
        logger.info(f"Image downloaded successfully, size: {len(image_bytes)} bytes")

        # 2) 모델 호출
        logger.info(f"Calling model service for inference")
        resp = infer_image_bytes(image_bytes, filename=f"{job_id}.bin")
        logger.info(f"Model inference completed: {resp}")
        
        # resp 형태에 맞게 파싱 (두 형태 모두 지원 예시)
        summary = resp.get("summary")
        items = resp.get("items")
        text = resp.get("text")

        # summary가 없고 text만 있으면, 간단 파서로 요약 생성(임시)
        if not summary:
            summary = {"extracted_text": text}

        # 3) DB 저장
        logger.info(f"Saving results to database")
        with transaction.atomic():
            # 요약 upsert(없으면 생성)
            RecResultSummary.objects.update_or_create(
                job_id=job_id,  # pk 대신 job_id 사용
                defaults={
                    "store_name": summary.get("store_name"),
                    "payment_date": summary.get("payment_date"),
                    "card_company": summary.get("card_company"),
                    "card_number_masked": summary.get("card_number_masked"),
                    "total_amount": summary.get("total_amount"),
                    "currency": summary.get("currency","KRW"),
                    "extracted_text": summary.get("extracted_text"),
                    "raw_json": summary if isinstance(summary, dict) else None,
                }
            )
            # 품목 리스트 저장(있으면 교체)
            if items:
                RecResultItem.objects.filter(job_id=job_id).delete()
                bulk = []
                for idx, it in enumerate(items, start=1):
                    bulk.append(RecResultItem(
                        item_id=uuid.uuid4(),
                        job_id=job_id,
                        name=it.get("name",""),
                        unit_price=it.get("unit_price"),
                        quantity=it.get("quantity"),
                        amount=it.get("amount"),
                        line_no=idx,
                        extra=None
                    ))
                RecResultItem.objects.bulk_create(bulk, batch_size=500)
                logger.info(f"Saved {len(bulk)} items to database")

        # 4) CSV 생성 → S3 업로드
        logger.info(f"Generating CSV and uploading to S3")
        from .services.s3_client import presign_download
        out = io.StringIO()
        w = csv.writer(out)
        
        # CSV 헤더 (DB 스키마와 일치)
        w.writerow([
            "store_name", "payment_date", "card_company", "card_number_masked", 
            "total_amount", "currency", "item_name", "unit_price", "quantity", "amount"
        ])
        
        # 요약 로우 + 품목 펼치기
        sumrow = RecResultSummary.objects.get(job_id=job_id)  # pk 대신 job_id 사용
        items_qs = RecResultItem.objects.filter(job_id=job_id).order_by("line_no")
        
        if items_qs.exists():
            for it in items_qs:
                w.writerow([
                    sumrow.store_name, 
                    sumrow.payment_date.strftime("%Y-%m-%d %H:%M:%S") if sumrow.payment_date else "",
                    sumrow.card_company, 
                    sumrow.card_number_masked,
                    sumrow.total_amount, 
                    sumrow.currency,
                    it.name, 
                    it.unit_price, 
                    it.quantity, 
                    it.amount
                ])
        else:
            # 품목이 없으면 요약만 1행
            w.writerow([
                sumrow.store_name, 
                sumrow.payment_date.strftime("%Y-%m-%d %H:%M:%S") if sumrow.payment_date else "",
                sumrow.card_company, 
                sumrow.card_number_masked,
                sumrow.total_amount, 
                sumrow.currency,
                "", "", "", ""  # 품목 필드들
            ])

        result_key = f"results/{job_id}.csv"
        s3.put_object(Bucket=BUCKET, Key=result_key, Body=out.getvalue().encode("utf-8"),
                      ContentType="text/csv")
        logger.info(f"CSV uploaded to S3: {result_key}")

        # 5) 상태 DONE
        with transaction.atomic():
            job.result_s3_key = result_key
            job.status = RecJob.Status.DONE
            job.processed_at = timezone.now()
            job.save(update_fields=["result_s3_key","status","processed_at","updated_at"])
        
        logger.info(f"Job {job_id} completed successfully")
        return {"ok": True, "job_id": job_id}
        
    except RecJob.DoesNotExist:
        logger.error(f"Job {job_id} not found")
        return {"ok": False, "error": f"Job {job_id} not found"}
    except Exception as e:
        logger.error(f"Error in job {job_id}: {e}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job_id}, attempt {self.request.retries + 1}")
            raise self.retry(exc=e)
        
        # 최대 재시도 횟수 초과 시 실패 처리
        try:
            job = RecJob.objects.get(job_id=job_id)
            job.status = RecJob.Status.FAILED
            job.error_message = str(e)
            job.save(update_fields=["status","error_message","updated_at"])
            logger.error(f"Job {job_id} marked as FAILED")
        except Exception as save_error:
            logger.error(f"Failed to save error status for job {job_id}: {save_error}")
        
        return {"ok": False, "error": str(e)}
