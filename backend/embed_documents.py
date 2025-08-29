#!/usr/bin/env python3
"""
PDF → Clean Text → Page-aware Chunking → KoE5 Embedding → Qdrant Upsert
- 불필요 문자/제어문자 제거(clean_text)
- 페이지 번호 보존 + 안정적 point ID(uuid5)
- 확장된 메타데이터(payload = metadata)
- 자주 쓰는 필드 인덱스 생성

사용법:
  python embed_documents.py                    # 기존 데이터 유지 (기본값)
  python embed_documents.py --reset           # 기존 데이터 삭제 후 새로 시작
  python embed_documents.py -r                # --reset의 축약형

사용 전 환경변수(.env 혹은 시스템 환경):
  PDF_DIR=/app/documents/kisa_pdf
  QDRANT_HOST=qdrant
  QDRANT_PORT=6333
  COLLECTION_NAME=regulations_final
  RESET_COLLECTION=false
  BATCH_SIZE=256

필요 패키지:
  pip install qdrant-client sentence-transformers PyPDF2 tqdm python-dotenv
"""
from __future__ import annotations

import os
import re
import sys
import uuid
import argparse
from uuid import uuid5, NAMESPACE_URL
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from tqdm import tqdm
from PyPDF2 import PdfReader

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# -------------------- 환경 --------------------
load_dotenv()
PDF_DIR = os.getenv("PDF_DIR", "/app/documents/kisa_pdf")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "regulations_final")
RESET_COLLECTION = os.getenv("RESET_COLLECTION", "false").lower() == "true"
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "256"))

# Embedding: KoE5 (한국어 최적화, 1024차원)
EMBED_MODEL = os.getenv("HF_MODEL", "nlpai-lab/KoE5")
EMBED_BACKEND = "hf"
EMBED_DIM = 1024

KST = timezone(timedelta(hours=9))

# -------------------- 유틸 --------------------
def now_year_kst() -> int:
    return datetime.now(KST).year

def calculate_recency_score(year: int) -> int:
    if not year:
        return 1
    cy = now_year_kst()
    if year >= cy:
        return 3
    elif year >= cy - 2:
        return 2
    else:
        return 1

def parse_register_date_from_filename(filename: str) -> Dict[str, Any]:
    """파일명 내 (YYMMDD) → ISO 및 파생값
    예) 3_16_전자서명... (210809).pdf → 2021-08-09
    """
    m = re.search(r"\((\d{6})\)", filename)
    if not m:
        return {"register_date_iso": None, "year": 0, "month": 0, "day": 0}
    y, mo, d = m.group(1)[:2], m.group(1)[2:4], m.group(1)[4:6]
    year = 2000 + int(y)
    return {
        "register_date_iso": f"{year:04d}-{int(mo):02d}-{int(d):02d}",
        "year": year,
        "month": int(mo),
        "day": int(d)
    }

# 불필요 문자/제어문자 제거
_DEF_SYMBOLS = "□■○●◆◇▶▷◀◁※☆★•ㆍ∙◦●▪︎▫︎❖✓✔✗✘❌"

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Zero-width & 제어문자 제거
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)              # zero-width
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", text)              # C0/C1 control
    # 도형/글머리 기호 제거 (필요 시 치환 태깅으로 변경 가능)
    text = re.sub(f"[{re.escape(_DEF_SYMBOLS)}]", " ", text)
    # 하이픈 줄바꿈 연결(워드랩 아티팩트)
    text = re.sub(r"-\s*\n\s*", "", text)
    # 여러 공백/탭 정규화
    text = re.sub(r"[ \t]+", " ", text)
    # 연속 공백 축소
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

# 머리말 제거 정규식 수정
_DEF_HEADER_RE = re.compile(r"제\s*\d+\s*(장|조)")

def strip_header(text: str) -> str:
    m = _DEF_HEADER_RE.search(text or "")
    return text[m.start():] if m else (text or "")

# 파일명 기반 도메인/서브도메인/문서타입 추정

