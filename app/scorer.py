"""
Purple Letter Scorer Module
Calculates ImpactScore based on multiple relevance factors
"""
import os
import sys
import re
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings


class ImpactScorer:
    """
    Calculates ImpactScore for articles

    ImpactScore Formula:
    - MarketRelevance (1-3): How relevant to financial markets
    - BusinessRelevance (1-3): How relevant to business decisions
    - TechShift (1-2): Technology/innovation impact
    - Urgency (1-2): Time sensitivity

    Total ImpactScore: 4-10 (sum of all components)
    """

    # Market relevance keywords (Korean + English)
    MARKET_HIGH_KEYWORDS = [
        "증시", "코스피", "코스닥", "주가", "시장", "투자", "금리", "환율",
        "달러", "원화", "채권", "국채", "금융시장", "거래소", "상장",
        "KOSPI", "KOSDAQ", "stock", "market", "interest rate", "forex"
    ]
    MARKET_MEDIUM_KEYWORDS = [
        "경제", "성장률", "GDP", "인플레이션", "물가", "수출", "수입",
        "무역", "경기", "산업", "economy", "growth", "inflation", "trade"
    ]

    # Business relevance keywords
    BUSINESS_HIGH_KEYWORDS = [
        "실적", "매출", "영업이익", "순이익", "M&A", "인수", "합병",
        "투자유치", "사업확장", "신사업", "계약", "수주", "partnership",
        "revenue", "profit", "acquisition", "expansion"
    ]
    BUSINESS_MEDIUM_KEYWORDS = [
        "기업", "회사", "사업", "경영", "전략", "시장점유율", "경쟁",
        "company", "business", "strategy", "competition", "market share"
    ]

    # Tech shift keywords
    TECH_HIGH_KEYWORDS = [
        "AI", "인공지능", "반도체", "배터리", "전기차", "자율주행",
        "양자", "블록체인", "메타버스", "로봇", "우주", "바이오",
        "신기술", "혁신", "특허", "R&D", "연구개발",
        "semiconductor", "battery", "EV", "autonomous", "quantum", "biotech"
    ]
    TECH_MEDIUM_KEYWORDS = [
        "디지털", "플랫폼", "클라우드", "데이터", "5G", "6G",
        "소프트웨어", "하드웨어", "IT", "테크",
        "digital", "platform", "cloud", "data", "software"
    ]

    # Urgency keywords
    URGENCY_HIGH_KEYWORDS = [
        "[속보]", "[긴급]", "[특보]", "[단독]", "[전격]",
        "긴급", "속보", "돌발", "급변", "충격", "폭락", "폭등",
        "BREAKING", "URGENT", "ALERT"
    ]

    def __init__(self):
        self.scored_count = 0
        # Load weights from settings
        self.weights = {
            "market": settings.WEIGHT_MARKET_RELEVANCE,
            "business": settings.WEIGHT_BUSINESS_RELEVANCE,
            "tech": settings.WEIGHT_TECH_SHIFT,
            "urgency": settings.WEIGHT_URGENCY,
        }

    def calculate_score(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate ImpactScore for a single article

        Args:
            article_data: Transformed article dictionary

        Returns:
            Article dictionary with calculated scores
        """
        title = article_data.get("title", "").lower()
        summary = article_data.get("summary", "").lower()
        text = f"{title} {summary}"
        sector = article_data.get("primary_sector", "")

        # Calculate individual components
        market_relevance = self._calculate_market_relevance(text, sector)
        business_relevance = self._calculate_business_relevance(text, sector)
        tech_shift = self._calculate_tech_shift(text, sector)
        urgency = self._calculate_urgency(article_data.get("title", ""), text)

        # Calculate total impact score (4-10)
        impact_score = (
            market_relevance +
            business_relevance +
            tech_shift +
            urgency
        )

        # Update article data with scores
        article_data.update({
            "market_relevance": market_relevance,
            "business_relevance": business_relevance,
            "tech_shift": tech_shift,
            "urgency": urgency,
            "impact_score": impact_score,
        })

        self.scored_count += 1
        return article_data

    def score_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score a batch of articles"""
        return [self.calculate_score(article) for article in articles]

    def _calculate_market_relevance(self, text: str, sector: str) -> int:
        """
        Calculate market relevance score (1-3)

        3: Directly about financial markets
        2: Indirectly affects markets (economy, trade)
        1: General news with limited market impact
        """
        # Check for high relevance keywords
        if any(kw.lower() in text for kw in self.MARKET_HIGH_KEYWORDS):
            return 3

        # Finance sector boost
        if sector == "finance":
            return 3

        # Check for medium relevance keywords
        if any(kw.lower() in text for kw in self.MARKET_MEDIUM_KEYWORDS):
            return 2

        # Macro economy sector gets at least 2
        if sector == "macro_economy":
            return 2

        return 1

    def _calculate_business_relevance(self, text: str, sector: str) -> int:
        """
        Calculate business relevance score (1-3)

        3: Direct business impact (earnings, M&A, contracts)
        2: Indirect business impact (strategy, competition)
        1: General information
        """
        # Check for high relevance keywords
        if any(kw.lower() in text for kw in self.BUSINESS_HIGH_KEYWORDS):
            return 3

        # Industry/tech sector boost
        if sector == "industry_tech":
            return 3

        # Check for medium relevance keywords
        if any(kw.lower() in text for kw in self.BUSINESS_MEDIUM_KEYWORDS):
            return 2

        # Finance sector gets at least 2
        if sector in ["finance", "macro_economy"]:
            return 2

        return 1

    def _calculate_tech_shift(self, text: str, sector: str) -> int:
        """
        Calculate technology shift score (1-2)

        2: Technology/innovation related
        1: Not technology focused
        """
        # Check for high tech keywords
        if any(kw.lower() in text for kw in self.TECH_HIGH_KEYWORDS):
            return 2

        # Industry/tech sector
        if sector == "industry_tech":
            return 2

        # Check for medium tech keywords
        if any(kw.lower() in text for kw in self.TECH_MEDIUM_KEYWORDS):
            return 2

        return 1

    def _calculate_urgency(self, original_title: str, text: str) -> int:
        """
        Calculate urgency score (1-2)

        2: Breaking news, urgent updates
        1: Regular news
        """
        # Check original title for urgency markers (case-sensitive)
        if any(kw in original_title for kw in self.URGENCY_HIGH_KEYWORDS):
            return 2

        # Check lowercase text for additional urgency indicators
        urgency_patterns = [
            r"긴급\s*발표",
            r"속보\s*:",
            r"급(락|등|변)",
            r"충격.*발표",
            r"돌발.*상황",
        ]
        for pattern in urgency_patterns:
            if re.search(pattern, text):
                return 2

        return 1

    def get_score_breakdown(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed score breakdown with explanations
        Useful for debugging and transparency
        """
        title = article_data.get("title", "")
        summary = article_data.get("summary", "")
        text = f"{title} {summary}".lower()

        breakdown = {
            "market_relevance": {
                "score": article_data.get("market_relevance", 1),
                "max": 3,
                "matched_keywords": [
                    kw for kw in self.MARKET_HIGH_KEYWORDS + self.MARKET_MEDIUM_KEYWORDS
                    if kw.lower() in text
                ][:5],
            },
            "business_relevance": {
                "score": article_data.get("business_relevance", 1),
                "max": 3,
                "matched_keywords": [
                    kw for kw in self.BUSINESS_HIGH_KEYWORDS + self.BUSINESS_MEDIUM_KEYWORDS
                    if kw.lower() in text
                ][:5],
            },
            "tech_shift": {
                "score": article_data.get("tech_shift", 1),
                "max": 2,
                "matched_keywords": [
                    kw for kw in self.TECH_HIGH_KEYWORDS + self.TECH_MEDIUM_KEYWORDS
                    if kw.lower() in text
                ][:5],
            },
            "urgency": {
                "score": article_data.get("urgency", 1),
                "max": 2,
                "matched_keywords": [
                    kw for kw in self.URGENCY_HIGH_KEYWORDS
                    if kw in title
                ][:3],
            },
            "total_impact_score": article_data.get("impact_score", 4),
            "max_possible": 10,
        }

        return breakdown


# Default scorer instance
scorer = ImpactScorer()
