from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Database Configuration
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_rbgtUJ63IuDH@ep-rough-dawn-a45dikld-pooler.us-east-1.aws.neon.tech/rehema123?sslmode=require&channel_binding=require"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
