from PIL import Image
import os
import tempfile
import subprocess
from typing import List
import pytesseract
from pdf2image import convert_from_path
from docx2pdf import convert as convert_docx_to_pdf
from urllib.parse import urlparse


# 이미지 전처리 함수(이진화)
def preprocess_image(img: Image.Image):
    gray = img.convert("L")
    bw = gray.point(lambda x: 0 if x < 150 else 255, '1')
    return bw

# 이미지 -> 텍스트 추출 함수(OCR)
def extract_text(img: Image.Image):
    config = '--psm 6 -l kor+eng'
    return pytesseract.image_to_string(img, config=config).strip()

# pdf, ppt, docx, hwp -> 이미지 변환 함수
def convert_to_images(file_path: str) -> List[Image.Image]:
    file_ext = remove_url_query(file_path)
    ext = os.path.splitext(file_ext)[1].lower()
    if ext == ".pdf":
        return convert_from_path(file_path, dpi=300)
    elif ext == ".pptx":
        return convert_pptx_to_images(file_path)
    elif ext == ".docx":
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            convert_docx_to_pdf(file_path, tmp_pdf.name)
            return convert_from_path(tmp_pdf.name, dpi=300)
    elif ext == ".hwp":
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "converted.pdf")
            libreoffice_convert_to_pdf(file_path, pdf_path)
            return convert_from_path(pdf_path, dpi=300)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}")

# ppt -> 이미지 변환 함수
def convert_pptx_to_images(pptx_path: str) -> List[Image.Image]:
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "converted.pdf")
        libreoffice_convert_to_pdf(pptx_path, pdf_path)
        return convert_from_path(pdf_path, dpi=300)

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

# 문서 통합 OCR 처리 함수
def process_any_document(file_path: str) -> str:
    pages = convert_to_images(file_path)
    texts = []
    for img in pages:
        processed = preprocess_image(img)
        text = extract_text(processed)
        texts.append(text if text else "[내용 없음]")
    return "\n\n".join(texts)