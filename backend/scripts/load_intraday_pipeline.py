import os
import sys
import asyncio
import pandas as pd
from sqlalchemy import select

# ==============================================================================
# ZERO-COMPROMISE ABSOLUTE PATH RESOLUTION
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(SCRIPT_DIR)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.core.database import AsyncSessionLocal
from app.models.entities import Stock, MarketBarDaily, MarketBarIntraday


async def run_high_efficiency_pipeline(data_directory: str):
    print("==================================================================")
    print("🚀 MarketShield-AI: Vectorized Intraday Ingestion Engine v2.0")
    print(f"📂 Targeted Asset Directory: {data_directory}")
    print("==================================================================")

    if not os.path.exists(data_directory):
        print(f"❌ Operational Fault: Folder context path '{data_directory}' does not exist.")
        return

    csv_files = [f for f in os.listdir(data_directory) if f.endswith(".csv")]
    if not csv_files:
        print("⚠️ Exception: No matching raw CSV assets found to synchronize.")
        return

    async with AsyncSessionLocal() as db:
        try:
            for file_name in csv_files:
                symbol = os.path.splitext(file_name)[0].upper().replace("_MINUTE", "").strip()
                file_path = os.path.join(data_directory, file_name)

                print(f"\n⚡ Synthesizing High-Frequency Stream for Asset Node: [{symbol}]")

                result = await db.execute(select(Stock).where(Stock.symbol == symbol))
                stock = result.scalar_one_or_none()

                if not stock:
                    stock = Stock(
                        symbol=symbol,
                        company_name=f"{symbol} India Asset Ltd",
                        exchange="NSE",
                        is_active=True
                    )
                    db.add(stock)
                    await db.commit()

                print("   📥 Streaming chunks and extracting structural text fields...")
                chunks = pd.read_csv(file_path, chunksize=50000)

                master_daily_tracker = {}

                for chunk in chunks:
                    chunk.columns = [str(col).strip().upper() for col in chunk.columns]
                    time_col = next(
                        (c for c in ["DATE", "TIMESTAMP", "DATETIME", "DATE & TIME"] if c in chunk.columns),
                        chunk.columns[0]
                    )

                    chunk["PARSED_TIME"] = pd.to_datetime(chunk[time_col], errors="coerce")
                    chunk = chunk.dropna(subset=["PARSED_TIME"])

                    chunk["PARSED_DATE"] = chunk["PARSED_TIME"].dt.date

                    if "VOLUME" not in chunk.columns:
                        chunk["VOLUME"] = 0

                    chunk_summary = chunk.groupby("PARSED_DATE").agg(
                        open_price=("OPEN", "first"),
                        high_price=("HIGH", "max"),
                        low_price=("LOW", "min"),
                        close_price=("CLOSE", "last"),
                        volume_total=("VOLUME", "sum")
                    )

                    for date_key, metrics in chunk_summary.iterrows():
                        if date_key not in master_daily_tracker:
                            master_daily_tracker[date_key] = {
                                "open": metrics["open_price"],
                                "high": metrics["high_price"],
                                "low": metrics["low_price"],
                                "close": metrics["close_price"],
                                "volume": int(metrics["volume_total"])
                            }
                        else:
                            master_daily_tracker[date_key]["high"] = max(
                                master_daily_tracker[date_key]["high"],
                                metrics["high_price"]
                            )
                            master_daily_tracker[date_key]["low"] = min(
                                master_daily_tracker[date_key]["low"],
                                metrics["low_price"]
                            )
                            master_daily_tracker[date_key]["close"] = metrics["close_price"]
                            master_daily_tracker[date_key]["volume"] += int(metrics["volume_total"])

                    intraday_records_batch = [
                        {
                            "symbol": symbol,
                            "timestamp": row["PARSED_TIME"],
                            "open_price": float(row["OPEN"]),
                            "high_price": float(row["HIGH"]),
                            "low_price": float(row["LOW"]),
                            "close_price": float(row["CLOSE"]),
                            "volume": int(row["VOLUME"])
                        }
                        for _, row in chunk.iterrows()
                    ]

                    if intraday_records_batch:
                        await db.run_sync(
                            lambda sync_session: sync_session.bulk_insert_mappings(
                                MarketBarIntraday, intraday_records_batch
                            )
                        )
                        await db.commit()

                print(f"   📊 Finalizing summary updates to 'market_bars_daily' for {symbol}...")

                daily_records_batch = [
                    {
                        "symbol": symbol,
                        "timestamp": dt,
                        "open_price": float(vals["open"]),
                        "high_price": float(vals["high"]),
                        "low_price": float(vals["low"]),
                        "close_price": float(vals["close"]),
                        "volume": int(vals["volume"])
                    }
                    for dt, vals in master_daily_tracker.items()
                ]

                if daily_records_batch:
                    await db.run_sync(
                        lambda sync_session: sync_session.bulk_insert_mappings(
                            MarketBarDaily, daily_records_batch
                        )
                    )
                    await db.commit()

                print(f"   ✅ Finished processing {symbol} successfully!")

            print("\n🎉 Verification Pipeline completed. Data layers are locked and loaded.")

        except Exception as e:
            await db.rollback()
            print(f"❌ Processing Core Failure: {str(e)}")


if __name__ == "__main__":
    TARGET_DIR = os.path.join(BACKEND_ROOT, "data", "raw_intraday")
    asyncio.run(run_high_efficiency_pipeline(TARGET_DIR))