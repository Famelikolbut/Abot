from groq import AsyncGroq
from config.config import settings

class GroqSQLGenerator:
    def __init__(self):
        self.client = AsyncGroq(
            api_key=settings.groq_api_key.get_secret_value()
        )
        self.model_name = "openai/gpt-oss-120b" # As requested by user

    async def generate_sql(self, user_query: str) -> str:
        system_prompt = """
You are an expert PostgreSQL Data Analyst. 
Your task is to convert a natural language question into a valid, executable PostgreSQL SQL query.

The database schema is as follows:

Table: videos (v)
- id (text, PK)
- creator_id (text)
- video_created_at (timestamp with time zone) - When the video was published
- views_count (bigint) - Total views
- likes_count (int) - Total likes
- comments_count (int) - Total comments
- reports_count (int) - Total reports
- created_at (timestamp)
- updated_at (timestamp)

Table: video_snapshots (vs)
- id (text, PK)
- video_id (text, FK -> videos.id)
- views_count (bigint) - Value at snapshot time
- likes_count (int)
- comments_count (int)
- reports_count (int)
- delta_views_count (bigint) - Change since last snapshot
- delta_likes_count (int)
- delta_comments_count (int)
- delta_reports_count (int)
- created_at (timestamp with time zone) - Snapshot time (hourly)

Rules:
1. Return ONLY the SQL query. No markdown formatting (no ```sql), no explanations.
2. The query MUST return exactly ONE row with ONE column (a single number).
3. Use PostgreSQL syntax.
4. Dealing with dates:
   - Current year is 2025 (based on the context of the data).
   - "28 ноября 2025" means '2025-11-28'.
   - Use correct date casting: `WHERE created_at::date = '2025-11-28'`
5. Common logic:
   - "Сколько всего видео?" -> COUNT(*) from videos.
   - "Сколько видео у креатора X?" -> COUNT(*) from videos where creator_id = '...'.
   - "Прирост просмотров за дату X" -> SUM(delta_views_count) from video_snapshots where created_at::date = 'YYYY-MM-DD'.
   - "Сколько видео набрало больше X просмотров?" -> COUNT(*) from videos where views_count > X.
   
CRITICAL: DO NOT OUTPUT JSON. DO NOT USE TOOLS OR FUNCTIONS. JUST OUTPUT THE RAW SQL STRING.
"""
        
        completion = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            temperature=0.1, # Lower temperature for more deterministic SQL
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
            stream=False
        )
        
        sql = completion.choices[0].message.content.strip()
        
        # Cleanup potential markdown formatting
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
            
        return sql.strip()
