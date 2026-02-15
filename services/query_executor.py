from sqlalchemy import text
from database.database import get_db

class QueryExecutor:
    async def execute_query(self, sql_query: str):
        async for session in get_db():
            try:
                # Use execute with text() for raw SQL
                result = await session.execute(text(sql_query))
                # Fetch the single scalar value
                value = result.scalar()
                return value
            except Exception as e:
                # In a real app, strict error handling/logging
                return f"Error executing query: {e}"
