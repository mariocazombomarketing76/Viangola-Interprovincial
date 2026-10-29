"""Configuração dos testes — base SQLite dedicada, isolada da base de dev.

A variável DATABASE_URL é definida ANTES de importar qualquer módulo da
aplicação, para que app.db crie o engine contra o ficheiro de teste.
"""

import os
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent / "test_viangola.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: F401,E402 — regista as tabelas no Base
from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    if TEST_DB.exists():
        TEST_DB.unlink()
    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()
