from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

with engine.connect() as conn:
    print("Connected to RDS successfully.\n")

    print("Tables in public schema:")
    tables = conn.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """))

    table_names = [row[0] for row in tables]
    for name in table_names:
        print("-", name)

    print("\nSample rows from trading_signals:")
    result1 = conn.execute(text('SELECT * FROM trading_signals LIMIT 5;'))
    for row in result1:
        print(row)

    print("\nSample rows from equity_curve:")
    result2 = conn.execute(text('SELECT * FROM equity_curve LIMIT 5;'))
    for row in result2:
        print(row)