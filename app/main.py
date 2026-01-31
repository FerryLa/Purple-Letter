"""
Purple Letter API Server
FastAPI-based intelligence server for news curation and newsletter generation
"""
import os
import sys
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from app.database import get_db, db_manager, NewsArticle, NewsRepository, SyncLog
from app.models import (
    NewsItem,
    NewsItemResponse,
    NewsListResponse,
    NewsletterResponse,
    DatasetResponse,
    SelectionRequest,
    SelectionResponse,
    HealthCheckResponse,
    SyncStatus,
    FilterParams,
)
from app.core_import import get_connector, NewsScannerCoreConnector
from app.transformer import transformer
from app.scorer import scorer
from app.ranker import ranker
from app.selector import get_selector


# Background sync status
_sync_status = SyncStatus()


def sync_from_core(db: Session) -> SyncStatus:
    """
    Synchronize data from news-scanner-core

    This function:
    1. Fetches articles from the core database
    2. Transforms them to structured format
    3. Calculates ImpactScores
    4. Stores in Purple Letter database
    """
    global _sync_status
    _sync_status = SyncStatus(last_sync=datetime.utcnow())

    try:
        connector = get_connector()
        raw_articles = connector.fetch_with_scores(limit=200)
        _sync_status.articles_synced = len(raw_articles)

        # Transform articles
        transformed = transformer.transform_batch(raw_articles)
        _sync_status.articles_transformed = len(transformed)

        # Score articles
        scored = scorer.score_batch(transformed)
        _sync_status.articles_scored = len(scored)

        # Save to database
        for article_data in scored:
            try:
                article = NewsArticle(
                    id=article_data["id"],
                    title=article_data["title"],
                    link=article_data["link"],
                    summary=article_data["summary"],
                    source=article_data["source"],
                    published_at=article_data["published_at"],
                    image_url=article_data.get("image_url"),
                    primary_sector=article_data.get("primary_sector"),
                    secondary_sector=article_data.get("secondary_sector"),
                    subcategories=article_data.get("subcategories", []),
                    market_relevance=article_data["market_relevance"],
                    business_relevance=article_data["business_relevance"],
                    tech_shift=article_data["tech_shift"],
                    urgency=article_data["urgency"],
                    impact_score=article_data["impact_score"],
                    strategic_tag=article_data["strategic_tag"],
                    original_score=article_data.get("original_score"),
                    matched_keywords=article_data.get("matched_keywords", []),
                    why_it_matters=article_data.get("why_it_matters"),
                    implication=article_data.get("implication"),
                )
                NewsRepository.upsert(db, article)
            except Exception as e:
                _sync_status.errors.append(f"Failed to save article: {str(e)}")

        # Log sync
        sync_log = SyncLog(
            sync_started=_sync_status.last_sync,
            sync_completed=datetime.utcnow(),
            articles_fetched=len(raw_articles),
            articles_new=len(scored),
            status="completed" if not _sync_status.errors else "partial",
            errors=_sync_status.errors,
        )
        db.add(sync_log)
        db.commit()

    except Exception as e:
        _sync_status.errors.append(str(e))

    return _sync_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize database
    db_manager.get_db()
    print("Database initialized")

    # Initial sync from news-scanner-core
    try:
        with db_manager.get_session() as db:
            status = sync_from_core(db)
            print(f"Initial sync completed: {status.articles_synced} articles")
    except Exception as e:
        print(f"Warning: Initial sync failed: {e}")

    yield

    # Shutdown
    print("Shutting down Purple Letter API")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligence API for news curation and newsletter generation",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper function to convert DB model to Pydantic model
def article_to_response(article: NewsArticle) -> NewsItem:
    """Convert SQLAlchemy model to Pydantic response model"""
    return NewsItem(
        id=article.id,
        title=article.title,
        link=article.link,
        summary=article.summary or "",
        source=article.source or "",
        published_at=article.published_at or datetime.utcnow(),
        date=article.published_at.strftime("%Y-%m-%d") if article.published_at else "",
        image_url=article.image_url,
        primary_sector=article.primary_sector,
        secondary_sector=article.secondary_sector,
        subcategories=article.subcategories or [],
        market_relevance=article.market_relevance,
        business_relevance=article.business_relevance,
        tech_shift=article.tech_shift,
        urgency=article.urgency,
        impact_score=article.impact_score,
        strategic_tag=article.strategic_tag,
        selected=article.selected,
        selected_at=article.selected_at,
        original_score=article.original_score,
        matched_keywords=article.matched_keywords or [],
        why_it_matters=article.why_it_matters,
        implication=article.implication,
    )


