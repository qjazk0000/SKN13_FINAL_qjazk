import os
import re
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFFormExtractorV6:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 개별 서식 시작을 나타내는 패턴들 (개선됨)
        self.form_start_patterns = [
            r'^\s*\[별지\s*제\d+호\s*서식\]',
            r'^\s*\[별표\s*\d*\]',
            r'^\s*\[부록\s*\d*\]',
            r'^\s*\[첨부서식\s*\d*\]',
            r'^\s*\[첨부양식\s*\d*\]',
        ]
        
        # 서식 제목 패턴들 (분석 결과를 바탕으로 확장)
        self.form_title_patterns = [
            # 신청/제출 관련
            r'신청서', r'제출서', r'청구서', r'요청서', r'요구서', r'사유서', r'취소신청서', r'재발급신청서', r'인증연장신청서',
            # 보고/평가 관련
            r'보고서', r'평가서', r'평가표', r'점검표', r'체크리스트', r'확인서', r'요약서', r'결과표', r'검토서', r'결과확인서', r'완료확인서',
            # 서약/계약 관련
            r'서약서', r'계약서', r'협약서', r'각서', r'조서', r'확약서', r'윤리서약서', r'보안서약서', r'직무윤리서약서',
            # 승인/통지 관련
            r'승인서', r'통지서', r'통보서', r'발주서', r'입찰서', r'고지', r'처분서',
            # 등록/변경 관련
            r'등록서', r'변경서', r'폐지서', r'정지서', r'회복서', r'작업중지',
            # 관리/운영 관련
            r'관리서', r'운영서', r'처리서', r'관리방침', r'전결규정', r'처리내역', r'관리대장', r'출입관리대장',
            # 대장/접수 관련
            r'대장', r'접수증', r'접수대장', r'위촉장', r'일지', r'점검일지', r'이력카드', r'키관리대장', r'문서관리대장',
            # 인사 관련
            r'자격기준', r'지급기준', r'전형단계', r'사직원', r'휴직원', r'복직원', r'추천서', r'인적사항', r'추천사유', r'심사', r'성과평가표',
            # 급여 관련
            r'급여', r'산정기준액', r'수당', r'명예퇴직금', r'직무급', r'자격수당지급신청서',
            # 안전보건 관련
            r'안전보건관리체계', r'산업안전보건위원회',
            # 조직/직무 관련
            r'조직도', r'직무분장표', r'분류표', r'직호', r'직무명', r'직무구분',
            # 의결/결의 관련
            r'의결서', r'결의서', r'결의표', r'안건', r'서면결의서', r'심의의결서',
            # 감사/의견 관련
            r'감사', r'의견서', r'진술서', r'검토의견서', r'심의의견서', r'다면평가서',
            # 문답 관련
            r'문답서', r'질문서',
            # 인증/시험 관련
            r'인증서', r'시험신청서', r'시험계약서', r'인증평가서', r'성능평가서', r'보안인증서',
            # 동의/약관 관련
            r'동의서', r'이용약관', r'개인정보수집이용동의서', r'사후관리동의서',
            # 현황/명세 관련
            r'현황', r'명세서', r'내역서', r'요약서', r'프로파일',
            # 기타
            r'환산표', r'프로파일', r'기준', r'절차', r'심의항목', r'세부기준', r'검토자료',
            # 서식 구분
            r'양식', r'서식', r'별지', r'별표', r'부록', r'첨부',
        ]
    
    def is_form_page(self, text):
        """페이지가 서식 페이지인지 확인합니다."""
        if not text:
            return False
        
        lines = text.split('\n')
        
        # 첫 번째 라인에서 서식 시작 패턴 확인
        if lines:
            first_line = lines[0].strip()
            for pattern in self.form_start_patterns:
                if re.search(pattern, first_line, re.IGNORECASE):
                    return True
        
        return False
    
    def extract_form_title(self, text):
        """서식 페이지에서 제목을 추출합니다."""
        if not text:
            return None
        
        lines = text.split('\n')
        
        # 첫 번째 라인에서 서식 번호와 제목이 함께 있는 경우 처리
        if lines:
            first_line = lines[0].strip()
            # [별지 제1호 서식] 제목 패턴에서 제목 부분만 추출
            match = re.search(r'\[별지\s*제\d+호\s*서식\]\s*(.+)', first_line)
            if match and match.group(1).strip():
                form_title = match.group(1).strip()
            else:
                # [별표 1] 제목 패턴에서 제목 부분만 추출
                match = re.search(r'\[별표\s*\d*\]\s*(.+)', first_line)
                if match and match.group(1).strip():
                    form_title = match.group(1).strip()
                else:
                    # 첫 번째 라인에 제목이 없으면 다음 라인들에서 찾기
                    form_title = None
                    for i in range(1, min(6, len(lines))):
                        line = lines[i].strip()
                        if line and len(line) > 2:
                            # 서식 제목 패턴이 포함된 라인 찾기
                            for pattern in self.form_title_patterns:
                                if pattern in line:
                                    form_title = line
                                    break
                            if form_title:
                                break
                    
                    # 여전히 제목을 찾지 못했으면 첫 번째 라인 사용
                    if not form_title:
                        form_title = first_line
        
        # 파일명으로 사용할 수 있도록 정리
        if form_title:
            # 특수문자 제거 및 공백 처리
            form_title = re.sub(r'[^\w\s가-힣]', '', form_title)
            form_title = re.sub(r'\s+', '_', form_title.strip())
            # 연속된 언더스코어 제거
            form_title = re.sub(r'_+', '_', form_title)
            # 앞뒤 언더스코어 제거
            form_title = form_title.strip('_')
            form_title = form_title[:50]  # 길이 제한
        
        return form_title
    
    def find_all_form_pages(self, pdf_path):
        """PDF에서 모든 서식 페이지를 찾습니다."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                form_pages = []
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if self.is_form_page(text):
                        form_pages.append(page_num)
                
                return form_pages
        except Exception as e:
            logger.error(f"서식 페이지 찾기 실패: {str(e)}")
            return []
    
    def extract_forms_from_pdf(self, pdf_path):
        """PDF 파일에서 모든 개별 표/서식을 추출합니다."""
        pdf_name = pdf_path.stem
        logger.info(f"처리 중: {pdf_name}")
        
        try:
            # 모든 서식 페이지 찾기
            form_pages = self.find_all_form_pages(pdf_path)
            
            if not form_pages:
                logger.warning(f"  {pdf_name}: 서식 페이지를 찾을 수 없습니다.")
                return
            
            logger.info(f"  발견된 서식 페이지: {[p+1 for p in form_pages]}")
            
            # PyPDF2로 페이지 분할
            pdf_reader = PdfReader(pdf_path)
            
            # 각 서식 페이지를 개별 파일로 저장
            for page_num in form_pages:
                if page_num >= len(pdf_reader.pages):
                    continue
                
                # 서식 제목 추출
                with pdfplumber.open(pdf_path) as pdf:
                    form_page = pdf.pages[page_num]
                    text = form_page.extract_text()
                    form_title = self.extract_form_title(text)
                
                # 개별 PDF 생성
                pdf_writer = PdfWriter()
                pdf_writer.add_page(pdf_reader.pages[page_num])
                
                # 출력 파일명 생성
                if form_title:
                    output_filename = f"{pdf_name}_{form_title}.pdf"
                else:
                    output_filename = f"{pdf_name}_서식_{page_num+1:03d}.pdf"
                
                output_path = self.output_dir / output_filename
                
                with open(output_path, "wb") as output_file:
                    pdf_writer.write(output_file)
                
                logger.info(f"  저장됨: {output_filename} (페이지 {page_num + 1})")
                if form_title:
                    logger.info(f"    제목: {form_title}")
            
        except Exception as e:
            logger.error(f"  {pdf_name} 처리 중 오류 발생: {str(e)}")
    
    def process_all_pdfs(self):
        """입력 디렉토리의 모든 PDF 파일을 처리합니다."""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"입력 디렉토리에서 PDF 파일을 찾을 수 없습니다: {self.input_dir}")
            return
        
        logger.info(f"총 {len(pdf_files)}개의 PDF 파일을 처리합니다.")
        
        processed_count = 0
        for pdf_file in pdf_files:
            try:
                self.extract_forms_from_pdf(pdf_file)
                processed_count += 1
            except Exception as e:
                logger.error(f"파일 처리 실패 {pdf_file.name}: {str(e)}")
        
        logger.info(f"처리 완료: {processed_count}/{len(pdf_files)} 파일")

def main():
    # 설정
    input_directory = "/app/documents/kisa_pdf"
    output_directory = "/app/documents/kisa_pdf/forms_extracted_v6"
    
    # 추출기 생성 및 실행
    extractor = PDFFormExtractorV6(input_directory, output_directory)
    extractor.process_all_pdfs()

if __name__ == "__main__":
    main()
