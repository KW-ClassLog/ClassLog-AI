<div align="center">

  <h2>ClassLog-AI | 클래스로그 인공지능 모듈</h2>
  <h3>퀴즈 자동 생성부터 학습 데이터 분석까지, AI로 더 스마트하게 🤖</h3>
  <b>2025.03.19 ~ 개발중✨</b>

</div>

<br />

## 🧠 프로젝트 개요

**ClassLog-AI**는 메인 프로젝트인 [ClassLog](([https://github.com/KW-ClassLog/ClassLog]))에서 **퀴즈 자동 생성**, **학생 이해도 분석**, **데이터 기반 피드백 제공** 등의 AI 기반 기능을 담당하는 서브 레포입니다.  
이 레포는 GPT 기반 자연어 처리 기능을 중심으로 하며, 학습 데이터를 분석하고, 맞춤형 퀴즈를 생성해 교육 효과를 극대화하는 데 목적이 있습니다.

<br />

## 🎯 주요 기능

> ✅ GPT 기반 퀴즈 생성 (객관식, OX, 주관식 등 다양한 형식)  
> ✅ 퀴즈 답변 분석

<br />

## 🧩 프로젝트 구조
```bash
📦CLASSLOG-AI
 ┣ 📁app
 ┃ ┣ 📁api                   # API 엔드포인트
 ┃ ┃ ┗ 📄quiz_api.py
 ┃ ┣ 📁core                  # 핵심 로직
 ┃ ┃ ┗ 📄memory.py
 ┃ ┣ 📁pipeline              # 퀴즈 생성 파이프라인
 ┃ ┃ ┗ 📄pipeline.py
 ┃ ┣ 📁service               # 외부 서비스 연동 (OCR, Whisper 등)
 ┃ ┃ ┣ 📄ocr_service.py
 ┃ ┃ ┣ 📄quiz_generator_service.py
 ┃ ┃ ┗ 📄whisper_service.py
 ┃ ┗ 📁utils                 # 유틸리티 함수
 ┃   ┗ 📄parse_utils.py
 ┣ 📁multi_agent             # 멀티 에이전트 관련 로직
 ┣ 📄main.py                 # 애플리케이션 진입점
 ┣ 📄requirements.txt        # 의존성 목록
 ┗ 📄README.md               # 프로젝트 설명서

```

## 🛠️ 설치 및 실행 가이드

1. 사용 패키지 다운
```bash
pip install -r requirements.txt
```
2. 서버 빌드 및 실행
```bash
uvicorn main:app --reload
```
