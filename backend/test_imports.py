#!/usr/bin/env python
"""
Quick test script to verify backend setup.
"""
import sys
import asyncio

async def test_imports():
    """Test if all imports work."""
    try:
        print("Testing imports...")
        from app.core.config import get_settings
        print("✓ Config loaded")
        
        from app.providers.base import MarketDataProvider
        print("✓ Provider base loaded")
        
        from app.providers.finnhub_service import FinnhubService
        print("✓ Finnhub service loaded")
        
        from app.providers.sec_service import SECEDGARService
        print("✓ SEC service loaded")
        
        from app.services.ingestion import MarketIngestionService
        print("✓ Ingestion services loaded")
        
        from app.services.scheduler_service import IngestionScheduler
        print("✓ Scheduler loaded")
        
        from app.main import app
        print("✓ FastAPI app loaded")
        
        print("\n✅ All imports successful!")
        return True
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_imports())
    sys.exit(0 if success else 1)
