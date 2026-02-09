from flask import Blueprint, jsonify

from db import get_session
from models.exercise import Exercise

exercise_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


@exercise_bp.route("/", methods=["GET"])
def get_exercises():
    with get_session() as session:
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
