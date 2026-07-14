"""
Database configuration for SupportFlow.

This module creates the SQLAlchemy engine, session factory, and shared
declarative base used by every database model in the application.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Read the database connection string from the environment.
#
# During local development, SupportFlow defaults to a SQLite database file.
# When DATABASE_URL is set, the same application can connect to PostgreSQL
# without changing the source code.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///supportflow.db")


# SQLite requires this option when the same connection may be used across
# multiple Streamlit execution threads. PostgreSQL does not need it.
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)


# The engine manages connections between SQLAlchemy and the database.
#
# pool_pre_ping=True checks a connection before using it. This helps recover
# from stale connections, especially when using a hosted PostgreSQL database.
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


# SessionLocal is a factory that creates individual database sessions.
#
# Each page opens a session inside a "with" block so that the connection is
# released cleanly after the database work finishes.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """
    Shared parent class for all SQLAlchemy models.

    Customer, Ticket, and TicketUpdate inherit from this class so SQLAlchemy
    can collect their table definitions in one metadata registry.
    """

    pass


def init_db() -> None:
    """
    Create all database tables that do not already exist.

    Importing the models inside this function ensures that SQLAlchemy knows
    about every table before create_all() runs. This function is safe to call
    when the application starts because create_all() does not overwrite
    existing tables.
    """

    # Imported here instead of at the top to avoid a circular import:
    # models.py imports Base from this module.
    from models import Customer, Ticket, TicketUpdate  # noqa: F401

    Base.metadata.create_all(bind=engine)
