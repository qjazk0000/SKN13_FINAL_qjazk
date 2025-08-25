import os
import json
# from langchain_upstage import UpstageDocumentParseLoader, ChatUpstage
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import JsonOutputParser

# template = """영수증에서 다음 정보를 추출해서 JSON 형식으로 출력해주세요. 반드시
# json 코드 블록으로 감싸주세요.

# [추출 대상 항목]
# - 결제처: 매장 이름 또는 브랜드 이름 (매장명)
# - 결제일시: "YYYY-MM-DD HH:MM:SS" 형식으로 표기된 실제 결제 시간. 만약 시각 정보가 없다면 날짜만 추출해도 됩니다.
# - 카드사: 한국 내 주요 카드사 중 하나. 아래 리스트 중에 일치하는 카드사가 있다면 해당 카드사명만 출력:
#   [신한카드, 삼성카드, 현대카드, 롯데카드, KB국민카드, 우리카드, 하나카드, NH농협카드, 비씨카드, 카카오뱅크, 토스뱅크]
# - 카드번호: 마스킹된 번호 포함
# - 품목: 구매 항목 정보. 항목이 여러 개 있을 수 있으며, 각 항목에 대해 아래 정보를 포함해야 합니다:
#     - 품목: 상품 이름
#     - 단가: 한 개당 가격
#     - 수량: 구매 개수 (숫자만 추출)
#     - 금액: 해당 품목의 총 가격 = 단가 * 수량
# - 총합계: 모든 품목의 금액을 합한 총 구매 금액 (합계. 보통 받은 금액과 같음.)

# ※ 품목명은 정확하게 읽어주세요.
# ※ 동일한 품목이 여러 번 등장해도, 개별로 나열해주세요 (중복 제거 X).
# ※ 항목이 누락된 경우에는 빈 문자열("")로 남겨두세요.

# [영수증 내용]
# {context}
# """

# messages = [("human", template)]
# prompt = ChatPromptTemplate.from_messages(messages)
# chain = (
#     {"context": lambda x: "\n".join([doc.page_content for doc in x])}
#     | prompt
#     | ChatUpstage(temperature=0)
#     | JsonOutputParser()
# )

def extract_receipt_info(image_path: str) -> dict:
    """
    영수증 이미지 경로를 받아 Upstage OCR 결과(JSON)를 반환
    현재는 임시로 더미 데이터 반환
    """
    # TODO: Upstage API 키 설정 후 OCR 기능 활성화
    return {
        "결제처": "임시 매장명",
        "결제일시": "2025-01-01 12:00:00",
        "카드사": "신한카드",
        "카드번호": "****-****-****-1234",
        "품목": [
            {
                "품명": "임시 상품",
                "단가": 1000,
                "수량": 1,
                "금액": 1000
            }
        ],
        "총합계": 1000
    }