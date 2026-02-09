from sqlalchemy import (
    SMALLINT,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
)

from models.base import Base


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True)
    workout_exercise_id = Column(
        Integer,
        ForeignKey("workout_exercises.id"),
        nullable=False,
    )
    set_number = Column(SMALLINT, nullable=False)
    reps = Column(Integer, nullable=False)
    weight_lbs = Column(Numeric(6, 2))
    set_type = Column(SMALLINT, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "workout_exercise_id",
            "set_number",
            name="uq_workout_sets_exercise_set_number",
        ),
        CheckConstraint(
            "set_type IN (0, 1, 2)",
            name="ck_workout_sets_set_type",
        ),
    )
