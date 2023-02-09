from contextlib import redirect_stdout

from alembic import command
from alembic.config import Config

# run existing migrations
alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")
command.revision(alembic_cfg, autogenerate=True)
with open("schema.sql", "w+") as f:
    with redirect_stdout(f):
        command.upgrade(alembic_cfg, "head", sql=True)
