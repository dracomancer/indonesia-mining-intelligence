import os
from sqlalchemy import create_engine, text

DB_USER = "mining_user"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "mining_market"

DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("PostgreSQL connection successful!")
        print(result.fetchone()[0])

except Exception as error:
    print("Connection failed:")
    print(error)

finally:
    engine.dispose()