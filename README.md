# Purple Letter 🟣

**Intelligence API Server for News Curation and Newsletter Generation**

Purple Letter는 news-scanner-core의 래퍼로, 뉴스 데이터를 구조화하고 점수화하여 전략적 인사이트를 제공하는 FastAPI 기반 API 서버입니다.

## 🎯 핵심 원칙

1. **뉴스는 자동으로 "완성"되지 않는다**
   - 시스템이 Top 4 추천
   - 사람이 최종 선택
   - 선택된 뉴스만 Newsletter로 Export

2. **API 중심 설계**
   - JSON 기반 응답
   - Power BI direct query 가능
   - React 대시보드 확장 가능

## 📐 아키텍처

```
                ┌─────────────────────┐
                │ news-scanner-core   │
                │  (RSS/API ingest)   │
                └─────────────┬───────┘
                              │ raw articles
                              ▼
                ┌─────────────────────┐
                │ Purple Letter API   │
                │  (FastAPI)          │
                │  - transform        │
                │  - scoring          │
                │  - ranking          │
                │  - selection state  │
                └─────────────┬───────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
  Admin Selection UI      Power BI Dataset     Mobile Newsletter
  (뉴스 선별)              (자동 연결)           (최종 출력)
```

## 📁 프로젝트 구조

```
purple-letter/
│
├── app/
│   ├── main.py            # FastAPI entry point
│   ├── core_import.py     # news-scanner-core 연결
│   ├── transformer.py     # 데이터 변환
│   ├── scorer.py          # ImpactScore 계산
│   ├── ranker.py          # 순위 결정
│   ├── selector.py        # 수동 선택 로직
│   ├── models.py          # Pydantic models
│   └── database.py        # SQLAlchemy ORM
│
├── data/                   # SQLite 데이터베이스
│
├── config/
│   └── settings.py        # 설정 관리
│
├── requirements.txt
└── README.md
```

## 🚀 시작하기

### 1. 설치

```bash
cd Purple-Letter
pip install -r requirements.txt
```

### 2. 환경 설정

```bash
cp .env.example .env
# .env 파일에서 NEWS_SCANNER_CORE_PATH 설정
```

### 3. 서버 실행

```bash
# 개발 모드
uvicorn app.main:app --reload --port 8000

# 또는 직접 실행
python -m app.main
```

### 4. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

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
| `/newsletter/preview` | GET | 뉴스레터 미리보기 + 검증 |

### 데이터셋 (Power BI)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dataset` | GET | Power BI용 전체 데이터셋 |

### 시스템

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | 헬스체크 |
| `/sync` | POST | 데이터 동기화 트리거 |
| `/sync/status` | GET | 동기화 상태 조회 |

## 📊 ImpactScore 계산

```
ImpactScore = MarketRelevance + BusinessRelevance + TechShift + Urgency

- MarketRelevance (1-3): 금융시장 관련성
- BusinessRelevance (1-3): 비즈니스 의사결정 관련성
- TechShift (1-2): 기술/혁신 영향도
- Urgency (1-2): 시간 민감도

Total: 4-10점
```

## 🔌 Power BI 연결

### Option A: Web API 직접 연결

1. Power BI Desktop 열기
2. Get Data → Web 선택
3. URL 입력: `https://your-server.com/dataset`
4. JSON 데이터 변환

### Option B: 자동 새로고침 설정

1. Power BI Service에서 데이터셋 선택
2. Settings → Scheduled Refresh
3. 새로고침 간격 설정 (최소 30분)

## 🔧 Strategic Tags

| Tag | Description |
|-----|-------------|
| `opportunity` | 투자/사업 기회 |
| `risk` | 리스크 요인 |
| `trend` | 시장 트렌드 |
| `policy` | 정책/규제 변화 |
| `breaking` | 속보 |
| `exclusive` | 단독 뉴스 |
| `neutral` | 일반 뉴스 |

## 🛠 개발 환경

### 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite + SQLAlchemy
- **Validation**: Pydantic v2
- **Server**: Uvicorn

### Production 권장 스택

- PostgreSQL (대용량 처리)
- Redis (캐싱)
- Nginx (리버스 프록시)
- Docker Compose

## 📝 사용 예시

### 추천 뉴스 조회

```bash
curl http://localhost:8000/news/recommended?top_n=4
```

### 뉴스 선택

```bash
curl -X POST http://localhost:8000/news/select/article_123
```

### 선택된 뉴스 조회 (뉴스레터용)

```bash
curl http://localhost:8000/newsletter
```

### Power BI 데이터셋

```bash
curl http://localhost:8000/dataset?limit=500
```

## 📄 License

MIT License

---

Built with ❤️ for strategic intelligence
