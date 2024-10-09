"""Module to handle LabTracks database session"""

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine

from aind_metadata_service.backends.labtracks.configs import Settings

# Construct a Settings. Can be set via env vars or aws param store.
settings = Settings()

engine = create_engine(url=settings.db_connection_str)

session_local = sessionmaker(
    bind=engine, class_=Session, expire_on_commit=False
)


def get_session() -> Session:
    """Yield a session object. This will automatically close the session when
    finished."""
    session = session_local()
    try:
        yield session
    finally:
        session.close()
