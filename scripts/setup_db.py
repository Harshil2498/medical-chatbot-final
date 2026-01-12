import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from app.models.database import Base
from app.config import get_settings


def setup_database():
    """Create database tables"""
    print("\n" + "="*60)
    print("🗄️  DATABASE SETUP")
    print("="*60 + "\n")
    
    settings = get_settings()
    
    print(f"📍 Connecting to: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    print("📊 Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ Database setup complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    setup_database()