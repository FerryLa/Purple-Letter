"""
Purple Letter Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class StrategicTag(str, Enum):
    """Strategic classification tags"""
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    TREND = "trend"
    POLICY = "policy"
    BREAKING = "breaking"
    EXCLUSIVE = "exclusive"
    NEUTRAL = "neutral"


class SectorType(str, Enum):
    """Main sector classification"""
    MACRO_ECONOMY = "macro_economy"
    SOCIAL_POLICY = "social_policy"
    FINANCE = "finance"
    INDUSTRY_TECH = "industry_tech"
    CULTURE_LIFESTYLE = "culture_lifestyle"


class NewsItemBase(BaseModel):
    """Base news item model"""
    title: str
    link: str
    summary: str
    source: str
    published_at: datetime
    primary_sector: Optional[str] = None
    secondary_sector: Optional[str] = None
    subcategories: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None


class NewsItemCreate(NewsItemBase):
    """Model for creating news items"""
    pass


class ScoreBreakdown(BaseModel):
    """ImpactScore component breakdown"""
    market_relevance: int = Field(ge=1, le=3, description="Market relevance score (1-3)")
    business_relevance: int = Field(ge=1, le=3, description="Business relevance score (1-3)")
    tech_shift: int = Field(ge=1, le=2, description="Technology shift score (1-2)")
    urgency: int = Field(ge=1, le=2, description="Urgency score (1-2)")


class NewsItem(NewsItemBase):
    """Full news item model with scores and selection state"""
    id: str
    date: str

    # Score components
    market_relevance: int = Field(ge=1, le=3, default=1)
    business_relevance: int = Field(ge=1, le=3, default=1)
    tech_shift: int = Field(ge=1, le=2, default=1)
    urgency: int = Field(ge=1, le=2, default=1)

    # Calculated score
    impact_score: int = Field(ge=4, le=10, default=4)

    # Classification
    strategic_tag: StrategicTag = StrategicTag.NEUTRAL

    # Selection state
    selected: bool = False
    selected_at: Optional[datetime] = None

    # Original data reference
    original_score: Optional[int] = None  # Score from news-scanner-core
    matched_keywords: Optional[List[str]] = None

    # Why it matters analysis
    why_it_matters: Optional[str] = None
    implication: Optional[str] = None

    class Config:
        from_attributes = True


class NewsItemResponse(BaseModel):
    """API response for single news item"""
    success: bool = True
    data: NewsItem


class NewsListResponse(BaseModel):
    """API response for news list"""
    success: bool = True
    total: int
    data: List[NewsItem]


class NewsletterResponse(BaseModel):
    """API response for newsletter (selected news only)"""
    success: bool = True
    selected_count: int
    newsletter_date: str
    data: List[NewsItem]


class DatasetResponse(BaseModel):
    """API response for Power BI dataset"""
    success: bool = True
    last_updated: datetime
    total_records: int
    data: List[NewsItem]


class SelectionRequest(BaseModel):
    """Request model for selecting news"""
    news_ids: List[str]


class SelectionResponse(BaseModel):
    """Response model for selection operation"""
    success: bool = True
    selected_count: int
    message: str


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    database_connected: bool
    news_scanner_connected: bool
    last_sync: Optional[datetime] = None


class FilterParams(BaseModel):
    """Query filter parameters"""
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    category: Optional[str] = None
    sector: Optional[str] = None
    strategic_tag: Optional[StrategicTag] = None
    selected_only: bool = False
    limit: int = Field(default=50, le=200)
    offset: int = 0
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class SyncStatus(BaseModel):
    """Status of data synchronization with news-scanner-core"""
    last_sync: Optional[datetime] = None
    articles_synced: int = 0
    articles_transformed: int = 0
    articles_scored: int = 0
    errors: List[str] = Field(default_factory=list)
