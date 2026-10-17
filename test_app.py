import os
import sqlite3
import tempfile

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture(scope="module", autouse=True)
def db_path():
    path = os.path.join(tempfile.mkdtemp(), "test.db")
    os.environ["DB_PATH"] = path
    yield path


def test_app_loads_without_errors():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert not at.exception
    assert "Rural Telemedicine" in at.title[0].value


def test_database_table_is_created(db_path):
    AppTest.from_file("app.py", default_timeout=30).run()
    conn = sqlite3.connect(db_path)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    conn.close()
    assert "appointments" in tables


def test_language_toggle_changes_title():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].select_index(1).run()
    assert not at.exception
    assert "Rural Telemedicine" not in at.title[0].value


def test_wrong_doctor_password_is_rejected():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.radio[0].set_value("Doctor Panel").run()
    at.text_input[0].input("wrong-password").run()
    assert len(at.warning) == 1