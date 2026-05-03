from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = "sqlite:///kanban_data.db"

# Create engine
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """Fungsi untuk membuat semua tabel yang terdaftar di Base"""
    # Import model here to avoid circular import
    from models.task import Task 
    Base.metadata.create_all(bind=engine)
    print("Database terinisialisasi di src/config/db.py")
