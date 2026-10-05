"""Database configuration for the backend application."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# use SQLite to create a local database file named quicklearner.db in the current directory
DATABASE_URL = "sqlite:///./quicklearner.db"

# create a SQLAlchemy engine and sessionmaker for the database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create a base class for the database models
Base = declarative_base()
