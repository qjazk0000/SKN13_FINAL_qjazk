#!/usr/bin/env python3
"""
문서 임베딩 스크립트
embedding.ipynb를 기반으로 작성
"""

import os
import re
import uuid
from pathlib import Path
from PyPDF2 import PdfReader
from tqdm import tqdm

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# === 설정 ===
PDF_DIR = "/app/documents/kisa_pdf"  # Docker 컨테이너 내부 경로
COLLECTION_NAME = "regulations_final"
EMBED_MODEL = "nlpai-lab/KoE5"
EMBED_DIM = 1024
BATCH_SIZE = 100

def main():
    print("🚀 문서 임베딩 시작...")
    
    # 임베딩 모델 초기화
    print("📥 임베딩 모델 로딩 중...")
    embedding_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    
    # 텍스트 분할기 초기화
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    # Qdrant 클라이언트 초기화 (Docker 컨테이너 내부 주소)
    print("🔗 Qdrant 연결 중...")
    qdrant_client = QdrantClient(host="qdrant", port=6333)
    
    # 컬렉션 확인
    collections = qdrant_client.get_collections()
    collection_names = [c.name for c in collections.collections]
    
    if COLLECTION_NAME in collection_names:
        print(f"✅ 컬렉션 '{COLLECTION_NAME}' 이미 존재합니다.")
    else:
        print(f"📝 컬렉션 '{COLLECTION_NAME}' 생성 중...")
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE)
        )
    
    def strip_header(text: str) -> str:
        """PDF 헤더 제거"""
        match = re.search(r"제\s*\d+\s*[장|조]", text)
        return text[match.start():] if match else text
    
    # === PDF 임베딩 및 업로드 ===
    print("📚 PDF 문서 처리 중...")
    points = []
    total_files = 0
    processed_files = 0
    
    # PDF 파일 목록 확인
    if not os.path.exists(PDF_DIR):
        print(f"❌ PDF 디렉토리를 찾을 수 없습니다: {PDF_DIR}")
        return
    
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
    total_files = len(pdf_files)
    
    if total_files == 0:
        print("❌ PDF 파일을 찾을 수 없습니다.")
        return
    
    print(f"📄 총 {total_files}개의 PDF 파일을 처리합니다.")
    
    for file in tqdm(pdf_files, desc="PDF 처리"):
        if not file.endswith(".pdf"):
            continue
            
        filepath = os.path.join(PDF_DIR, file)
        filename = Path(filepath).name
        
        try:
            reader = PdfReader(filepath)
            full_text = "\n".join([p.extract_text() or "" for p in reader.pages]).strip()
            main_text = strip_header(full_text)
            
            # 등록 날짜 추출
            register_date = re.search(r"\((\d{6})\)", filename)
            
            metadata_common = {
                "register_date": register_date.group(1) if register_date else "unknown",
                "doc_title": filename.replace(".pdf", ""),
                "file_path": str(Path(filepath)),
                "source": filename.replace(".pdf", ""),  # RAG 서비스에서 사용
                "page": "1"  # 기본값
            }
            
            # 텍스트 분할
            chunks = text_splitter.split_text(main_text)
            
            for i, chunk in enumerate(chunks):
                # 페이지 번호 업데이트 (대략적인 추정)
                chunk_metadata = metadata_common.copy()
                chunk_metadata["page"] = str(i + 1)
                
                # 임베딩 생성
                vector = embedding_model.embed_query(chunk)
                points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": chunk,
                        **chunk_metadata
                    }
                ))
                
                # 배치 처리
                if len(points) >= BATCH_SIZE:
                    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
                    print(f"  📤 {len(points)}개 벡터 업로드 완료")
                    points = []
            
            processed_files += 1
            
        except Exception as e:
            print(f"❌ 파일 처리 실패: {filename} - {str(e)}")
            continue
    
    # 남은 포인트 처리
    if points:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"  📤 마지막 {len(points)}개 벡터 업로드 완료")
    
    # 최종 결과 확인
    collection_info = qdrant_client.get_collection(COLLECTION_NAME)
    total_points = collection_info.points_count
    
    print(f"\n🎉 임베딩 완료!")
    print(f"📊 처리된 파일: {processed_files}/{total_files}")
    print(f"🔢 총 벡터 수: {total_points}")
    print(f"📁 컬렉션: {COLLECTION_NAME}")

if __name__ == "__main__":
    main() 