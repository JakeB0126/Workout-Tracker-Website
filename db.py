from sqlalchemy import create_engine, text, select

engine = create_engine(
    "postgresql+psycopg2://workout:Koanda@127.0.0.1:5433/workout_dev"
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.scalar())

