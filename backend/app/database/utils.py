from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import func



def model_to_json(model: DeclarativeBase) -> dict:
    return func.json_build_object(*[
        item for col in model.__table__.columns 
        for item in [col.name, col]
    ])
