"""Social media manipulation analysis."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import pandas as pd


@dataclass
class SocialRiskResult:
    manipulation_score: float
    narrative_summary: str
    keyword_clusters: list[dict]
    top_tickers: list[str]
    bot_burst_ratio: float


class SocialAnalysisEngine:
    def analyze_posts(self, posts_df: pd.DataFrame, stock_ticker: str) -> SocialRiskResult:
        if posts_df.empty:
            return SocialRiskResult(0.0, "No social activity", [], [], 0.0)

        df = posts_df.copy()
        bullish = (df["sentiment_score"] > 0.3).sum()
        total = len(df)
        burst = df["mention_burst"].sum() if "mention_burst" in df.columns else 0
        bots = df["is_bot_like"].sum() if "is_bot_like" in df.columns else 0

        manipulation_score = min(
            1.0,
            0.35 * (bullish / max(total, 1))
            + 0.25 * (burst / max(total, 1))
            + 0.25 * (bots / max(total, 1))
            + 0.15 * min(total / 50.0, 1.0),
        )

        words = []
        for c in df["content"].astype(str):
            words.extend(w.lower() for w in c.split() if len(w) > 4)
        common = Counter(words).most_common(5)
        keyword_clusters = [{"term": t, "count": c} for t, c in common]

        narrative = (
            f"Detected {burst} mention bursts and {bots} bot-like posts "
            f"with {bullish}/{total} bullish messages for {stock_ticker}."
        )

        return SocialRiskResult(
            manipulation_score=round(manipulation_score, 4),
            narrative_summary=narrative,
            keyword_clusters=keyword_clusters,
            top_tickers=[stock_ticker],
            bot_burst_ratio=round(bots / max(total, 1), 4),
        )
