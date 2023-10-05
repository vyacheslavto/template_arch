import pytest
from pytest_alembic import create_alembic_fixture
from pytest_alembic import tests

# The argument here represents the equivalent to `alembic_config`. Depending
# on your setup, this may be configuring the "file" argument, "script_location",
# or some other way of configuring one or the other of your histories.
history = create_alembic_fixture({"file": "alembic.ini"})


@pytest.mark.usefixtures("migrations_clean_up")
class TestMigrations:
    def test_single_head_revision(self, history):
        tests.test_single_head_revision(history)

    def test_upgrade(self, history):
        tests.test_upgrade(history)

    def test_model_definitions_match_ddl(self, history):
        tests.test_model_definitions_match_ddl(history)

    @pytest.mark.slow
    def test_up_down_consistency(self, history):
        tests.test_up_down_consistency(history)
