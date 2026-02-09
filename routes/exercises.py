from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from models.exercise import Exercise

exercise_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


@exercise_bp.route("/", methods=["GET"])
def get_exercises():
    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        exercises = session.query(Exercise).all()
        data = [
            {
                "id": ex.id,
                "name": ex.name,
                "muscle_group": ex.muscle_group,
                "equipment_type": ex.equipment_type,
            }
            for ex in exercises
        ]
        return jsonify(data), 200
    finally:
        session.close()
