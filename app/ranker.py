"""
Purple Letter Ranker Module
Ranks and filters articles based on ImpactScore and other criteria
"""
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings


class ArticleRanker:
    """
    Ranks articles for newsletter recommendation

    Ranking criteria (in order of priority):
    1. ImpactScore (primary)
    2. Urgency (breaking news priority)
    3. Recency (newer articles preferred)
    4. Strategic diversity (avoid all same-sector picks)
    """

    def __init__(self):
        self.default_top_n = settings.DEFAULT_TOP_N
        self.min_score = settings.MIN_IMPACT_SCORE

    def rank(
        self,
        articles: List[Dict[str, Any]],
        top_n: Optional[int] = None,
        min_score: Optional[int] = None,
        sector_filter: Optional[str] = None,
        strategic_tag_filter: Optional[str] = None,
        ensure_diversity: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Rank articles and return top N

        Args:
            articles: List of scored article dictionaries
            top_n: Number of top articles to return (default: 4)
            min_score: Minimum ImpactScore threshold
            sector_filter: Filter by specific sector
            strategic_tag_filter: Filter by strategic tag
            ensure_diversity: Ensure sector diversity in results

        Returns:
            Sorted and filtered list of articles
        """
        top_n = top_n or self.default_top_n
        min_score = min_score or self.min_score

        # Apply filters
        filtered = self._apply_filters(
            articles,
            min_score=min_score,
            sector_filter=sector_filter,
            strategic_tag_filter=strategic_tag_filter,
        )

        # Sort by ranking criteria
        sorted_articles = self._sort_articles(filtered)

        # Apply diversity if requested
        if ensure_diversity and len(sorted_articles) > top_n:
            sorted_articles = self._ensure_diversity(sorted_articles, top_n)
        else:
            sorted_articles = sorted_articles[:top_n]

        return sorted_articles

    def get_recommendations(
        self,
        articles: List[Dict[str, Any]],
        top_n: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Get top N recommended articles for newsletter

        This is the main method for newsletter generation.
        Returns diverse, high-impact articles.
        """
        return self.rank(
            articles,
            top_n=top_n,
            ensure_diversity=True,
        )

    def _apply_filters(
        self,
        articles: List[Dict[str, Any]],
        min_score: int = 4,
        sector_filter: Optional[str] = None,
        strategic_tag_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Apply filtering criteria"""
        filtered = []

        for article in articles:
            # Score filter
            if article.get("impact_score", 0) < min_score:
                continue

            # Sector filter
            if sector_filter:
                if article.get("primary_sector") != sector_filter and \
                   article.get("secondary_sector") != sector_filter:
                    continue

            # Strategic tag filter
            if strategic_tag_filter:
                if article.get("strategic_tag") != strategic_tag_filter:
                    continue

            filtered.append(article)

        return filtered

    def _sort_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort articles by ranking criteria

        Primary: ImpactScore (descending)
        Secondary: Urgency (descending)
        Tertiary: Published date (descending - newer first)
        """
        def sort_key(article):
            impact_score = article.get("impact_score", 0)
            urgency = article.get("urgency", 1)

            # Parse published_at for recency scoring
            published_at = article.get("published_at")
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    published_at = datetime.min
            elif not isinstance(published_at, datetime):
                published_at = datetime.min

            # Recency bonus: articles from last 24 hours get +1
            recency_bonus = 0
            if published_at > datetime.utcnow() - timedelta(hours=24):
                recency_bonus = 1

            # Combined score for sorting
            # Impact score is primary (multiply by 100)
            # Urgency is secondary (multiply by 10)
            # Recency bonus is tertiary
            combined = (impact_score * 100) + (urgency * 10) + recency_bonus

            return (-combined, published_at)

        return sorted(articles, key=sort_key)

    def _ensure_diversity(
        self,
        articles: List[Dict[str, Any]],
        top_n: int,
    ) -> List[Dict[str, Any]]:
        """
        Ensure sector diversity in selected articles

        Strategy:
        - First pick: Highest scoring article
        - Subsequent picks: Prefer different sectors while maintaining high scores
        - Allow max 2 articles from same sector in top 4
        """
        if len(articles) <= top_n:
            return articles

        selected = []
        sector_counts = {}
        max_per_sector = max(2, top_n // 2)  # At most half from same sector

        for article in articles:
            if len(selected) >= top_n:
                break

            sector = article.get("primary_sector", "unknown")

            # Check sector diversity constraint
            if sector_counts.get(sector, 0) >= max_per_sector:
                # Skip if we already have enough from this sector
                # Unless we're running out of options
                remaining_needed = top_n - len(selected)
                remaining_articles = len(articles) - articles.index(article)
                if remaining_articles > remaining_needed:
                    continue

            selected.append(article)
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        return selected

    def get_sector_distribution(
        self, articles: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Get distribution of articles by sector"""
        distribution = {}
        for article in articles:
            sector = article.get("primary_sector", "unknown")
            distribution[sector] = distribution.get(sector, 0) + 1
        return distribution

    def get_score_distribution(
        self, articles: List[Dict[str, Any]]
    ) -> Dict[int, int]:
        """Get distribution of articles by ImpactScore"""
        distribution = {}
        for article in articles:
            score = article.get("impact_score", 0)
            distribution[score] = distribution.get(score, 0) + 1
        return dict(sorted(distribution.items(), reverse=True))

    def get_strategic_tag_distribution(
        self, articles: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Get distribution of articles by strategic tag"""
        distribution = {}
        for article in articles:
            tag = article.get("strategic_tag", "neutral")
            distribution[tag] = distribution.get(tag, 0) + 1
        return distribution


# Default ranker instance
ranker = ArticleRanker()
