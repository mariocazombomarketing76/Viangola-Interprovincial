import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# Em desenvolvimento local não é preciso configurar nada: usa SQLite.
# Em produção defina DATABASE_URL com o PostgreSQL (ver README.md).
DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///./viangola.db"
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# O FastAPI executa os endpoints síncronos num threadpool, por isso o
# SQLite precisa de aceitar ligações fora do thread principal.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()