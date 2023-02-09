from sqlalchemy import column
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import table


engine = create_engine("sqlite://")

engine.execute("CREATE TABLE foo (id integer)")
engine.execute("INSERT INTO foo (id) VALUES (1)")


foo = table("foo", column("id"))
result = engine.execute(select([foo.c.id]))

print(result.fetchall())
