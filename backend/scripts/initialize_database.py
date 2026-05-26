import os
import sys
import asyncio

# ==============================================================================
# ZERO-COMPROMISE ABSOLUTE PATH RESOLUTION
# ==============================================================================
# This block must execute before ANY custom app modules are fetched.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(SCRIPT_DIR)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.core.database import engine, Base
from app.models.entities import Stock, MarketBarDaily, MarketBarIntraday


async def init_db():
    print("==================================================================")
    print("🧱 MarketShield-AI: Initializing Relational Table Mappings")
    print("==================================================================")

    try:
        print("🔄 Compiling declarative metadata and pushing structural schema bindings...")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("🎉 Success: All database tables verified and generated without path conflicts!")

    except Exception as e:
        print(f"❌ Structural Initializer Fault: {str(e)}")


if __name__ == "__main__":
    asyncio.run(init_db())