"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

from alembic import context


def upgrade():
    schema_upgrades()
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_upgrades()

    import os
    if os.getenv("ENVIRONMENT") in ["LOCAL", "PYTEST"]: 
        from loguru import logger
        logger.opt(colors=True).info("Success migration [ <green>OK</green> ]")
    else:
        pg_user = "user_template_service"
        pg_schema = "template_schema"
        op.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {pg_schema} TO {pg_user}")
        op.execute(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {pg_schema} TO {pg_user}")
        op.execute(f"GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA {pg_schema} TO {pg_user}")

def downgrade():
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_downgrades()
    schema_downgrades()

def schema_upgrades():
    """schema upgrade migrations go here."""
    ${upgrades if upgrades else "pass"}

def schema_downgrades():
    """schema downgrade migrations go here."""
    ${downgrades if downgrades else "pass"}

def data_upgrades():
    """Add any optional data upgrade migrations here!"""
    pass

def data_downgrades():
    """Add any optional data downgrade migrations here!"""
    pass