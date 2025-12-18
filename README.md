<div align="center">

# 전주대학교 파이썬 기초 및 실습 기말 팀프로젝트
# 🎓 3중 학사관리시스템 
**Python / JSON Based Academic Platform** 

![js](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![js](https://img.shields.io/badge/JSON-3776AB?style=flat&logo=json&logoColor=white) 
      
</div>

---
# 👥 Team 와해(渦解) 소개
**구성원 : 나지수 임지후 정종빈 김재영 송제용 장현준 최혁**

---
# 📌 프로젝트 개요

본 프로젝트는 **학생(Student)**, **교수(Professor)**, **행정직원(Admin)**  
세 가지 역할을 기반으로 각각 다른 기능을 제공하는 **학사관리 시스템**입니다.

Python + JSON 데이터 구조를 활용하여  
동작하는 **학사관리 시스템**을 구현했습니다.

---
# 🧩 개발 목적

- 역할별로 다른 학사 기능을 제공하는 통합 시스템 제작  
- JSON 데이터를 통한 경량 스토리지 구조 실습  
- Python OOP 클래스 구조 기반 설계 능력 향상  
- 실제 학사관리 기능을 단순화하여 콘솔 기반으로 모델링  

---
# 🗂️ 시스템 주요 기능 및 구

## 👨‍🎓 **학생(Student) 기능**
- 수강신청 / 수강취소  
- 시간표 조회  
- 성적 조회  
- 공지사항 열람  
- 내 정보 수정  

## 👨‍🏫 **교수(Professor) 기능**
- 담당 강의 목록 조회  
- 수강생 명단 확인  
- 성적 입력  
- 공지사항 등록  

## 🧑‍💼 **행정직원(Admin) 기능**
- 강의 개설 / 삭제  
- 전체 사용자 조회  
- 기본 시스템 데이터 관리

## 🏗️ 시스템 구조

```plaintext
academic_system/
│
├── main.py
├── data.py
│
├── user_base.py
├── student.py
├── professor.py
├── admin.py
│
├── unified_users.json
└── login_users.json
```
---

# 🔍 개발 진행 과정 (4주차 팀 활동 기록)

## 📅 1주차 – 요구사항 분석 / 구조 설계 (1022~1029)

역할별 기능 정의(Student/Professor/Admin)

JSON 기반 저장 구조 확정

UML 개념 스케치 작성

팀 역할 분담 및 GitHub 초기 세팅

## 📅 2주차 – 클래스 · JSON 구조 설계(1030~1105)

User → Student / Professor / Admin 상속 구조 완성

unified_users.json 설계

student.py, professor.py, admin.py 기본 코드 작성

## 📅 3주차 – 기능 구현 및 통합(1106~1112)

로그인 기능 완성

JSON → 객체 자동 생성 로직 구현

학생/교수/행정직원 메뉴 기능 70% 개발 완료

수강신청, 공지등록 등 핵심 기능 작동 확인

## 📅 4주차 – 중간발표(1113~1121)

JSON 기반 전체 로직 검증 완료

SD UML 다이어그램 제작

README(과제 제출용) 정리

PPT 발표자료 및 시연 흐름 정리

## 📅 5주차 기능 수정 및 통합(1122~1130)
Json 기반 파일 수정

필요없는 기능 삭제 및 새로운 기능 추가

예외처리 
 
## 📅 6주차 Tkinter기반 GUI로 UI 구현(1201~1210)
Tkinter라이브러리 사용 UI 구현

pyinstaller로 Exe 파일로 실행

아이콘 및 사진변경

## 📅 7,8주차 기말프로젝트 종료 (1211~1219)

---

# 🌐 웹 버전 (Flask 기반)

기존 콘솔 기반 시스템을 웹 애플리케이션으로 확장했습니다!

## 🚀 웹 버전 실행 방법

```bash
# 1. web_app 디렉토리로 이동
cd web_app

# 2. 필요한 패키지 설치
pip install -r requirements.txt

# 3. Flask 애플리케이션 실행
python app.py

# 4. 브라우저에서 접속
# http://localhost:5000
```

## 🔐 테스트 계정

- **학생**: `student1` / `1234`
- **교수**: `prof1` / `1234`
- **관리자**: `admin1` / `1234`

## ✨ 웹 버전 주요 기능

### 👨‍🎓 학생
- 수강 신청/취소 (시간 충돌 감지)
- 시간표 조회
- 성적 조회 (GPA 자동 계산)
- 공지사항 확인

### 👨‍🏫 교수
- 담당 강좌 관리
- 수강생 명단 확인
- 성적 입력/수정

### 🧑‍💼 관리자
- 강좌 개설/삭제
- 사용자 계정 관리 (추가/삭제/비밀번호 초기화)
- 공지사항 관리
- 학적 변동 신청 처리

## 🛠️ 기술 스택

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **Data Storage**: JSON 파일
- **Session Management**: Flask Session

---

## 성능 · 테스트(시간부족으로 인해 미진행)

프로젝트 특성상 다음처럼 테스트 가능:

JSON 로딩 시간 측정

메뉴 기능 반복 호출 테스트

공지사항/수강신청 대량 생성 스트레스 테스트

(프로그램 완성 후 시간이 남을시 테스트 해볼 예정)

<div align="center">

# 감사합니다.

</div> 

```

