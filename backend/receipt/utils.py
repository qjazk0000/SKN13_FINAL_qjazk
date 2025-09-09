# receipts/utils.py
import os
import json
import base64
import cv2
import numpy as np
from openai import OpenAI

# --------------------------
# Upstage API 설정
# --------------------------
UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY")
client = OpenAI(api_key=UPSTAGE_API_KEY,
                base_url="https://api.upstage.ai/v1/information-extraction")


# --------------------------
# 1) 공통 유틸
# --------------------------
def _to_base64(img_path: str) -> str:
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _safe_out_path(image_path: str, suffix: str = "_proc", ext_fallback: str = ".png") -> str:
    root, ext = os.path.splitext(image_path)
    if not ext or ext.lower() not in (".png", ".jpg", ".jpeg"):
        ext = ext_fallback
    return f"{root}{suffix}{ext}"


# --------------------------
# 2) 분류 기준 (edge_density)
# --------------------------
def _edge_density(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 60, 180)
    return float(np.mean(edges > 0) * 100.0)  # % 단위


def classify_receipt(gray: np.ndarray) -> tuple[str, float]:
    """
    edge_density >= 10 → scan, 아니면 photo
    """
    ed = _edge_density(gray)
    if ed >= 10:
        return "scan", ed
    return "photo", ed


# --------------------------
# 3) 타입별 전처리
# --------------------------
def _preprocess_photo(
    gray,
    alpha: float = 1.65,
    beta: int = 8,
    blockSize: int = 31,   # 홀수! 21~41 구간에서 미세 튜닝
    C: int = 7,
    do_median: bool = True,
    ksize_median: int = 3,
    do_close: bool = True,
    close_kernel: tuple = (2, 2),
):
    # 1) 대비/밝기
    adj = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    # 2) 노이즈 억제
    if do_median and ksize_median > 1:
        adj = cv2.medianBlur(adj, ksize_median)

    # 3) 적응형 이진화
    bin_img = cv2.adaptiveThreshold(
        adj, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize, C
    )

    # 4) 얇은 획 보강
    if do_close:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, close_kernel)
        bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel, iterations=1)

    return bin_img

def preprocess_receipt(image_path: str) -> tuple[str, str, float]:
    """
    원본 이미지 로드 → 분류(photo/scan) → 전처리 → 저장 경로 반환
    """
    bgr = cv2.imread(image_path)
    if bgr is None:
        raise FileNotFoundError(image_path)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    mode, ed = classify_receipt(gray)

    if mode == "photo":
        out = _preprocess_photo(gray)
    else:
        return image_path, mode, ed

    out_path = _safe_out_path(image_path, suffix=f"_proc_{mode}")
    cv2.imwrite(out_path, out)

    return out_path, mode, ed


# --------------------------
# 4) Upstage 정보 추출 호출
# --------------------------
def _call_information_extraction(base64_data: str) -> dict:
    response = client.chat.completions.create(
        model="information-extract",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url",
                     "image_url": {"url": f"data:application/octet-stream;base64,{base64_data}"}}
                ],
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "receipt_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "storeName": {"type": "string"},
                        "transactionDate": {"type": "string"},
                        "cardCompany": {"type": "string"},
                        "cardNumber": {"type": "string"},
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "productName": {"type": "string"},
                                    "unitPrice": {"type": "number"},
                                    "quantity": {"type": "integer"},
                                    "totalPrice": {"type": "number"}
                                }
                            }
                        },
                        "transactionAmount": {"type": "number"}
                    }
                }
            }
        }
    )
    return json.loads(response.choices[0].message.content)


def extract_receipt_info(image_path: str) -> dict:
    """
    메인 엔드포인트:
    - edge_density 기준으로 scan/photo 분류
    - 전처리 후 Upstage Information Extraction 호출
    """
    proc_path, mode, ed = preprocess_receipt(image_path)
    base64_data = _to_base64(proc_path)

    try:
        result = _call_information_extraction(base64_data)
    except Exception as e:
        print("Upstage API 호출 오류:", e)
        return {}

    if isinstance(result, dict):
        result.setdefault("_preprocess_mode", mode)
        result.setdefault("_edge_density", ed)

    return result
