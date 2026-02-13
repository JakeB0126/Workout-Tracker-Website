from datetime import datetime
from decimal import Decimal
from typing import Optional, cast

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from db import get_session
from models.exercise import Exercise
from models.user import User
from models.workout import Workout
from models.workout_exercise import WorkoutExercise
from models.workout_set import WorkoutSet

workout_bp = Blueprint("workouts", __name__, url_prefix="/workouts")


def _parse_iso8601(value: str):
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _get_user_from_identity(session, identity):
    if isinstance(identity, int):
        return session.query(User).filter(User.id == identity).first()
    if isinstance(identity, str) and identity.isdigit():
        return session.query(User).filter(User.id == int(identity)).first()
    if isinstance(identity, str):
        return session.query(User).filter(User.email == identity).first()
    return None

# ADD a workout
@workout_bp.route("/", methods=["POST"])
@jwt_required()
def create_workout():
    payload = request.get_json(silent=True) or {}

    name = payload.get("name")
    started_at_raw = payload.get("started_at")
    ended_at_raw = payload.get("ended_at")

    if not name or not isinstance(name, str) or not name.strip():
        return jsonify({"msg": "name is required"}), 400

    if not started_at_raw or not isinstance(started_at_raw, str):
        return jsonify({"msg": "started_at is required and must be an ISO 8601 string"}), 400

    try:
        started_at = _parse_iso8601(started_at_raw)
        ended_at = _parse_iso8601(ended_at_raw) if ended_at_raw else None
    except ValueError:
        return jsonify({"msg": "Invalid datetime format. Use ISO 8601."}), 400

    if ended_at is not None and ended_at < started_at:
        return jsonify({"msg": "ended_at must be greater than or equal to started_at"}), 400

    identity = get_jwt_identity()

    with get_session() as session:
        user = _get_user_from_identity(session, identity)

        if user is None:
            return jsonify(
                {"msg": "Authenticated user was not found. Login identity must map to a real user."}
            ), 401

        workout = Workout(
            user_id=user.id,
            name=name.strip(),
            started_at=started_at,
            ended_at=ended_at,
        )
        session.add(workout)
        session.commit()
        session.refresh(workout)

    return jsonify(
        {
            "id": workout.id,
            "user_id": workout.user_id,
            "name": workout.name,
            "started_at": workout.started_at.isoformat(),
            "ended_at": workout.ended_at.isoformat() if workout.ended_at is not None else None,
        }
    ), 201

# ADD an exericse to a workout
@workout_bp.route("/<int:workout_id>/exercises", methods=["POST"])
@jwt_required()
def post_workout_exercise(workout_id):
    identity = get_jwt_identity()
    body = request.get_json(silent=True) or {}

    exercise_id = body.get("exercise_id")
    order_index = body.get("order_index")

    if exercise_id is None or not isinstance(exercise_id, int):
        return jsonify({"msg": "exercise_id is required and must be an integer"}), 400

    with get_session() as session:
        user = _get_user_from_identity(session, identity)

        if user is None:
            return jsonify(
                {"msg": "Authenticated user was not found. Login identity must map to a real user."}
            ), 401

        workout = session.query(Workout).filter(Workout.id == workout_id).first()
        if workout is None:
            return jsonify({"msg": "Workout does not exist"}), 404

        owned_workout = (
            session.query(Workout)
            .filter(
                Workout.id == workout_id,
                Workout.user_id == user.id,
            )
            .first()
        )
        if owned_workout is None:
            return jsonify({"msg": "You do not have permission to access this workout"}), 403

        exercise = session.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            return jsonify({"msg": "Exercise does not exist"}), 404

        existing_rows = (
            session.query(WorkoutExercise)
            .filter(WorkoutExercise.workout_id == workout_id)
            .order_by(WorkoutExercise.order_index.asc())
            .all()
        )

        if order_index is None:
            max_order = existing_rows[-1].order_index if existing_rows else 0
            order_index = max_order + 1
        else:
            if not isinstance(order_index, int) or order_index < 1:
                return jsonify({"msg": "order_index must be a positive integer"}), 400

            # Shift existing rows down to keep order_index unique within the workout.
            session.query(WorkoutExercise).filter(
                WorkoutExercise.workout_id == workout.id,
                WorkoutExercise.order_index >= order_index,
            ).update(
                {WorkoutExercise.order_index: WorkoutExercise.order_index + 1},
                synchronize_session=False,
            )

        workout_exercise = WorkoutExercise(
            workout_id=workout.id,
            exercise_id=exercise.id,
            order_index=order_index,
        )
        session.add(workout_exercise)
        session.commit()
        session.refresh(workout_exercise)

    return jsonify(
        {
            "id": workout_exercise.id,
            "workout_id": workout_exercise.workout_id,
            "exercise_id": workout_exercise.exercise_id,
            "order_index": workout_exercise.order_index,
        }
    ), 201

