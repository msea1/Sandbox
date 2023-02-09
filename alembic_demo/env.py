from logging.config import fileConfig

from alembic import context
from alembic.operations import ops
from alembic.script import write_hooks
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config  # type: ignore

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.
    In this scenario we need to create an Engine and associate a connection with the context.
    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(_context, _revision, directives):
        add_updated_at_trigger(directives, "updated_at")
        drop_updated_at_trigger(directives)
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


# If we are creating a table with an updated_at column, add a trigger to automatically update
# its value with the latest timestamp upon any update to a row in that table.
def add_updated_at_trigger(directives: list, col_name: str):
    if not directives:
        return
    db_ops = directives[0].upgrade_ops.ops
    new_ops = []
    for op in db_ops:
        if isinstance(op, ops.CreateTableOp):
            for index, col in enumerate(op.columns):
                if getattr(col, "key", "") == col_name:
                    new_op = create_auto_update_trigger(op.table_name)
                    new_ops.append(new_op)
                    break
    db_ops.extend(new_ops)


# If we are dropping a table, try to drop the updated_at trigger as well
# It may not exist which is fine since covered by IF EXISTS
def drop_updated_at_trigger(directives: list):
    if not directives:
        return
    db_ops = directives[0].downgrade_ops.ops
    new_ops = []
    for op in db_ops:
        if isinstance(op, ops.DropTableOp):
            new_op = delete_auto_update_trigger(op.table_name)
            new_ops.append(new_op)
    db_ops[0:0] = new_ops  # prepend list


def create_auto_update_trigger(table_name: str) -> ops.ExecuteSQLOp:
    trigger_name = f"update_{table_name}_modtime"
    trigger_sql = f"BEFORE UPDATE ON {table_name} FOR EACH ROW EXECUTE PROCEDURE set_updated_at()"
    return ops.ExecuteSQLOp(sqltext=f"CREATE TRIGGER {trigger_name} {trigger_sql}")


def delete_auto_update_trigger(table_name: str) -> ops.ExecuteSQLOp:
    trigger_name = f"update_{table_name}_modtime"
    return ops.ExecuteSQLOp(sqltext=f"DROP TRIGGER IF EXISTS {trigger_name} ON {table_name}")


@write_hooks.register("python_hook")
def sample_python_hook(_filename, _options):
    pass
