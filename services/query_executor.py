from sqlalchemy import text
from database.database import get_db

class QueryExecutor:
    async def execute_query(self, sql_query: str):
        async for session in get_db():
            try:
                result = await session.execute(text(sql_query))
                value = result.scalar()
                return value
            except Exception as e:
                return f"Error executing query: {e}"