# ADD a set to an exercise
@workout_bp.route("/workout-exercises/<int:workout_exercise_id>/sets", methods=["POST"])
@jwt_required()
def post_workout_set(workout_exercise_id):
    identity = get_jwt_identity()
    body = request.get_json(silent=True) or {}

    set_number = body.get("set_number")
    reps = body.get("reps")
    set_type = body.get("set_type")
    weight_lbs = body.get("weight_lbs")

    if not isinstance(reps, int) or reps <= 0:
        return jsonify({"msg": "reps is required and must be a positive integer"}), 400

    if not isinstance(set_type, int) or set_type not in (0, 1, 2):
        return jsonify({"msg": "set_type is required and must be one of: 0, 1, 2"}), 400

    if set_number is not None and (not isinstance(set_number, int) or set_number <= 0):
        return jsonify({"msg": "set_number must be a positive integer"}), 400

    if weight_lbs is not None:
        if not isinstance(weight_lbs, (int, float)) or weight_lbs < 0:
            return jsonify({"msg": "weight_lbs must be a non-negative number"}), 400

    with get_session() as session:
        user = _get_user_from_identity(session, identity)
        if user is None:
            return jsonify(
                {"msg": "Authenticated user was not found. Login identity must map to a real user."}
            ), 401

        workout_exercise = (
            session.query(WorkoutExercise)
            .filter(WorkoutExercise.id == workout_exercise_id)
            .first()
        )
        if not workout_exercise:
            return jsonify({"msg": "Workout exercise does not exist"}), 404

        workout = session.query(Workout).filter(Workout.id == workout_exercise.workout_id).first()
        if workout is None:
            return jsonify({"msg": "Workout does not exist"}), 404

        owned_workout = (
            session.query(Workout)
            .filter(
                Workout.id == workout_exercise.workout_id,
                Workout.user_id == user.id,
            )
            .first()
        )
        if owned_workout is None:
            return jsonify({"msg": "You do not have permission to access this workout"}), 403

        existing_sets = (
            session.query(WorkoutSet)
            .filter(WorkoutSet.workout_exercise_id == workout_exercise.id)
            .order_by(WorkoutSet.set_number.asc())
            .all()
        )

        if set_number is None:
            max_set_number = existing_sets[-1].set_number if existing_sets else 0
            set_number = max_set_number + 1
        else:
            session.query(WorkoutSet).filter(
                WorkoutSet.workout_exercise_id == workout_exercise.id,
                WorkoutSet.set_number >= set_number,
            ).update(
                {WorkoutSet.set_number: WorkoutSet.set_number + 1},
                synchronize_session=False,
            )

        workout_set = WorkoutSet(
            workout_exercise_id=workout_exercise.id,
            set_number=set_number,
            reps=reps,
            weight_lbs=weight_lbs,
            set_type=set_type,
        )
        session.add(workout_set)
        session.commit()
        session.refresh(workout_set)

    weight_lbs_value = cast(Optional[Decimal], workout_set.weight_lbs)

    return jsonify(
        {
            "id": workout_set.id,
            "workout_exercise_id": workout_set.workout_exercise_id,
            "set_number": workout_set.set_number,
            "reps": workout_set.reps,
            "weight_lbs": float(weight_lbs_value) if weight_lbs_value is not None else None,
            "set_type": workout_set.set_type,
        }
    ), 201

# DELETE exercise from a workout
@workout_bp.route("/<int:workout_id>/exercises/<int:workout_exercise_id>", methods=["DELETE"])
@jwt_required()
def delete_workout_exercise(workout_id, workout_exercise_id):
    identity = get_jwt_identity()

    with get_session() as session:
        user = _get_user_from_identity(session, identity)
        if user is None:
            return jsonify(
                {"msg": "Authenticated user was not found. Login identity must map to a real user."}
            ), 401

        owned_workout = (
            session.query(Workout)
            .filter(
                Workout.id == workout_id,
                Workout.user_id == user.id,
            )
            .first()
        )
        if owned_workout is None:
            return jsonify({"msg": "Workout not found or access denied"}), 404

        workout_exercise = (
            session.query(WorkoutExercise)
            .filter(
                WorkoutExercise.id == workout_exercise_id,
                WorkoutExercise.workout_id == workout_id,
            )
            .first()
        )
        if workout_exercise is None:
            return jsonify({"msg": "Workout exercise does not exist"}), 404

        deleted_order_index = workout_exercise.order_index

        session.query(WorkoutSet).filter(
            WorkoutSet.workout_exercise_id == workout_exercise.id
        ).delete(synchronize_session=False)

        session.delete(workout_exercise)

        session.query(WorkoutExercise).filter(
            WorkoutExercise.workout_id == workout_id,
            WorkoutExercise.order_index > deleted_order_index,
        ).update(
            {WorkoutExercise.order_index: WorkoutExercise.order_index - 1},
            synchronize_session=False,
        )

        session.commit()

    return jsonify({"msg": "Workout exercise deleted"}), 200

