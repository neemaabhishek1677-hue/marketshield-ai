"""News sentiment pipeline with VADER + hype heuristics."""

from __future__ import annotations

import re
from dataclasses import dataclass

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

HYPE_KEYWORDS = {"moon", "rocket", "guaranteed", "breakout", "insider tip", "100x", "pump", "squeeze"}
FEAR_KEYWORDS = {"crash", "fraud", "sec probe", "bankruptcy", "delisting", "scam"}
SUSPICIOUS_KEYWORDS = {"leak", "confidential", "undisclosed", "before announcement", "sure thing"}


@dataclass
class SentimentResult:
    label: str
    score: float
    tone: str
    hype_score: float


class SentimentEngine:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> SentimentResult:
        scores = self.analyzer.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.25:
            label = "positive"
        elif compound <= -0.25:
            label = "negative"
        else:
            label = "neutral"

        lower = text.lower()
        hype_hits = sum(1 for k in HYPE_KEYWORDS if k in lower)
        fear_hits = sum(1 for k in FEAR_KEYWORDS if k in lower)
        sus_hits = sum(1 for k in SUSPICIOUS_KEYWORDS if k in lower)

        hype_score = min(1.0, (hype_hits * 0.25) + (len(re.findall(r"!", text)) * 0.05))
        if sus_hits > 0:
            tone = "suspicious_misinformation"
        elif hype_hits >= 2:
            tone = "hype"
        elif fear_hits >= 2:
            tone = "fear"
        else:
            tone = "neutral"

        return SentimentResult(label=label, score=round(compound, 4), tone=tone, hype_score=round(hype_score, 4))
