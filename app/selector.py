"""
Purple Letter Selector Module
Handles manual selection of articles for newsletter
"""
import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import NewsArticle, SelectionHistory, NewsRepository


class NewsletterSelector:
    """
    Manages manual selection of articles for newsletter

    Key principles:
    - Newsletter content is NOT auto-generated
    - System provides recommendations (Top 4)
    - Human makes final selection
    - Selection history is tracked for analytics
    """

    def __init__(self, db: Session):
        self.db = db

    def select_article(self, article_id: str, selected_by: str = "admin") -> Optional[NewsArticle]:
        """
        Select an article for newsletter inclusion

        Args:
            article_id: ID of the article to select
            selected_by: Username/identifier of person selecting

        Returns:
            Updated article or None if not found
        """
        article = NewsRepository.select_article(self.db, article_id)

        if article:
            # Record selection history
            history = SelectionHistory(
                newsletter_date=datetime.utcnow().strftime("%Y-%m-%d"),
                article_id=article_id,
                selected_at=datetime.utcnow(),
                selected_by=selected_by,
            )
            self.db.add(history)
            self.db.commit()

        return article

    def select_multiple(
        self, article_ids: List[str], selected_by: str = "admin"
    ) -> Dict[str, Any]:
        """
        Select multiple articles at once

        Returns:
            Dict with success count and any errors
        """
        results = {
            "selected_count": 0,
            "errors": [],
            "selected_ids": [],
        }

        for article_id in article_ids:
            try:
                article = self.select_article(article_id, selected_by)
                if article:
                    results["selected_count"] += 1
                    results["selected_ids"].append(article_id)
                else:
                    results["errors"].append(f"Article not found: {article_id}")
            except Exception as e:
                results["errors"].append(f"Error selecting {article_id}: {str(e)}")

        return results

    def deselect_article(self, article_id: str) -> Optional[NewsArticle]:
        """
        Remove an article from newsletter selection

        Args:
            article_id: ID of the article to deselect

        Returns:
            Updated article or None if not found
        """
        return NewsRepository.deselect_article(self.db, article_id)

    def deselect_multiple(self, article_ids: List[str]) -> Dict[str, Any]:
        """Deselect multiple articles"""
        results = {
            "deselected_count": 0,
            "errors": [],
        }

        for article_id in article_ids:
            try:
                article = self.deselect_article(article_id)
                if article:
                    results["deselected_count"] += 1
                else:
                    results["errors"].append(f"Article not found: {article_id}")
            except Exception as e:
                results["errors"].append(f"Error deselecting {article_id}: {str(e)}")

        return results

    def clear_all_selections(self) -> int:
        """
        Clear all current selections

        Use this when starting a new newsletter edition
        Returns the count of cleared selections
        """
        return NewsRepository.clear_selections(self.db)

    def get_selected_articles(self) -> List[NewsArticle]:
        """Get all currently selected articles"""
        return NewsRepository.get_selected(self.db)

    def get_selection_count(self) -> int:
        """Get count of currently selected articles"""
        return NewsRepository.count(self.db, selected_only=True)

    def get_selection_history(
        self,
        date: Optional[str] = None,
        limit: int = 100,
    ) -> List[SelectionHistory]:
        """
        Get selection history

        Args:
            date: Filter by newsletter date (YYYY-MM-DD format)
            limit: Maximum records to return

        Returns:
            List of SelectionHistory records
        """
        query = self.db.query(SelectionHistory)

        if date:
            query = query.filter(SelectionHistory.newsletter_date == date)

        return query.order_by(SelectionHistory.selected_at.desc()).limit(limit).all()

    def validate_selection(self) -> Dict[str, Any]:
        """
        Validate current selection for newsletter readiness

        Returns:
            Validation results with warnings and recommendations
        """
        selected = self.get_selected_articles()
        count = len(selected)

        validation = {
            "is_valid": True,
            "selected_count": count,
            "warnings": [],
            "recommendations": [],
        }

        # Check minimum selection
        if count < 3:
            validation["warnings"].append(
                f"Only {count} articles selected. Recommend at least 3 for a balanced newsletter."
            )

        # Check maximum selection
        if count > 5:
            validation["warnings"].append(
                f"{count} articles selected. Consider limiting to 4-5 for reader engagement."
            )

        # Check sector diversity
        sectors = {}
        for article in selected:
            sector = article.primary_sector or "unknown"
            sectors[sector] = sectors.get(sector, 0) + 1

        if len(sectors) == 1 and count > 2:
            validation["warnings"].append(
                "All selected articles are from the same sector. Consider adding diversity."
            )

        # Check for breaking news inclusion
        has_breaking = any(
            article.strategic_tag in ["breaking", "exclusive"]
            for article in selected
        )
        if not has_breaking:
            validation["recommendations"].append(
                "No breaking/exclusive news in selection. Check if any important updates were missed."
            )

        # Check score distribution
        scores = [article.impact_score for article in selected]
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score < 6:
                validation["recommendations"].append(
                    f"Average ImpactScore is {avg_score:.1f}. Consider selecting higher-impact articles."
                )

        if validation["warnings"]:
            validation["is_valid"] = False

        return validation

    def get_newsletter_preview(self) -> Dict[str, Any]:
        """
        Get a preview of the newsletter with selected articles

        Returns formatted preview data
        """
        selected = self.get_selected_articles()

        preview = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "article_count": len(selected),
            "articles": [],
            "sectors_covered": set(),
            "avg_impact_score": 0,
        }

        total_score = 0
        for article in selected:
            preview["articles"].append({
                "id": article.id,
                "title": article.title,
                "source": article.source,
                "impact_score": article.impact_score,
                "strategic_tag": article.strategic_tag,
                "primary_sector": article.primary_sector,
            })
            preview["sectors_covered"].add(article.primary_sector)
            total_score += article.impact_score

        preview["sectors_covered"] = list(preview["sectors_covered"])

        if selected:
            preview["avg_impact_score"] = round(total_score / len(selected), 1)

        return preview


def get_selector(db: Session) -> NewsletterSelector:
    """Factory function for creating selector instance"""
    return NewsletterSelector(db)
