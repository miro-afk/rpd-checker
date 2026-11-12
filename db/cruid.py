from sqlalchemy.orm import Session, joinedload
from . import db_models as models
from .database import get_db

def get_required_headers():
    Session= get_db()
    with Session() as session:
        headers = session.query(models.Headers).all()
    result = []
    for header in headers:
        result.append(header.content)
    return result

def get_competentions():
    Session= get_db()
    with Session() as session:
        competentions = session.query(models.Competentions).all()
    result = []
    for competention in competentions:
        result.append(competention.content)
    return result

if __name__ == "__main__":
    print(get_required_headers())
    print(get_competentions())