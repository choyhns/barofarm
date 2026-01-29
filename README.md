# Barofarm

## 프로젝트 소개
Barofarm은 농산물 직거래와 가격 예측을 지원하는 참여형 플랫폼입니다.
사용자는 생산자 게시글을 통해 상품을 구매하고, 일별 가격 정보와 ML 기반 가격 예측을 활용할 수 있습니다.
본 프로젝트는 팀 프로젝트로 진행되었으며,
저는 인증·온보딩, 마이페이지, 판매자 등록·판매자 페이지 및 전체 ERD 설계를 담당했습니다.

## 기술 스택

### Backend
- Spring Boot 2.7.7
- Spring Security
- Spring Data JPA
- OAuth2 Client (Google / Kakao / Naver)
- JWT

### Frontend
- React 19
- Material UI
- HTML/CSS/JavaScript

### Database
- Oracle DB

### ML / 예측
- Python, Flask
- LightGBM, XGBoost, scikit-learn (일별 가격 예측 API)

### Server/Tool
- Apache Tomcat (Embedded)
- Gradle
- Git / Github
- AWS S3, Solapi SMS, Portone 결제, KAMIS API

## 프로젝트 구성
### 프로젝트 유형: 팀 프로젝트
### 개발 인원: 5명
### 개발 기간: 20일
### 담당 역할
- 인증: 로그인 / 회원가입 / 계정 찾기
- 마이페이지: 배송지 / 개인정보 관리
- 판매자 등록(온보딩)
- 판매자 페이지(대시보드 / 관리 화면)
- 전체 ERD 설계

## 담당 기능 상세

### 인증: 로그인 / 회원가입 / 계정 찾기
- 서비스 기본 진입을 위한 인증·온보딩 흐름 구성
- 로그인, 회원가입, 계정 찾기(복구) 화면 및 API 연동
- 계정 복구 화면까지 포함해 사용자 접근성을 높였습니다.

### 마이페이지: 배송지 / 개인정보 관리
- 배송지 관리(추가 / 수정) 및 개인정보 수정 기능 제공
- 사용자 계정 관리 UX를 구성했습니다.

### 판매자 등록(온보딩)
- 약관 동의 및 판매자 등록 신청 흐름 구성
- 일반 사용자에서 판매자로 확장되는 구조를 마련했습니다.

### 판매자 페이지(대시보드 / 관리 화면)
- 판매자 대시보드 및 판매자 관리 화면의 구조 구성
- 판매자 운영 경험을 제공했습니다.

### 전체 ERD 설계
- 프로젝트 전반의 엔티티 관계 및 DB 스키마 설계를 담당했습니다.

## DB 설정 구조(보안 분리)
DB 접속 정보는 보안 및 환경 분리를 위해 Git에 직접 포함하지 않았습니다.

### 설정 방식
- application.properties -> Git 제외
- application.yml -> Git 제외
- application.properties.example -> Git에 포함
- application.yml.example -> Git에 포함

### application.properties.example (주요 항목)
- spring.datasource.driver-class-name=oracle.jdbc.driver.OracleDriver
- spring.datasource.url=jdbc:oracle:thin:@localhost:1521/XEPDB1
- spring.datasource.username=YOUR_DB_USERNAME
- spring.datasource.password=YOUR_DB_PASSWORD  
(그 외 OAuth client-id/secret, jwt.secret, naver API 등은 예시 파일 참고)

## 실행 방법

### 환경
- JDK 8 이상
- Node.js (npm)
- Oracle DB
- (선택) Python 3 — ML 예측 API 사용 시

### DB 설정
- barofarm/src/main/resources/application.properties.example  
  -> application.properties 로 복사 후 DB 계정 및 OAuth/API 정보 입력

### 실행

**백엔드**
- barofarm 폴더에서 `.\gradlew bootRun`
- API 서버: http://localhost:8080

**프론트엔드**
- client 폴더에서 `npm install` 후 `npm run start`
- 브라우저 접속: http://localhost:3000 (기본 포트)
- ※ `npm run dev` 스크립트는 없으며, `npm run start` 사용

**ML 예측 API (선택)**
- python 폴더에서 가상환경 설정 후 `pip install -r requirements.txt` (또는 필요 패키지 설치)
- `python app.py` 실행 후 예측 API 사용

## 프로젝트를 통해 얻은 점
- Spring Security + OAuth2 + JWT 기반 인증·온보딩 흐름 설계 경험
- 사용자·판매자 역할 확장을 고려한 온보딩 및 권한 구조 설계
- 전체 ERD 설계를 통한 도메인·테이블 관계 정리 경험
- 배송지·개인정보 등 계정 관리 UX 설계 및 구현 경험
- 팀 프로젝트에서 인증·마이페이지·판매자 영역 책임 구현 경험

## 참고
본 프로젝트는 학습 및 포트폴리오 목적의 팀 프로젝트이며, 실제 서비스 흐름을 고려한 구조로 구현되었습니다.
