"""Pump-and-dump early warning via multi-signal fusion."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PumpDumpPrediction:
    likelihood: float
    risk_level: str
    dump_risk_after_peak: float
    indicators: dict
    explanation: str


class PumpDumpEngine:
    def predict(
        self,
        volume_spike: float,
        price_acceleration: float,
        social_burst: float,
        market_cap: float,
        sentiment_hype: float,
        buy_concentration: float,
    ) -> PumpDumpPrediction:
        low_liquidity = 1.0 - min(market_cap / 5e9, 1.0)
        likelihood = min(
            1.0,
            0.22 * min(volume_spike / 4.0, 1.0)
            + 0.18 * min(abs(price_acceleration) / 0.12, 1.0)
            + 0.2 * social_burst
            + 0.12 * low_liquidity
            + 0.15 * sentiment_hype
            + 0.13 * buy_concentration,
        )
        dump_risk = min(1.0, likelihood * 0.85 + 0.15 * social_burst)

        if likelihood >= 0.75:
            level = "high-risk pump formation"
        elif likelihood >= 0.55:
            level = "elevated"
        elif likelihood >= 0.35:
            level = "watchlist"
        else:
            level = "low risk"

        indicators = {
            "volume_spike": round(volume_spike, 3),
            "price_acceleration": round(price_acceleration, 3),
            "social_burst": round(social_burst, 3),
            "low_liquidity_profile": round(low_liquidity, 3),
            "sentiment_hype": round(sentiment_hype, 3),
            "buy_concentration": round(buy_concentration, 3),
        }
        explanation = (
            f"Pump-and-dump surveillance estimate {likelihood:.0%} ({level}). "
            f"Primary drivers: volume spike, social burst, and buy concentration. "
            "Demo signal only — not trading advice."
        )
        return PumpDumpPrediction(
            likelihood=round(likelihood, 4),
            risk_level=level,
            dump_risk_after_peak=round(dump_risk, 4),
            indicators=indicators,
            explanation=explanation,
        )
