from pathlib import Path
from typing import Any, Generator, List

import psycopg2
import pytest
from pytest_postgresql.factories import postgresql_noproc
from pytest_postgresql.janitor import DatabaseJanitor

from src.fakes import FakeCrudService
from src.services import CrudService
from tests.contracts import CrudServiceContract

MIGRATIONS: List[str] = [
    p.as_posix() for p in sorted(Path("db/migrations").glob("*.sql"))
]
ci_pg = postgresql_noproc(
    dbname="ci",
    password="password",
    load=MIGRATIONS,
)


@pytest.fixture(scope="session")
def real_db_conn(ci_pg):
    with DatabaseJanitor(
        user=ci_pg.user,
        port=ci_pg.port,
        dbname=ci_pg.dbname,
        password=ci_pg.password,
        host=ci_pg.host,
        version=ci_pg.version,
    ):
        yield psycopg2.connect(
            database=ci_pg.dbname,
            user=ci_pg.user,
            password=ci_pg.password,
            host=ci_pg.host,
            port=ci_pg.port,
        )


@pytest.fixture
def test_suite() -> CrudServiceContract:
    return CrudServiceContract()


@pytest.fixture(scope="session")
def real_crud_service(real_db_conn) -> Generator[CrudService, Any, Any]:
    yield CrudService(real_db_conn)


@pytest.fixture(scope="session")
def fake_crud_service(real_db_conn) -> Generator[FakeCrudService, Any, Any]:
    yield FakeCrudService(real_db_conn)


@pytest.mark.parametrize("crud_service", ["fake_crud_service", "real_crud_service"])
class TestServices:
    def test_create_user(self, test_suite, crud_service, request):
        service = request.getfixturevalue(crud_service)
        test_suite.create_user(service)

    def test_read_user(self, test_suite, crud_service, request):
        service = request.getfixturevalue(crud_service)
        test_suite.read_user(service)

    def test_update_user(self, test_suite, crud_service, request):
        service = request.getfixturevalue(crud_service)
        test_suite.update_user(service)

    def test_delete_user(self, test_suite, crud_service, request):
        service = request.getfixturevalue(crud_service)
        test_suite.delete_user(service)
