"""
Purple Letter Database Module
SQLAlchemy ORM with SQLite backend
"""
import os
import sys
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool

# Add config to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

Base = declarative_base()


class NewsArticle(Base):
    """SQLAlchemy model for news articles"""

    __tablename__ = "news_articles"

    id = Column(String(255), primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    link = Column(String(1000), nullable=False, unique=True)
    summary = Column(Text)
    source = Column(String(100))
    published_at = Column(DateTime, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Sector classification
    primary_sector = Column(String(50))
    secondary_sector = Column(String(50))
    subcategories = Column(JSON, default=list)

    # Image
    image_url = Column(String(1000))

    # ImpactScore components
    market_relevance = Column(Integer, default=1)  # 1-3
    business_relevance = Column(Integer, default=1)  # 1-3
    tech_shift = Column(Integer, default=1)  # 1-2
    urgency = Column(Integer, default=1)  # 1-2
    impact_score = Column(Integer, default=4, index=True)  # 4-10

    # Strategic classification
    strategic_tag = Column(String(50), default="neutral")

    # Selection state
    selected = Column(Boolean, default=False, index=True)
    selected_at = Column(DateTime, nullable=True)

    # Original data from news-scanner-core
    original_score = Column(Integer, nullable=True)
    matched_keywords = Column(JSON, default=list)

    # Analysis
    why_it_matters = Column(Text)
    implication = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_published_at_desc", published_at.desc()),
        Index("idx_impact_score_desc", impact_score.desc()),
        Index("idx_selected_published", selected, published_at.desc()),
    )


class SelectionHistory(Base):
    """History of newsletter selections"""

    __tablename__ = "selection_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    newsletter_date = Column(String(10), index=True)  # YYYY-MM-DD
    article_id = Column(String(255), index=True)
    selected_at = Column(DateTime, default=datetime.utcnow)
    selected_by = Column(String(100), default="admin")


class SyncLog(Base):
    """Log of synchronization with news-scanner-core"""

    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_started = Column(DateTime, default=datetime.utcnow)
    sync_completed = Column(DateTime)
    articles_fetched = Column(Integer, default=0)
    articles_new = Column(Integer, default=0)
    articles_updated = Column(Integer, default=0)
    errors = Column(JSON, default=list)
    status = Column(String(20), default="running")


class DatabaseManager:
    """Database connection and session management"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Ensure data directory exists
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

        # Create engine with SQLite optimizations
        self.engine = create_engine(
            settings.DATABASE_URL,
            connect_args={
                "check_same_thread": False,
            },
            poolclass=StaticPool,
            echo=settings.DEBUG,
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Create tables
        Base.metadata.create_all(bind=self.engine)

        self._initialized = True

    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_db(self) -> Session:
        """Get database session (for FastAPI dependency injection)"""
        return self.SessionLocal()


# Singleton instance
db_manager = DatabaseManager()


def get_db():
    """FastAPI dependency for database session"""
    db = db_manager.get_db()
    try:
        yield db
    finally:
        db.close()


# Repository functions
class NewsRepository:
    """Repository pattern for news article operations"""

    @staticmethod
    def get_all(
        db: Session,
        min_score: Optional[int] = None,
        category: Optional[str] = None,
        sector: Optional[str] = None,
        selected_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NewsArticle]:
        """Get all news articles with optional filters"""
        query = db.query(NewsArticle)

        if min_score is not None:
            query = query.filter(NewsArticle.impact_score >= min_score)
        if category:
            query = query.filter(
                (NewsArticle.primary_sector == category)
                | (NewsArticle.secondary_sector == category)
            )
        if sector:
            query = query.filter(NewsArticle.primary_sector == sector)
        if selected_only:
            query = query.filter(NewsArticle.selected == True)

        return (
            query.order_by(NewsArticle.impact_score.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, article_id: str) -> Optional[NewsArticle]:
        """Get article by ID"""
        return db.query(NewsArticle).filter(NewsArticle.id == article_id).first()

    @staticmethod
    def get_recommended(db: Session, top_n: int = 4) -> List[NewsArticle]:
        """Get top N recommended articles by impact score"""
        return (
            db.query(NewsArticle)
            .filter(NewsArticle.selected == False)
            .order_by(NewsArticle.impact_score.desc())
            .limit(top_n)
            .all()
        )

    @staticmethod
    def get_selected(db: Session) -> List[NewsArticle]:
        """Get all selected articles for newsletter"""
        return (
            db.query(NewsArticle)
            .filter(NewsArticle.selected == True)
            .order_by(NewsArticle.impact_score.desc())
            .all()
        )

    @staticmethod
    def select_article(db: Session, article_id: str) -> Optional[NewsArticle]:
        """Select an article for newsletter"""
        article = NewsRepository.get_by_id(db, article_id)
        if article:
            article.selected = True
            article.selected_at = datetime.utcnow()
            db.commit()
            db.refresh(article)
        return article

    @staticmethod
    def deselect_article(db: Session, article_id: str) -> Optional[NewsArticle]:
        """Deselect an article"""
        article = NewsRepository.get_by_id(db, article_id)
        if article:
            article.selected = False
            article.selected_at = None
            db.commit()
            db.refresh(article)
        return article

    @staticmethod
    def clear_selections(db: Session) -> int:
        """Clear all selections"""
        count = (
            db.query(NewsArticle)
            .filter(NewsArticle.selected == True)
            .update({"selected": False, "selected_at": None})
        )
        db.commit()
        return count

    @staticmethod
    def upsert(db: Session, article: NewsArticle) -> NewsArticle:
        """Insert or update an article"""
        existing = NewsRepository.get_by_id(db, article.id)
        if existing:
            for key, value in article.__dict__.items():
                if not key.startswith("_") and key != "id":
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            db.add(article)
            db.commit()
            db.refresh(article)
            return article

    @staticmethod
    def count(db: Session, selected_only: bool = False) -> int:
        """Count articles"""
        query = db.query(NewsArticle)
        if selected_only:
            query = query.filter(NewsArticle.selected == True)
        return query.count()
