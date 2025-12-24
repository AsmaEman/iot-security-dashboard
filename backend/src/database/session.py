from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import os

# Mock database session for development
class MockAsyncSession:
    """Mock async session for development without database"""
    
    async def execute(self, query):
        # Return mock result
        class MockResult:
            def scalars(self):
                return MockScalars()
            def scalar(self):
                return 0
            def scalar_one_or_none(self):
                return None
        return MockResult()
    
    async def commit(self):
        pass
    
    async def refresh(self, obj):
        pass
    
    async def delete(self, obj):
        pass

class MockScalars:
    def all(self):
        return []
    
    def first(self):
        return None

# Dependency to get database session
async def get_db():
    """Get database session - returns mock session for development"""
    return MockAsyncSession()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://iotuser:iotpass123@localhost:5432/iotdb")

# Create async engine (commented out for mock mode)
# engine = create_async_engine(DATABASE_URL, echo=True)
# AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# async def get_db():
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()