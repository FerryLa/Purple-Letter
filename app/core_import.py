"""
Purple Letter Core Import Module
Connects to news-scanner-core (News-Leafletter) and imports data
"""
import os
import sys
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings


@dataclass
class RawArticle:
    """Raw article data from news-scanner-core"""

    article_id: str
    title: str
    link: str
    summary: str
    source_name: str
    published_at: Optional[datetime]
    image_url: Optional[str]
    primary_sector: Optional[str]
    secondary_sector: Optional[str]
    subcategories: List[str]
    original_score: int = 0
    matched_keywords: List[str] = None

    def __post_init__(self):
        if self.matched_keywords is None:
            self.matched_keywords = []


class NewsScannerCoreConnector:
    """
    Connector to news-scanner-core (News-Leafletter)
    Reads data directly from the SQLite database without modifying it
    """

    def __init__(self, core_path: str = None, db_path: str = None):
        self.core_path = core_path or settings.NEWS_SCANNER_CORE_PATH
        self.db_path = db_path or self._find_database()
        self._validate_connection()

    def _find_database(self) -> str:
        """Find the news-scanner-core database file"""
        possible_paths = [
            os.path.join(self.core_path, "data", "news_scanner.db"),
            os.path.join(self.core_path, "news_scanner.db"),
            os.path.join(self.core_path, "data", "articles.db"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        raise FileNotFoundError(
            f"Could not find news-scanner-core database. Searched paths: {possible_paths}"
        )

    def _validate_connection(self) -> bool:
        """Validate that we can connect to the database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        return True

    def _get_connection(self) -> sqlite3.Connection:
        """Get a read-only connection to the database"""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def fetch_articles(
        self,
        limit: int = 100,
        offset: int = 0,
        since: Optional[datetime] = None,
        min_score: Optional[int] = None,
    ) -> List[RawArticle]:
        """
        Fetch articles from news-scanner-core database
        Read-only operation - does not modify the source database
        """
        conn = self._get_connection()
        try:
            query = """
                SELECT
                    article_id,
                    title,
                    link,
                    COALESCE(summary, content, '') as summary,
                    source_name,
                    published_at,
                    image_url,
                    primary_sector,
                    secondary_sector,
                    subcategories
                FROM articles
                WHERE 1=1
            """
            params = []

            if since:
                query += " AND published_at >= ?"
                params.append(since.isoformat())

            query += " ORDER BY published_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            articles = []
            for row in rows:
                try:
                    subcategories = []
                    if row["subcategories"]:
                        try:
                            subcategories = json.loads(row["subcategories"])
                        except (json.JSONDecodeError, TypeError):
                            subcategories = []

                    published_at = None
                    if row["published_at"]:
                        try:
                            published_at = datetime.fromisoformat(
                                row["published_at"].replace("Z", "+00:00")
                            )
                        except (ValueError, AttributeError):
                            pass

                    article = RawArticle(
                        article_id=row["article_id"]
                        or self._generate_id(row["link"], row["title"]),
                        title=row["title"] or "",
                        link=row["link"] or "",
                        summary=row["summary"] or "",
                        source_name=row["source_name"] or "Unknown",
                        published_at=published_at,
                        image_url=row["image_url"],
                        primary_sector=row["primary_sector"],
                        secondary_sector=row["secondary_sector"],
                        subcategories=subcategories,
                    )
                    articles.append(article)
                except Exception as e:
                    print(f"Warning: Failed to parse article: {e}")
                    continue

            return articles
        finally:
            conn.close()

    def fetch_with_scores(
        self, chat_id: Optional[int] = None, limit: int = 100
    ) -> List[RawArticle]:
        """
        Fetch articles with their original scores from news-scanner-core
        If chat_id is provided, fetch user-specific scores
        """
        conn = self._get_connection()
        try:
            # Check if news_history table exists for scores
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='news_history'"
            )
            has_history = cursor.fetchone() is not None

            if has_history and chat_id:
                query = """
                    SELECT DISTINCT
                        a.article_id,
                        a.title,
                        a.link,
                        COALESCE(a.summary, a.content, '') as summary,
                        a.source_name,
                        a.published_at,
                        a.image_url,
                        a.primary_sector,
                        a.secondary_sector,
                        a.subcategories,
                        COALESCE(h.score, 0) as original_score
                    FROM articles a
                    LEFT JOIN news_history h ON a.article_id = h.article_id
                    WHERE h.chat_id = ? OR h.chat_id IS NULL
                    ORDER BY a.published_at DESC
                    LIMIT ?
                """
                cursor = conn.execute(query, [chat_id, limit])
            else:
                query = """
                    SELECT
                        article_id,
                        title,
                        link,
                        COALESCE(summary, content, '') as summary,
                        source_name,
                        published_at,
                        image_url,
                        primary_sector,
                        secondary_sector,
                        subcategories,
                        0 as original_score
                    FROM articles
                    ORDER BY published_at DESC
                    LIMIT ?
                """
                cursor = conn.execute(query, [limit])

            rows = cursor.fetchall()

            articles = []
            for row in rows:
                try:
                    subcategories = []
                    if row["subcategories"]:
                        try:
                            subcategories = json.loads(row["subcategories"])
                        except (json.JSONDecodeError, TypeError):
                            subcategories = []

                    published_at = None
                    if row["published_at"]:
                        try:
                            published_at = datetime.fromisoformat(
                                row["published_at"].replace("Z", "+00:00")
                            )
                        except (ValueError, AttributeError):
                            pass

                    article = RawArticle(
                        article_id=row["article_id"]
                        or self._generate_id(row["link"], row["title"]),
                        title=row["title"] or "",
                        link=row["link"] or "",
                        summary=row["summary"] or "",
                        source_name=row["source_name"] or "Unknown",
                        published_at=published_at,
                        image_url=row["image_url"],
                        primary_sector=row["primary_sector"],
                        secondary_sector=row["secondary_sector"],
                        subcategories=subcategories,
                        original_score=row["original_score"] or 0,
                    )
                    articles.append(article)
                except Exception as e:
                    print(f"Warning: Failed to parse article: {e}")
                    continue

            return articles
        finally:
            conn.close()

    def get_latest_article_time(self) -> Optional[datetime]:
        """Get the timestamp of the most recent article"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT MAX(published_at) as latest FROM articles"
            )
            row = cursor.fetchone()
            if row and row["latest"]:
                try:
                    return datetime.fromisoformat(
                        row["latest"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    return None
            return None
        finally:
            conn.close()

    def get_article_count(self) -> int:
        """Get total article count in source database"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) as count FROM articles")
            row = cursor.fetchone()
            return row["count"] if row else 0
        finally:
            conn.close()

    def get_sectors(self) -> Dict[str, int]:
        """Get sector distribution"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT primary_sector, COUNT(*) as count
                FROM articles
                WHERE primary_sector IS NOT NULL
                GROUP BY primary_sector
                ORDER BY count DESC
            """)
            return {row["primary_sector"]: row["count"] for row in cursor.fetchall()}
        finally:
            conn.close()

    def check_health(self) -> Dict[str, Any]:
        """Check connection health and return status"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("SELECT COUNT(*) as count FROM articles")
            count = cursor.fetchone()["count"]
            conn.close()
            return {
                "connected": True,
                "database_path": self.db_path,
                "article_count": count,
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}

    @staticmethod
    def _generate_id(link: str, title: str) -> str:
        """Generate a unique ID from link and title"""
        content = f"{link}:{title}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


# Singleton connector instance
_connector: Optional[NewsScannerCoreConnector] = None


def get_connector() -> NewsScannerCoreConnector:
    """Get or create the singleton connector instance"""
    global _connector
    if _connector is None:
        _connector = NewsScannerCoreConnector()
    return _connector
