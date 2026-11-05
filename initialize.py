from sqlalchemy import func, select

from app.bootstrap_demo import main as bootstrap_demo
from app.database import Base, SessionLocal, engine
from app.models import Engine


def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(Engine)) or 0
    if count == 0:
        bootstrap_demo()
    else:
        print(f"Database already contains {count} engines; preserving existing data.")


if __name__ == "__main__":
    main()
