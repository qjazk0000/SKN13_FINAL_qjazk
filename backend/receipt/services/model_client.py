import os, requests
MODEL_URL = os.getenv("MODEL_INFER_URL", "http://model:8001/infer")
TIMEOUT = int(os.getenv("MODEL_TIMEOUT_SEC", "120"))

def infer_image_bytes(image_bytes, filename="image.bin", content_type="application/octet-stream"):
    r = requests.post(MODEL_URL, files={"file": (filename, image_bytes, content_type)}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()