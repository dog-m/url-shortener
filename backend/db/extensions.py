from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression

#


class UniversalWeekday(expression.FunctionElement):
    """A custom SQL function that extracts the day of the week."""
    name = "universal_weekday"
    inherit_cache = True   # SQLAlchemy 1.4/2.0 performance?



# Postgres impl
@compiles(UniversalWeekday, 'postgresql')
def compile_universal_weekday_postgres(element, compiler, **kw):
    # Postgres uses extract('dow', column)
    # compiler.process(element.clauses) ensures the column passed in is correctly formatted
    return f"extract('dow', {compiler.process(element.clauses, **kw)})"


# MySQL impl
@compiles(UniversalWeekday, 'mysql')
def compile_universal_weekday_mysql(element, compiler, **kw):
    # MySQL uses dayofweek(column) that returns 1..7
    return f"(dayofweek({compiler.process(element.clauses, **kw)}) - 1)"


# SQLite impl
@compiles(UniversalWeekday, 'sqlite')
def compile_universal_weekday_sqlite(element, compiler, **kw):
    # SQLite uses strftime('%w', column)
    return f"strftime('%w', {compiler.process(element.clauses, **kw)})"


# "fallback" (if the DB is unknown)
@compiles(UniversalWeekday)
def compile_universal_weekday_default(element, compiler, **kw):
    # This is what happens if you use a DB we haven't defined above
    raise NotImplementedError(f"The current database dialect is not supported for {UniversalWeekday.__name__}")