def classify_domain_by_filename(filename: str) -> str:
    f = filename.casefold()
    if any(k in f for k in ["인사","급여","채용","복무","교육"]):
        return "인사관리"
    if any(k in f for k in ["회계","예산","감사","재정","계약","자산"]):
        return "재무관리"
    if any(k in f for k in ["보안","정보보호","개인정보","민원"]):
        return "보안관리"
    if any(k in f for k in ["기술","정보화","전자서명","시스템","it"]):
        return "기술관리"
    if any(k in f for k in ["문서","자료","기록","홍보"]):
        return "행정관리"
    if any(k in f for k in ["경영","성과","내부통제","조직","직제"]):
        return "경영관리"
    return "일반"

def extract_subdomain_by_filename(filename: str, domain: str) -> str:
    f = filename.casefold()
    if domain == "인사관리":
        if any(k in f for k in ["급여","봉급"]): return "급여관리"
        if any(k in f for k in ["채용","임용"]): return "채용관리"
        if any(k in f for k in ["복무","근무"]): return "복무관리"
        if any(k in f for k in ["교육","훈련"]): return "교육훈련"
        return "인사정책"
    if domain == "재무관리":
        if any(k in f for k in ["회계","장부"]): return "회계관리"
        if any(k in f for k in ["감사","감사인"]): return "감사관리"
        if any(k in f for k in ["계약","계약사무"]): return "계약관리"
        if any(k in f for k in ["자산","비유동자산"]): return "자산관리"
        return "재무정책"
    if domain == "보안관리":
        if any(k in f for k in ["정보보호","정보보안"]): return "정보보호"
        if any(k in f for k in ["개인정보","개인정보보호"]): return "개인정보보호"
        if any(k in f for k in ["민원","신고"]): return "민원신고"
        return "보안정책"
    if domain == "기술관리":
        if any(k in f for k in ["정보화","정보시스템"]): return "정보화관리"
        if any(k in f for k in ["전자서명","인증"]): return "전자서명관리"
        return "기술정책"
    if domain == "행정관리":
        if any(k in f for k in ["문서","문서관리"]): return "문서관리"
        if any(k in f for k in ["자료","자료관리"]): return "자료관리"
        if any(k in f for k in ["기록","기록물"]): return "기록관리"
        return "행정정책"
    if domain == "경영관리":
        if any(k in f for k in ["성과","성과평가"]): return "성과관리"
        if any(k in f for k in ["내부통제","통제"]): return "내부통제"
        if any(k in f for k in ["조직","직제"]): return "조직관리"
        return "경영정책"
    return "일반"

def infer_doc_level(filename: str) -> str:
    if filename.startswith("1_"): return "정관"
    if filename.startswith("2_"): return "규정"
    if filename.startswith("3_"): return "규칙"
    if filename.startswith("4_"): return "지침"
    return "기타"

def stable_doc_id(file_name: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"doc::{file_name}"))

# -------------------- Qdrant --------------------

def ensure_collection(client: QdrantClient, force_reset: bool = False):
    """컬렉션 생성 또는 재설정"""
    if force_reset:
        try:
            print(f"🗑️ 기존 컬렉션 '{COLLECTION_NAME}' 삭제 중...")
            client.delete_collection(COLLECTION_NAME)
            print(f"✅ 컬렉션 삭제 완료")
        except Exception:
            pass
    
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        print(f"📝 컬렉션 '{COLLECTION_NAME}' 생성 중...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE)
        )
        # payload 인덱스 생성(없는 경우만)
        for field, schema in [
            ("document_type","keyword"), ("document_level","keyword"),
            ("domain_primary","keyword"), ("domain_secondary","keyword"),
            ("year","integer"), ("recency_score","integer"),
            ("page","integer"), ("chunk_index","integer"),
            ("register_date_iso","datetime"), ("doc_title","keyword"),
            ("doc_type","keyword"),
        ]:
            try:
                client.create_payload_index(COLLECTION_NAME, field_name=field, field_schema=schema)
            except Exception:
                pass
        print(f"✅ 컬렉션 생성 완료")
    else:
        print(f"ℹ️ 컬렉션 '{COLLECTION_NAME}'이 이미 존재합니다.")

# -------------------- 메인 파이프라인 --------------------

def read_pdf_by_page(pdf_path: Path) -> List[Tuple[int, str]]:
    reader = PdfReader(str(pdf_path))
    out = []
    for i, page in enumerate(reader.pages, start=1):
        txt = page.extract_text() or ""
        out.append((i, txt))
    return out

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    # 간단 슬라이딩 윈도우 (langchain splitter 없이도 충분)
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(end - chunk_overlap, start + 1)
    return chunks

