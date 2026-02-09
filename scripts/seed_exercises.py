from db import get_session
from models.exercise import Exercise

EXERCISES = [
    {"name": "Back Squat", "muscle_group": "Legs", "equipment_type": "Barbell"},
    {"name": "Front Squat", "muscle_group": "Legs", "equipment_type": "Barbell"},
    {"name": "Romanian Deadlift", "muscle_group": "Hamstrings", "equipment_type": "Barbell"},
    {"name": "Conventional Deadlift", "muscle_group": "Back", "equipment_type": "Barbell"},
    {"name": "Bench Press", "muscle_group": "Chest", "equipment_type": "Barbell"},
    {"name": "Incline Dumbbell Press", "muscle_group": "Chest", "equipment_type": "Dumbbell"},
    {"name": "Overhead Press", "muscle_group": "Shoulders", "equipment_type": "Barbell"},
    {"name": "Lateral Raise", "muscle_group": "Shoulders", "equipment_type": "Dumbbell"},
    {"name": "Pull-Up", "muscle_group": "Back", "equipment_type": "Bodyweight"},
    {"name": "Lat Pulldown", "muscle_group": "Back", "equipment_type": "Cable"},
    {"name": "Barbell Row", "muscle_group": "Back", "equipment_type": "Barbell"},
    {"name": "Seated Cable Row", "muscle_group": "Back", "equipment_type": "Cable"},
    {"name": "Bicep Curl", "muscle_group": "Arms", "equipment_type": "Dumbbell"},
    {"name": "Hammer Curl", "muscle_group": "Arms", "equipment_type": "Dumbbell"},
    {"name": "Triceps Pushdown", "muscle_group": "Arms", "equipment_type": "Cable"},
    {"name": "Skull Crusher", "muscle_group": "Arms", "equipment_type": "EZ Bar"},
    {"name": "Walking Lunge", "muscle_group": "Legs", "equipment_type": "Dumbbell"},
    {"name": "Leg Press", "muscle_group": "Legs", "equipment_type": "Machine"},
    {"name": "Calf Raise", "muscle_group": "Calves", "equipment_type": "Machine"},
    {"name": "Plank", "muscle_group": "Core", "equipment_type": "Bodyweight"},
]


def seed_data() -> None:
    with get_session() as session:
        try:
            existing_names = {name for (name,) in session.query(Exercise.name).all()}

            new_exercises = [
                Exercise(**exercise)
                for exercise in EXERCISES
                if exercise["name"] not in existing_names
            ]

            if not new_exercises:
                print("No new exercises to insert. Seed is already up to date.")
                return

            session.add_all(new_exercises)
            session.commit()
            print(f"Inserted {len(new_exercises)} exercises.")
        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    seed_data()
