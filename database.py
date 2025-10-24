import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') 

# ساخت موتور آسنکرون
engine = create_async_engine(DATABASE_URL)

# ساخت یک SessionMaker آسنکرون
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    autocommit=False, 
    autoflush=False,
    expire_on_commit=False # این گزینه در حالت async معمولا توصیه می‌شود
)

# وابستگی (Dependency) جدید برای تزریق سشن به اندپوینت‌ها
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()