def main():
    # 명령줄 인수 파싱
    parser = argparse.ArgumentParser(description='PDF 문서 임베딩 및 Qdrant 업로드')
    parser.add_argument('--reset', '-r', action='store_true', 
                       help='기존 데이터 모두 삭제하고 새로 시작')
    args = parser.parse_args()
    
    print("🚀 KoE5 임베딩 + Qdrant 업서트 시작")
    
    if args.reset:
        print("🔄 기존 데이터를 모두 삭제하고 새로 시작합니다.")
    else:
        print("✅ 기존 데이터를 유지하고 새로 추가합니다.")
    
    embedder = SentenceTransformer(EMBED_MODEL)
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, prefer_grpc=True)
    ensure_collection(client, force_reset=args.reset)

    pdf_dir = Path(PDF_DIR)
    if not pdf_dir.is_dir():
        print(f"❌ PDF 디렉토리 없음: {pdf_dir}")
        return

    pdf_files = sorted([p for p in pdf_dir.glob("*.pdf")])
    if not pdf_files:
        print("❌ PDF 없음")
        return

    print(f"📚 총 {len(pdf_files)}개의 PDF 파일을 처리합니다.")

    batch: List[PointStruct] = []

    for pdf_path in tqdm(pdf_files, desc="Index PDFs"):
        file = pdf_path.name
        doc_id = stable_doc_id(file)
        meta_date = parse_register_date_from_filename(file)
        domain_primary = classify_domain_by_filename(file)
        domain_secondary = extract_subdomain_by_filename(file, domain_primary)

        try:
            pages = read_pdf_by_page(pdf_path)
            total_pages = len(pages)

            for page_no, raw_text in pages:
                # 전처리: 헤더 제거 → 불필요문자 제거 → 청크
                page_text = clean_text(strip_header(raw_text))
                if not page_text:
                    continue
                chunks = [clean_text(c) for c in chunk_text(page_text)]
                if not chunks:
                    continue

                # 배치 임베딩 (문서엔 embed_documents)
                vecs = embedder.encode(chunks, batch_size=32, show_progress_bar=False)

                # 공통 payload
                payload_common: Dict[str, Any] = {
                    "doc_id": doc_id,
                    "doc_title": file.replace(".pdf", ""),
                    "file_path": str(pdf_path),
                    "source": file.replace(".pdf", ""),
                    "document_level": infer_doc_level(file),
                    "document_type": infer_doc_level(file),
                    "domain_primary": domain_primary,
                    "domain_secondary": domain_secondary,
                    "register_date_iso": meta_date["register_date_iso"],
                    "year": meta_date["year"],
                    "month": meta_date["month"],
                    "day": meta_date["day"],
                    "recency_score": calculate_recency_score(meta_date["year"]),
                    "total_pages": total_pages,
                    "file_size": pdf_path.stat().st_size,
                    "embed_backend": EMBED_BACKEND,
                    "embed_model": EMBED_MODEL,
                    "embed_dim": EMBED_DIM,
                }

                total_chunks = len(chunks)
                for idx, (chunk, vec) in enumerate(zip(chunks, vecs)):
                    payload = {
                        **payload_common,
                        "text": chunk,
                        "page": page_no,
                        "chunk_index": idx,
                        "total_chunks": total_chunks,
                        "chunk_char_len": len(chunk),
                        "doc_type": "text",
                    }
                    point_id = str(uuid5(NAMESPACE_URL, f"{doc_id}:{page_no}:t:{idx}"))
                    batch.append(PointStruct(id=point_id, vector=vec.tolist() if hasattr(vec, 'tolist') else vec, payload=payload))

                    if len(batch) >= BATCH_SIZE:
                        client.upsert(collection_name=COLLECTION_NAME, points=batch)
                        batch.clear()
        except Exception as e:
            print(f"❌ 실패 {file}: {e}")

    if batch:
        client.upsert(collection_name=COLLECTION_NAME, points=batch)

    info = client.get_collection(COLLECTION_NAME)
    print(f"🎉 완료. points: {getattr(info, 'points_count', 'N/A')}")

if __name__ == "__main__":
    main() 