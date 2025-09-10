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
# 공통 유틸
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
# 1) Auto Scan (배경 제거 + 수평 맞춤)
# --------------------------
def auto_scan(image_path: str) -> str:
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(image_path)

    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = cv2.resize(image, (int(image.shape[1] * 500 / image.shape[0]), 500))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 25, 200)

    # 외곽선 검출
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is not None:
        rect = np.zeros((4, 2), dtype="float32")
        pts = screenCnt.reshape(4, 2) * ratio
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        (tl, tr, br, bl) = rect
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))
    else:
        warped = orig

    out_path = _safe_out_path(image_path, suffix="_scan")
    cv2.imwrite(out_path, warped)
    return out_path


# --------------------------
# 2) Photo / Scan 분류
# --------------------------
def _edge_density(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 60, 180)
    return float(np.mean(edges > 0) * 100.0)

def classify_receipt(gray: np.ndarray) -> tuple[str, float]:
    """
    edge_density >= 10 → scan, 아니면 photo
    """
    ed = _edge_density(gray)
    if ed >= 10:
        return "scan", ed
    return "photo", ed


# --------------------------
# 3) Photo 전처리
# --------------------------
def _preprocess_photo(
    gray,
    alpha: float = 1.65,
    beta: int = 8,
    blockSize: int = 31,
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


# --------------------------
# 4) Preprocess 전체
# --------------------------
def preprocess_receipt(image_path: str) -> tuple[str, str, float, str]:
    """
    1) Auto scan
    2) gray 변환
    3) classify (photo/scan)
    4) photo → _preprocess_photo
    """
    scan_path = auto_scan(image_path)
    bgr = cv2.imread(scan_path)
    if bgr is None:
        raise FileNotFoundError(scan_path)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    mode, ed = classify_receipt(gray)

    if mode == "photo":
        out = _preprocess_photo(gray)
        out_path = _safe_out_path(scan_path, suffix=f"_proc_{mode}")
        cv2.imwrite(out_path, out)
        return out_path, mode, ed, scan_path
    else:
        return image_path, mode, ed, image_path


# --------------------------
# 5) Upstage API 호출
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


# --------------------------
# 6) 메인 엔트리
# --------------------------
def extract_receipt_info(image_path: str) -> dict:
    """
    - auto scan → classify → 전처리(photo/scan)
    - OCR API 호출
    """
    proc_path, mode, ed, scan_path = preprocess_receipt(image_path)
    base64_data = _to_base64(proc_path)

    try:
        result = _call_information_extraction(base64_data)
    except Exception as e:
        print("Upstage API 호출 오류:", e)
        return {}

    if isinstance(result, dict):
        result.setdefault("_preprocess_mode", mode)
        result.setdefault("_edge_density", ed)
        result.setdefault("_processed_path", proc_path)  # OCR용
        result.setdefault("_scan_path", scan_path)        # S3 업로드용

    return result
