# receipts/utils.py
import os
import json
import base64
from openai import OpenAI

# Upstage API 설정
UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY")
client = OpenAI(api_key=UPSTAGE_API_KEY, base_url="https://api.upstage.ai/v1/information-extraction")


def encode_img_to_base64(img_path: str) -> str:
    """이미지를 base64 문자열로 변환"""
    with open(img_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def extract_receipt_info(image_path: str) -> dict:
    """
    영수증 이미지에서 정보 추출 (Upstage Information Extraction 모델 사용)
    """
    base64_data = encode_img_to_base64(image_path)

    # Information Extraction API 요청
    response = client.chat.completions.create(
        model="information-extract",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:application/octet-stream;base64,{base64_data}"
                        }
                    }
                ]
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

    # 결과 파싱
    try:
        parsed = json.loads(response.choices[0].message.content)
        return parsed
    except Exception as e:
        print("결과 파싱 오류:", e)
        return {}