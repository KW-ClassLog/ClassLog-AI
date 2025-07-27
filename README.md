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
📦classlog-ai
 ┣ 📁src
 ┃ ┣ 📁prompts         # 프롬프트 템플릿 정의
 ┃ ┣ 📁generator       # 퀴즈 생성 로직
 ┃ ┣ 📁validator       # 퀴즈 품질 필터링 및 검수
 ┃ ┗ 📁utils           # 유틸리티 함수
 ┣ 📄main.py           # 진입점
 ┣ 📄requirements.txt  # Python 의존성 목록
 ┗ 📄README.md

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
