import os
import tempfile
import subprocess
from PIL import Image
from typing import List
import pytesseract
from urllib.parse import urlparse
from io import BytesIO
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import requests
from docx2pdf import convert as convert_docx_to_pdf
from concurrent.futures import ThreadPoolExecutor

# 이미지 전처리: 회색조로 변환 후 이진화
def preprocess_image(img: Image.Image):
    gray = img.convert("L")
    bw = gray.point(lambda x: 0 if x < 150 else 255, '1')
    return bw

# OCR: 이미지에서 텍스트 추출
def extract_text_from_image(img: Image.Image):
    config = '--psm 6 -l kor+eng'
    return pytesseract.image_to_string(img, config=config).strip()

# S3 URL에서 쿼리 문자열 제거 (파일 확장자 추출용)
def remove_url_query(file_path: str) -> str:
    parsed_url = urlparse(file_path)
    return parsed_url.path

# PDF가 텍스트 기반인지 확인 (PyPDF2로 추출 가능한지 판단)
def is_text_based_pdf(pdf_bytes: bytes) -> bool:
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        for page in reader.pages:
            if page.extract_text().strip():
                return True
        return False
    except Exception:
        return False

# 텍스트 기반 PDF에서 텍스트 추출
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    texts = [page.extract_text().strip() for page in reader.pages if page.extract_text()]
    return "\n\n".join(texts)

# 이미지 기반 PDF에서 OCR로 텍스트 추출
def extract_text_from_pdf_images(pdf_bytes: bytes) -> str:
    images = convert_from_bytes(pdf_bytes, dpi=300)
    with ThreadPoolExecutor(max_workers=2) as executor:
        texts = list(executor.map(lambda img: extract_text_from_image(preprocess_image(img)), images))
    return "\n\n".join(texts)

# PDF가 아닌 문서(docx, pptx, hwpx, hwp)를 PDF로 변환하여 바이트로 반환
def convert_to_pdf(file_path: str) -> bytes:
    ext = os.path.splitext(remove_url_query(file_path))[1].lower()
    if ext == ".pdf":
        response = requests.get(file_path)
        response.raise_for_status()
        return response.content

    with tempfile.TemporaryDirectory() as tmpdir:
        local_path = os.path.join(tmpdir, f"input{ext}")
        with open(local_path, "wb") as f:
            f.write(requests.get(file_path).content)

        if ext == ".docx":
            convert_docx_to_pdf(local_path, tmpdir)
        else:
            subprocess.run([
                "libreoffice", "--headless", "--convert-to", "pdf",
                "--outdir", tmpdir, local_path
            ], check=True)

        converted_pdf_path = os.path.splitext(local_path)[0] + ".pdf"
        with open(converted_pdf_path, "rb") as f:
            return f.read()

# 문서 리스트를 입력 받아 텍스트로 변환하는 메인 함수
def process_any_documents(file_paths_str: str) -> str:
    file_paths = [url.strip() for url in file_paths_str.split(",") if url.strip()]
    all_texts = []

    for file_path in file_paths:
        try:
            pdf_bytes = convert_to_pdf(file_path)
            if is_text_based_pdf(pdf_bytes):
                text = extract_text_from_pdf(pdf_bytes)
            else:
                text = extract_text_from_pdf_images(pdf_bytes)
            all_texts.append(text or "[내용 없음]")
        except Exception as e:
            all_texts.append(f"[오류 발생: {file_path}]\n{str(e)}")

    return "\n\n".join(all_texts)
