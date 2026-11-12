from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .db_models import Base, Headers, Competentions
from .base_data import get_requierd_headers,get_competentions

# Конфигурация PostgreSQL
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

# URL для подключения к PostgreSQL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Создаем engine с настройками для PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "40")),
    pool_pre_ping=True,
)

# Создаем фабрику сессий
Session  = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency для получения сессии
def get_db():
    """
    Синхронная зависимость для получения сессии БД
    """
    

    return Session

if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session() as session:
        headers = get_requierd_headers()
        for header in headers:
            session.add(Headers(content = header))
        competentions = get_competentions()
        for competention in competentions:
            session.add(Competentions(content = competention, speciality = "09.03.02"))
        session.commit()