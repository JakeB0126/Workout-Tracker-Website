from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from models.base import Base


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    order_index = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "workout_id",
            "order_index",
            name="uq_workout_exercises_workout_order",
        ),
    )
