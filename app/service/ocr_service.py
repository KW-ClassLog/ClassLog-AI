import os
import tempfile
import subprocess
from PIL import Image
from typing import List
import pytesseract
import fitz
import requests
from docx2pdf import convert as convert_docx_to_pdf
from urllib.parse import urlparse
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor


# 이미지 전처리 함수(이진화)
def preprocess_image(img: Image.Image):
    gray = img.convert("L")
    bw = gray.point(lambda x: 0 if x < 150 else 255, '1')
    return bw

def process_image(img: Image.Image) -> str:
    processed = preprocess_image(img)
    return extract_text(processed) or "[내용 없음]"

# 이미지 -> 텍스트 추출 함수(OCR)
def extract_text(img: Image.Image):
    config = '--psm 6 -l kor+eng'
    return pytesseract.image_to_string(img, config=config).strip()

# PDF -> 이미지로 변환
def convert_pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

# pdf, ppt, docx, hwp 파일 형식 처리
def convert_to_images(file_path: str) -> List[Image.Image]:
    file_ext = remove_url_query(file_path)
    ext = os.path.splitext(file_ext)[1].lower()
    if ext == ".pdf":
        return convert_pdf_to_images_from_url(file_path)
    elif ext == ".pptx":
        return convert_pptx_to_images(file_path)
    elif ext == ".docx":
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            convert_docx_to_pdf(file_path, tmp_pdf.name)
            return convert_pdf_to_images(tmp_pdf.name)
    elif ext == ".hwp":
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "converted.pdf")
            libreoffice_convert_to_pdf(file_path, pdf_path)
            return convert_pdf_to_images(pdf_path)
    elif ext == ".hwpx":
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "converted.pdf")
            libreoffice_convert_to_pdf(file_path, pdf_path)
            return convert_pdf_to_images(pdf_path)    
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}")
    
# 강의자료 이미지로 변환
def convert_pdf_to_images_from_url(pdf_url: str) -> List[Image.Image]:
    response = requests.get(pdf_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download file from URL: {pdf_url}")
    
    pdf_bytes = BytesIO(response.content)
    return convert_pdf_to_images(pdf_bytes)

# ppt -> 이미지 변환 함수
def convert_pptx_to_images(pptx_path: str) -> List[Image.Image]:
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "converted.pdf")
        libreoffice_convert_to_pdf(pptx_path, pdf_path)
        return convert_pdf_to_images(pdf_path)

# hwp -> pdf 변환 함수(hwp는 이미지로 바로 변환 안 됨)
def libreoffice_convert_to_pdf(input_path: str, output_path: str):
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", os.path.dirname(output_path),
        input_path
    ], check=True)

# S3 URL 쿼리 파라미터 제거 함수
def remove_url_query(file_path: str) -> str:
    parsed_url = urlparse(file_path)
    return parsed_url.path

def process_image(img: Image.Image) -> str:
    processed = preprocess_image(img)
    return extract_text(processed) or "[내용 없음]"

# 문서 통합 OCR 처리 함수
def process_any_documents(file_paths_str: str) -> str:
    file_paths = [url.strip() for url in file_paths_str.split(",") if url.strip()]
    all_texts = []

    for file_path in file_paths:
        try:
            pages = convert_to_images(file_path)
            with ThreadPoolExecutor(max_workers=4) as executor:  # 병렬 처리
                texts = list(executor.map(process_image, pages))
            all_texts.append("\n\n".join(texts))
        except Exception as e:
            all_texts.append(f"[오류 발생: {file_path}]\n{str(e)}")

    return "\n\n".join(all_texts)