"""
Purple Letter Transformer Module
Transforms raw articles into structured intelligence format
"""
import os
import sys
import re
from datetime import datetime
from typing import List, Optional, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core_import import RawArticle
from app.models import StrategicTag


class ArticleTransformer:
    """
    Transforms raw articles from news-scanner-core into
    structured intelligence format for Purple Letter
    """

    # Breaking news indicators (Korean)
    BREAKING_KEYWORDS = {
        "[속보]": 15,
        "[긴급]": 15,
        "[특보]": 15,
        "긴급속보": 15,
        "[단독]": 12,
        "단독입수": 12,
        "[전격]": 10,
        "[독점]": 10,
        "BREAKING": 12,
        "Breaking": 12,
    }

    # Strategic tag keywords
    OPPORTUNITY_KEYWORDS = [
        "성장",
        "투자",
        "확대",
        "기회",
        "상승",
        "호재",
        "증가",
        "수혜",
        "전망 밝",
        "growth",
        "opportunity",
    ]
    RISK_KEYWORDS = [
        "리스크",
        "위험",
        "하락",
        "악재",
        "우려",
        "감소",
        "축소",
        "위기",
        "불안",
        "risk",
        "warning",
    ]
    TREND_KEYWORDS = [
        "트렌드",
        "동향",
        "전환",
        "변화",
        "흐름",
        "추세",
        "시장 동향",
        "trend",
        "shift",
    ]
    POLICY_KEYWORDS = [
        "정책",
        "규제",
        "법안",
        "발표",
        "정부",
        "금융위",
        "한국은행",
        "policy",
        "regulation",
    ]

    def __init__(self):
        self.transformed_count = 0

    def transform(self, raw_article: RawArticle) -> Dict[str, Any]:
        """
        Transform a single raw article into structured format

        Returns a dictionary ready for database insertion
        """
        title = raw_article.title.strip()
        summary = self._clean_summary(raw_article.summary)

        # Detect breaking/exclusive news
        is_breaking, breaking_score = self._detect_breaking(title)

        # Determine strategic tag
        strategic_tag = self._determine_strategic_tag(title, summary, is_breaking)

        # Generate analysis fields
        why_it_matters = self._generate_why_it_matters(title, summary, raw_article.primary_sector)
        implication = self._generate_implication(title, summary, strategic_tag)

        # Format date
        date_str = (
            raw_article.published_at.strftime("%Y-%m-%d")
            if raw_article.published_at
            else datetime.utcnow().strftime("%Y-%m-%d")
        )

        self.transformed_count += 1

        return {
            "id": raw_article.article_id,
            "title": title,
            "link": raw_article.link,
            "summary": summary,
            "source": raw_article.source_name,
            "published_at": raw_article.published_at or datetime.utcnow(),
            "date": date_str,
            "image_url": raw_article.image_url,
            "primary_sector": raw_article.primary_sector,
            "secondary_sector": raw_article.secondary_sector,
            "subcategories": raw_article.subcategories or [],
            "strategic_tag": strategic_tag.value,
            "original_score": raw_article.original_score,
            "matched_keywords": raw_article.matched_keywords or [],
            "why_it_matters": why_it_matters,
            "implication": implication,
            # Scores will be calculated by scorer module
            "market_relevance": 1,
            "business_relevance": 1,
            "tech_shift": 1,
            "urgency": 2 if is_breaking else 1,
            "impact_score": 4,  # Will be recalculated
        }

    def transform_batch(self, raw_articles: List[RawArticle]) -> List[Dict[str, Any]]:
        """Transform a batch of articles"""
        return [self.transform(article) for article in raw_articles]

    def _clean_summary(self, summary: str) -> str:
        """Clean and normalize summary text"""
        if not summary:
            return ""

        # Remove HTML tags
        summary = re.sub(r"<[^>]+>", "", summary)

        # Remove excessive whitespace
        summary = re.sub(r"\s+", " ", summary)

        # Remove common artifacts
        summary = summary.replace("&nbsp;", " ")
        summary = summary.replace("&amp;", "&")
        summary = summary.replace("&lt;", "<")
        summary = summary.replace("&gt;", ">")

        return summary.strip()

    def _detect_breaking(self, title: str) -> tuple:
        """
        Detect if article is breaking/exclusive news
        Returns (is_breaking, priority_score)
        """
        for keyword, score in self.BREAKING_KEYWORDS.items():
            if keyword in title:
                return True, score
        return False, 0

    def _determine_strategic_tag(
        self, title: str, summary: str, is_breaking: bool
    ) -> StrategicTag:
        """Determine the strategic classification tag"""
        text = f"{title} {summary}".lower()

        if is_breaking:
            if "[단독]" in title or "단독" in title:
                return StrategicTag.EXCLUSIVE
            return StrategicTag.BREAKING

        # Check for opportunity indicators
        if any(kw in text for kw in self.OPPORTUNITY_KEYWORDS):
            return StrategicTag.OPPORTUNITY

        # Check for risk indicators
        if any(kw in text for kw in self.RISK_KEYWORDS):
            return StrategicTag.RISK

        # Check for policy indicators
        if any(kw in text for kw in self.POLICY_KEYWORDS):
            return StrategicTag.POLICY

        # Check for trend indicators
        if any(kw in text for kw in self.TREND_KEYWORDS):
            return StrategicTag.TREND

        return StrategicTag.NEUTRAL

    def _generate_why_it_matters(
        self, title: str, summary: str, sector: Optional[str]
    ) -> str:
        """
        Generate a brief "Why it matters" analysis
        This can be enhanced with LLM integration later
        """
        sector_context = {
            "macro_economy": "거시경제 관점에서",
            "finance": "금융시장 관점에서",
            "industry_tech": "산업/기술 측면에서",
            "social_policy": "사회정책 측면에서",
            "culture_lifestyle": "문화/생활 트렌드 측면에서",
        }

        context = sector_context.get(sector, "")

        # Basic template - can be replaced with LLM-generated content
        if context:
            return f"{context} 주목할 필요가 있는 뉴스입니다."
        return "시장에 영향을 미칠 수 있는 뉴스입니다."

    def _generate_implication(
        self, title: str, summary: str, tag: StrategicTag
    ) -> str:
        """
        Generate implication analysis based on strategic tag
        This can be enhanced with LLM integration later
        """
        implications = {
            StrategicTag.OPPORTUNITY: "투자 또는 사업 기회로 검토해볼 만합니다.",
            StrategicTag.RISK: "리스크 관리 및 대응 방안 검토가 필요합니다.",
            StrategicTag.TREND: "시장 트렌드 변화에 주목하여 전략 조정을 고려하세요.",
            StrategicTag.POLICY: "규제 및 정책 변화에 따른 영향을 분석하세요.",
            StrategicTag.BREAKING: "긴급 상황으로 즉시 모니터링이 필요합니다.",
            StrategicTag.EXCLUSIVE: "단독 정보로 선제적 대응을 고려하세요.",
            StrategicTag.NEUTRAL: "지속적인 모니터링을 권장합니다.",
        }
        return implications.get(tag, "추가 분석이 필요합니다.")


# Default transformer instance
transformer = ArticleTransformer()
