FROM python:3.10.13

RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    ffmpeg

WORKDIR /classlog-ai

COPY requirements.txt /classlog-ai/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /classlog-ai/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]