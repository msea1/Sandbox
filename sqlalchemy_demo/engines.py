from sqlalchemy import create_engine, Engine


def get_sqlite_memory_db() -> Engine:
    return create_engine("sqlite+pysqlite:///memory:", echo=True)
