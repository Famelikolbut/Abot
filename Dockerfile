FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed for asyncpg/psycopg2 compilation, though binary wheels usually work)
# RUN apt-get update && apt-get install -y gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Command to run the bot
CMD ["python", "main.py"]
