from flask import Blueprint, jsonify, request

from db import get_session
from models.exercise import Exercise

exercise_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


@exercise_bp.route("/", methods=["GET"])
def get_exercises():
    name = request.args.get("name", type=str)
    
    with get_session() as session:
        q = session.query(Exercise)
        
        if name:
            q = q.filter(Exercise.name.ilike(f"%{name}%"))
        
        exercises = q.order_by(Exercise.name).all()
        
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
