"""Feature engineering for trade anomaly and risk fusion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


FEATURE_NAMES = [
    "trade_size_ratio",
    "trader_stock_frequency",
    "event_window_distance",
    "abnormal_profit_ratio",
    "intraday_volume_spike",
    "cancel_to_fill_ratio",
    "account_coordination_score",
    "insider_proximity_score",
    "sentiment_momentum",
    "social_burst_intensity",
    "price_acceleration_score",
    "abnormal_volatility_score",
]


@dataclass
class FeatureVector:
    values: np.ndarray
    names: list[str]
    metadata: dict


def build_trade_features(
    trades_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    events_df: pd.DataFrame,
    trader_id: int,
    stock_id: int,
    as_of: datetime,
) -> FeatureVector:
    """Compute per-trader-stock feature vector for anomaly detection."""
    tdf = trades_df[
        (trades_df["trader_id"] == trader_id) & (trades_df["stock_id"] == stock_id)
    ].copy()
    all_trader = trades_df[trades_df["trader_id"] == trader_id]
    stock_trades = trades_df[trades_df["stock_id"] == stock_id]

    window = as_of - timedelta(days=5)
    recent = tdf[tdf["executed_at"] >= window] if not tdf.empty else tdf

    hist_mean = all_trader["notional"].mean() if not all_trader.empty else 1.0
    recent_mean = recent["notional"].mean() if not recent.empty else 0.0
    trade_size_ratio = float(recent_mean / max(hist_mean, 1.0))

    trader_stock_frequency = float(len(tdf) / max(len(all_trader), 1))

    event_window_distance = 30.0
    if not events_df.empty:
        ev = events_df[events_df["stock_id"] == stock_id]
        if not ev.empty:
            nearest = (ev["event_date"] - as_of).abs().min()
            event_window_distance = float(nearest.total_seconds() / 86400)

    buy_recent = recent[recent["side"] == "buy"]["notional"].sum() if not recent.empty else 0
    sell_recent = recent[recent["side"] == "sell"]["notional"].sum() if not recent.empty else 0
    abnormal_profit_ratio = float((sell_recent - buy_recent) / max(buy_recent, 1.0))

    day_start = as_of.replace(hour=0, minute=0, second=0, microsecond=0)
    intraday = stock_trades[stock_trades["executed_at"] >= day_start]
    baseline = stock_trades[stock_trades["executed_at"] < day_start]["quantity"].mean()
    intraday_volume_spike = float(
        intraday["quantity"].sum() / max(baseline if not np.isnan(baseline) else 1.0, 1.0)
    )

    odf = orders_df[
        (orders_df["trader_id"] == trader_id) & (orders_df["stock_id"] == stock_id)
    ]
    cancelled = len(odf[odf["status"] == "cancelled"]) if not odf.empty else 0
    filled = len(odf[odf["status"] == "filled"]) if not odf.empty else 1
    cancel_to_fill_ratio = float(cancelled / max(filled, 1))

    same_window = trades_df[
        (trades_df["stock_id"] == stock_id)
        & (trades_df["executed_at"] >= window)
        & (trades_df["trader_id"] != trader_id)
    ]
    account_coordination_score = float(len(same_window["trader_id"].unique()) / 10.0)

    insider_proximity_score = 0.0
    sentiment_momentum = 0.0
    social_burst_intensity = 0.0

    prices = stock_trades.sort_values("executed_at")["price"].values
    if len(prices) >= 3:
        price_acceleration_score = float((prices[-1] - prices[-3]) / max(prices[-3], 0.01))
    else:
        price_acceleration_score = 0.0

    if len(prices) >= 5:
        abnormal_volatility_score = float(np.std(prices[-5:]) / max(np.mean(prices[-5:]), 0.01))
    else:
        abnormal_volatility_score = 0.0

    values = np.array(
        [
            trade_size_ratio,
            trader_stock_frequency,
            event_window_distance,
            abnormal_profit_ratio,
            intraday_volume_spike,
            cancel_to_fill_ratio,
            account_coordination_score,
            insider_proximity_score,
            sentiment_momentum,
            social_burst_intensity,
            price_acceleration_score,
            abnormal_volatility_score,
        ],
        dtype=float,
    )

    return FeatureVector(values=values, names=FEATURE_NAMES.copy(), metadata={"trader_id": trader_id, "stock_id": stock_id})
