import os
from typing import List, Dict
from django.conf import settings
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI

SYSTEM_PROMPT = """당신은 한국어 규정/규칙/지침 문서를 바탕으로 답변하는 도우미입니다.
- 아래 '컨텍스트'의 근거만 활용해 간결하고 정확하게 답하십시오.
- 추측하지 말고, 컨텍스트에 없으면 '해당 근거를 찾지 못했습니다'라고 답하세요.
- 필요한 경우 관련 조항/문서명/페이지를 함께 제시하세요.
"""

# QdrantClient를 전역으로 생성 (연결 재사용)
_qdrant_client = None
_embedder = None

def _get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _qdrant_client

def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("nlpai-lab/KoE5")
    return _embedder

def _build_context(chunks: List[Dict]) -> str:
    lines = []
    for i, c in enumerate(chunks, start=1):
        # ScoredPoint 객체에서 payload 속성 접근
        src = c.payload.get("source", "알 수 없음")
        page = c.payload.get("page", "알 수 없음")
        text = c.payload.get("text", "내용 없음")
        lines.append(f"[{i}] ({src} p.{page}) {text}")
    return "\n\n".join(lines)

def retrieve(question: str, top_k: int = None) -> List[Dict]:
    top_k = top_k or settings.RAG_TOP_K
    client = _get_qdrant_client()
    embedder = _get_embedder()
    qvec = embedder.encode([question])[0].tolist()

    res = client.search(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        query_vector=qvec,
        limit=top_k,
    )
    return res

def generate_answer(question: str, retrieved: List[Dict]) -> Dict:
    ctx = _build_context(retrieved)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    user_prompt = f"""컨텍스트:
{ctx}

질문:
{question}

요구사항:
- 한국어로 답변
- 컨텍스트에서 근거가 되는 조항과 문서명을 간단히 명시
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    answer = resp.choices[0].message.content
    sources = [
        {
            "source": r.payload.get("source", "알 수 없음"),
            "page": r.payload.get("page", "알 수 없음"),
            "path": r.payload.get("path", "알 수 없음"),
        }
        for r in retrieved
    ]
    return {"answer": answer, "sources": sources}

def rag_answer(question: str) -> Dict:
    retrieved = retrieve(question)
    return generate_answer(question, retrieved)