# ============== API Endpoints ==============


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        connector = get_connector()
        core_health = connector.check_health()
        core_connected = core_health.get("connected", False)
    except Exception:
        core_connected = False

    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        database_connected=True,
        news_scanner_connected=core_connected,
        last_sync=_sync_status.last_sync,
    )


# ============== News Endpoints ==============


@app.get("/news", response_model=NewsListResponse, tags=["News"])
async def get_all_news(
    min_score: Optional[int] = Query(None, ge=4, le=10, description="Minimum ImpactScore"),
    category: Optional[str] = Query(None, description="Filter by sector/category"),
    sector: Optional[str] = Query(None, description="Filter by primary sector"),
    limit: int = Query(50, ge=1, le=200, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
):
    """
    Get all news articles with optional filters

    Supports filtering by:
    - min_score: Minimum ImpactScore (4-10)
    - category: Sector category
    - limit: Results per page
    - offset: Pagination offset
    """
    articles = NewsRepository.get_all(
        db,
        min_score=min_score,
        category=category,
        sector=sector,
        limit=limit,
        offset=offset,
    )

    return NewsListResponse(
        success=True,
        total=len(articles),
        data=[article_to_response(a) for a in articles],
    )


@app.get("/news/recommended", response_model=NewsListResponse, tags=["News"])
async def get_recommended_news(
    top_n: int = Query(4, ge=1, le=10, description="Number of recommendations"),
    db: Session = Depends(get_db),
):
    """
    Get top N recommended articles by ImpactScore

    Returns unselected articles sorted by impact score.
    Default returns top 4 for newsletter inclusion.
    """
    articles = NewsRepository.get_recommended(db, top_n=top_n)

    return NewsListResponse(
        success=True,
        total=len(articles),
        data=[article_to_response(a) for a in articles],
    )


@app.get("/news/{news_id}", response_model=NewsItemResponse, tags=["News"])
async def get_news_by_id(
    news_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific news article by ID"""
    article = NewsRepository.get_by_id(db, news_id)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return NewsItemResponse(
        success=True,
        data=article_to_response(article),
    )


# ============== Selection Endpoints ==============


@app.post("/news/select/{news_id}", response_model=SelectionResponse, tags=["Selection"])
async def select_news(
    news_id: str,
    db: Session = Depends(get_db),
):
    """
    Select an article for newsletter inclusion

    Marks the article as selected for the current newsletter edition.
    """
    selector = get_selector(db)
    article = selector.select_article(news_id)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return SelectionResponse(
        success=True,
        selected_count=1,
        message=f"Article '{article.title[:50]}...' selected for newsletter",
    )


@app.post("/news/select", response_model=SelectionResponse, tags=["Selection"])
async def select_multiple_news(
    request: SelectionRequest,
    db: Session = Depends(get_db),
):
    """
    Select multiple articles for newsletter

    Accepts a list of article IDs to select.
    """
    selector = get_selector(db)
    result = selector.select_multiple(request.news_ids)

    return SelectionResponse(
        success=result["selected_count"] > 0,
        selected_count=result["selected_count"],
        message=f"Selected {result['selected_count']} articles. Errors: {len(result['errors'])}",
    )


@app.delete("/news/select/{news_id}", response_model=SelectionResponse, tags=["Selection"])
async def deselect_news(
    news_id: str,
    db: Session = Depends(get_db),
):
    """Remove an article from newsletter selection"""
    selector = get_selector(db)
    article = selector.deselect_article(news_id)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return SelectionResponse(
        success=True,
        selected_count=0,
        message=f"Article deselected from newsletter",
    )


@app.delete("/news/select", response_model=SelectionResponse, tags=["Selection"])
async def clear_all_selections(db: Session = Depends(get_db)):
    """Clear all current newsletter selections"""
    selector = get_selector(db)
    count = selector.clear_all_selections()

    return SelectionResponse(
        success=True,
        selected_count=0,
        message=f"Cleared {count} selections",
    )


# ============== Newsletter Endpoints ==============


@app.get("/newsletter", response_model=NewsletterResponse, tags=["Newsletter"])
async def get_newsletter(db: Session = Depends(get_db)):
    """
    Get selected articles for newsletter

    Returns only articles that have been manually selected.
    This is the endpoint for newsletter generation.
    """
    articles = NewsRepository.get_selected(db)

    return NewsletterResponse(
        success=True,
        selected_count=len(articles),
        newsletter_date=datetime.utcnow().strftime("%Y-%m-%d"),
        data=[article_to_response(a) for a in articles],
    )


@app.get("/newsletter/preview", tags=["Newsletter"])
async def get_newsletter_preview(db: Session = Depends(get_db)):
    """Get newsletter preview with validation"""
    selector = get_selector(db)
    preview = selector.get_newsletter_preview()
    validation = selector.validate_selection()

    return {
        "preview": preview,
        "validation": validation,
    }


# ============== Power BI Dataset Endpoint ==============


@app.get("/dataset", response_model=DatasetResponse, tags=["Dataset"])
async def get_dataset(
    limit: int = Query(500, ge=1, le=1000, description="Maximum records"),
    db: Session = Depends(get_db),
):
    """
    Get full dataset for Power BI integration

    Returns all articles with scores for direct Power BI connection.
    Use URL: https://your-server.com/dataset

    Power BI setup:
    1. Get Data → Web
    2. Enter this endpoint URL
    3. Transform JSON data as needed
    """
    articles = NewsRepository.get_all(db, limit=limit)

    return DatasetResponse(
        success=True,
        last_updated=datetime.utcnow(),
        total_records=len(articles),
        data=[article_to_response(a) for a in articles],
    )


# ============== Sync Endpoints ==============


@app.post("/sync", tags=["System"])
async def trigger_sync(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Trigger synchronization from news-scanner-core

    Fetches latest articles from the core database,
    transforms, scores, and stores them.
    """
    status = sync_from_core(db)

    return {
        "success": len(status.errors) == 0,
        "message": f"Synced {status.articles_synced} articles",
        "details": {
            "articles_synced": status.articles_synced,
            "articles_transformed": status.articles_transformed,
            "articles_scored": status.articles_scored,
            "errors": status.errors,
        },
    }


@app.get("/sync/status", response_model=SyncStatus, tags=["System"])
async def get_sync_status():
    """Get the status of the last synchronization"""
    return _sync_status


# ============== Analytics Endpoints ==============


@app.get("/analytics/sectors", tags=["Analytics"])
async def get_sector_analytics(db: Session = Depends(get_db)):
    """Get article distribution by sector"""
    articles = NewsRepository.get_all(db, limit=500)
    distribution = ranker.get_sector_distribution(
        [{"primary_sector": a.primary_sector} for a in articles]
    )

    return {
        "total_articles": len(articles),
        "sector_distribution": distribution,
    }


@app.get("/analytics/scores", tags=["Analytics"])
async def get_score_analytics(db: Session = Depends(get_db)):
    """Get article distribution by ImpactScore"""
    articles = NewsRepository.get_all(db, limit=500)
    distribution = ranker.get_score_distribution(
        [{"impact_score": a.impact_score} for a in articles]
    )

    return {
        "total_articles": len(articles),
        "score_distribution": distribution,
    }


@app.get("/analytics/tags", tags=["Analytics"])
async def get_strategic_tag_analytics(db: Session = Depends(get_db)):
    """Get article distribution by strategic tag"""
    articles = NewsRepository.get_all(db, limit=500)
    distribution = ranker.get_strategic_tag_distribution(
        [{"strategic_tag": a.strategic_tag} for a in articles]
    )

    return {
        "total_articles": len(articles),
        "tag_distribution": distribution,
    }


# ============== Run Server ==============

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
