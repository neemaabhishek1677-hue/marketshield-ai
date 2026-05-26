import os
import sys
from sqlalchemy.orm import Session

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(BACKEND_ROOT)

from app.database import SessionLocal
from app.models.market import Stock, MarketBarDaily, MarketBarIntraday

def run_diagnostics():
    db: Session = SessionLocal()
    try:
        print("\n==================================================")
        print("📊 MARKETSHIELD-AI STORAGE DIAGNOSTIC REPORT")
        print("==================================================")
        
        stocks_count = db.query(Stock).count()
        daily_count = db.query(MarketBarDaily).count()
        intraday_count = db.query(MarketBarIntraday).count()
        
        print(f"🔹 Total Unique Registered Stocks : {stocks_count}")
        print(f"🔹 Total Macro Daily Price Bars   : {daily_count}")
        print(f"🔹 Total Micro Intraday Records   : {intraday_count}")
        
        if stocks_count > 0:
            print("\n💡 Sample Active Registered Assets:")
            for s in db.query(Stock).limit(3).all():
                print(f"   -> [{s.symbol}] Exchange: {s.exchange} | Active: {s.is_active}")
                
        print("==================================================\n")
    finally:
        db.close()

if __name__ == "__main__":
    run_diagnostics()