# DELETE set from an exercise
@workout_bp.route("/workout-exercises/<int:workout_exercise_id>/sets/<int:set_id>", methods=["DELETE"])
@jwt_required()
def delete_workout_set(workout_exercise_id, set_id):
    identity = get_jwt_identity()

    with get_session() as session:
        user = _get_user_from_identity(session, identity)
        if user is None:
            return jsonify(
                {"msg": "Authenticated user was not found. Login identity must map to a real user."}
            ), 401

        workout_exercise = (
            session.query(WorkoutExercise)
            .filter(WorkoutExercise.id == workout_exercise_id)
            .first()
        )
        if workout_exercise is None:
            return jsonify({"msg": "Workout exercise does not exist"}), 404

        owned_workout = (
            session.query(Workout)
            .filter(
                Workout.id == workout_exercise.workout_id,
                Workout.user_id == user.id,
            )
            .first()
        )
        if owned_workout is None:
            return jsonify({"msg": "Workout not found or access denied"}), 404

        workout_set = (
            session.query(WorkoutSet)
            .filter(
                WorkoutSet.id == set_id,
                WorkoutSet.workout_exercise_id == workout_exercise_id,
            )
            .first()
        )
        if workout_set is None:
            return jsonify({"msg": "Workout set does not exist"}), 404

        deleted_set_number = workout_set.set_number
        session.delete(workout_set)

        session.query(WorkoutSet).filter(
            WorkoutSet.workout_exercise_id == workout_exercise_id,
            WorkoutSet.set_number > deleted_set_number,
        ).update(
            {WorkoutSet.set_number: WorkoutSet.set_number - 1},
            synchronize_session=False,
        )

        session.commit()

    return jsonify({"msg": "Workout set deleted"}), 200

@workout_bp.route("/<int:workout_id>/exercises/reorder", methods=["PATCH"])
@jwt_required()
def reorder_workout_exercises(workout_id):
    identity = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    ordered_ids = body.get("ordered_workout_exercise_ids")
    
    if not isinstance(ordered_ids, list) or not ordered_ids:
        return jsonify({"msg": "ordered_workout_exercise_ids must be a non-empty list"}), 400

    if not all(isinstance(x, int) for x in ordered_ids):
        return jsonify({"msg": "ordered_workout_exercise_ids must contain only integers"}), 400
    
    if len(set(ordered_ids)) != len(ordered_ids):
        return jsonify({"msg": "ordered_workout_exercise_ids contains duplicates"}), 400
    
    with get_session() as session:
        user = _get_user_from_identity(session, identity)
        if user is None:
            return jsonify(
                {"msg": "Authenticated user was not found. Login identity must map to a real user."}
            ), 401
            
        owned_workout = (
                session.query(Workout)
                .filter(
                    Workout.id == workout_id,
                    Workout.user_id == user.id,
                )
                .first()
            )
        if owned_workout is None:
            return jsonify({"msg": "Workout not found or access denied"}), 404
        
        rows = (
            session.query(WorkoutExercise)
            .filter(WorkoutExercise.workout_id == workout_id)
            .order_by(WorkoutExercise.order_index.asc())
            .all()
        )
        
        if not rows:
            return jsonify({"msg": "No exercises found for this workout"}), 404
        
        existing_ids = {row.id for row in rows}
        submitted_ids = set(ordered_ids)
        
        if submitted_ids != existing_ids:
            return jsonify(
                {"msg": "ordered_workout_exercise_ids must include every exercise in this workout exactly once"}
            ), 400
        
        # Re-index to avoid unique constraint collisions.
        for i, row_id in enumerate(ordered_ids, start=1):
            session.query(WorkoutExercise).filter(
                WorkoutExercise.id == row_id,
                WorkoutExercise.workout_id == workout_id,
            ).update(
                {WorkoutExercise.order_index: 1000 + i},
                synchronize_session=False,
            )
        
        session.flush()
        
        for i, row_id in enumerate(ordered_ids, start=1):
            session.query(WorkoutExercise).filter(
                WorkoutExercise.id == row_id,
                WorkoutExercise.workout_id == workout_id,
            ).update(
                {WorkoutExercise.order_index: i},
                synchronize_session=False,
            )
            
        session.commit()
        
    return jsonify(
        {
            "workout_id": workout_id,
            "ordered_workout_exercise_ids": ordered_ids,
        }
    ), 200
    

    
    
        
    
