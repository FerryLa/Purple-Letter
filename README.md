# Purple Letter

**News-Leafletter 모듈형 인텔리전스 API**

Purple Letter는 뉴스 스캐너 [News-Leafletter](https://github.com/FerryLa/News-Leafletter)의 모듈형 확장으로, 수집된 뉴스 데이터를 분석하여 ImpactScore를 산출하고 이커머스 동향 중심의 전략 브리핑을 제공합니다.

> Purple Letter의 ImpactScore는 RSS 뉴스 데이터 기반의 참고용 지표이며, 최종 뉴스레터 구성은 사용자 판단에 따릅니다. 본 프로젝트는 Claude를 활용하여 개발되었습니다.

---

## 개요

### 목적
사내 간식 공간에서 3분 만에 핵심 이커머스 동향을 파악하는 전략 브리핑 시스템

### 핵심 원칙
**Human-in-the-loop**: AI가 추천하고, 사람이 최종 결정

1. 시스템이 ImpactScore 기반 Top 4 추천
2. 사람이 Admin UI에서 최종 선택
3. 선택된 뉴스만 Newsletter로 Export

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│              News-Leafletter (뉴스 스캐너)                        │
│                                                                 │
│     RSS 피드 + 뉴스 API  →  수집  →  SQLite DB                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │ 읽기 전용 연결
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Purple Letter (인텔리전스 API)                       │
│                                                                 │
│   데이터 변환  →  ImpactScore 산출  →  랭킹  →  선택 관리           │
│   transformer       scorer          ranker     selector         │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API (JSON)
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
     Admin UI            Power BI          Newsletter
   (React + TS)          (데이터셋)          (최종 출력)
```

### 모듈 관계

| 프로젝트 | 역할 | 데이터 흐름 |
|---------|------|------------|
| News-Leafletter | RSS/API 뉴스 수집 및 저장 | 원본 데이터 생성 |
| Purple Letter | 분석, 스코어링, 큐레이션 | 읽기 전용으로 데이터 소비 |

---

## ImpactScore 계산

키워드 기반 5가지 요소의 합산으로 4~12점 범위 산출:

```
ImpactScore = MarketRelevance + BusinessRelevance + TechShift + Urgency + EcommerceRelevance
```

| 요소 | 범위 | 설명 | 키워드 예시 |
|------|------|------|------------|
| MarketRelevance | 1-3 | 금융시장 관련성 | 증시, 코스피, 환율, 금리 |
| BusinessRelevance | 1-3 | 비즈니스 영향도 | 실적, M&A, 매출, 계약 |
| TechShift | 1-2 | 기술/혁신 관련성 | AI, 반도체, 전기차 |
| Urgency | 1-2 | 긴급성 | [속보], [단독], BREAKING |
| EcommerceRelevance | 0-2 | 이커머스 관련성 | 쿠팡, 네이버쇼핑, 새벽배송 |

### 이커머스 키워드 (64개)

**플랫폼**: 쿠팡, 네이버쇼핑, 11번가, G마켓, 옥션, 위메프, 티몬, SSG닷컴, 롯데온, 마켓컬리, 무신사, 배달의민족, 아마존, 알리익스프레스, 테무 등

**용어**: 이커머스, 온라인쇼핑, 오픈마켓, 라이브커머스, 퀵커머스, 새벽배송, 로켓배송, 풀필먼트, D2C, 리테일테크

**결제**: 네이버페이, 카카오페이, 토스, 간편결제, BNPL

**물류**: 물류, 배송, 택배, CJ대한통운, 마켓플레이스

---

## Strategic Tags

| Tag | 설명 |
|-----|------|
| `breaking` | 속보 |
| `exclusive` | 단독 |
| `opportunity` | 투자/사업 기회 |
| `risk` | 리스크 요인 |
| `trend` | 트렌드 변화 |
| `policy` | 정책/규제 |
| `neutral` | 일반 뉴스 |

---

## 프로젝트 구조

```
purple-letter/
├── app/
│   ├── main.py            # FastAPI 엔트리포인트
│   ├── core_import.py     # News-Leafletter DB 연결
│   ├── transformer.py     # 데이터 변환
│   ├── scorer.py          # ImpactScore 계산 (이커머스 필터 포함)
│   ├── ranker.py          # 순위 결정
│   ├── selector.py        # 수동 선택 로직
│   ├── models.py          # Pydantic 모델
│   └── database.py        # SQLAlchemy ORM
│
├── admin-ui/              # React Admin 대시보드
│   ├── src/
│   │   ├── components/    # UI 컴포넌트
│   │   ├── hooks/         # TanStack Query 훅
│   │   ├── pages/         # 페이지 컴포넌트
│   │   └── types/         # TypeScript 타입
│   └── package.json
│
├── config/
│   └── settings.py        # 환경 설정
│
├── data/                  # SQLite 데이터베이스
├── .env.example           # 환경변수 템플릿
└── requirements.txt
```

---

## 시작하기

### 1. 사전 요구사항

- Python 3.9+
- Node.js 18+
- News-Leafletter 프로젝트 (뉴스 데이터 소스)

### 2. 설치

```bash
cd Purple-Letter

# Python 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 설정

```bash
cp .env.example .env
```

`.env` 파일 수정:
```env
# News-Leafletter 연결 설정 (필수)
NEWS_SCANNER_CORE_PATH=C:/dev/News-Leafletter
NEWS_SCANNER_DB_PATH=C:/dev/News-Leafletter/data/news_leafletter.db

# CORS 설정 (JSON 배열 형식)
CORS_ORIGINS=["*"]
```

### 4. API 서버 실행

```bash
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Admin UI 실행

```bash
cd admin-ui
npm install
npm run dev
```

- Admin UI: http://localhost:3000

---

## API Endpoints

### 뉴스 조회

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/news` | GET | 전체 뉴스 조회 (필터 지원) |
| `/news/recommended` | GET | 추천 뉴스 Top N |
| `/news/{news_id}` | GET | 개별 뉴스 조회 |

### 뉴스 선택

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/news/select/{news_id}` | POST | 뉴스 선택 |
| `/news/select` | POST | 복수 뉴스 선택 |
| `/news/select/{news_id}` | DELETE | 선택 해제 |
| `/news/select` | DELETE | 전체 선택 초기화 |

### 뉴스레터

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/newsletter` | GET | 선택된 뉴스 조회 |
| `/newsletter/preview` | GET | 미리보기 + 검증 |

### 분석

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analytics/sectors` | GET | 섹터별 분포 |
| `/analytics/scores` | GET | 점수별 분포 |
| `/analytics/tags` | GET | 태그별 분포 |

### 시스템

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | 헬스체크 |
| `/sync` | POST | 데이터 동기화 |
| `/dataset` | GET | Power BI용 데이터셋 |

---

## Admin UI 화면

### Dashboard
- 추천 뉴스 Top 4 표시 (이커머스 우선)
- 전체 통계 (기사 수, 선택 수, 평균 점수)
- 동기화 상태 및 Sync 버튼

### News List
- 전체 뉴스 테이블
- 필터: 최소 점수, 섹터
- 체크박스로 선택/해제

### Newsletter
- 선택된 기사 목록
- 검증 상태 (경고/권장사항)
- 섹터 커버리지 시각화

### Analytics
- 섹터별 분포 (파이 차트)
- ImpactScore 분포 (막대 차트)
- Strategic Tag 분석

---

## Power BI 연결

1. Power BI Desktop > Get Data > Web
2. URL 입력: `http://localhost:8000/dataset`
3. JSON 데이터 변환 및 시각화

---

## 기술 스택

### Backend
- Framework: FastAPI
- Database: SQLite + SQLAlchemy
- Validation: Pydantic v2

### Frontend (Admin UI)
- Framework: React 18 + TypeScript
- Build: Vite
- Styling: Tailwind CSS
- State: TanStack Query
- Charts: Recharts

### Production 권장
- PostgreSQL (대용량 처리)
- Redis (캐싱)
- Nginx (리버스 프록시)
- Docker Compose

---

## 사용 예시

```bash
# 추천 뉴스 조회
curl http://localhost:8000/news/recommended?top_n=4

# 뉴스 선택
curl -X POST http://localhost:8000/news/select/article_123

# 선택된 뉴스 조회
curl http://localhost:8000/newsletter

# 데이터 동기화
curl -X POST http://localhost:8000/sync
```

---

## License

MIT License

---

Built with Claude for strategic intelligence
