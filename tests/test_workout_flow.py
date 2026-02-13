from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app

def test_main_workout_flow():
    app = create_app()
    client = app.test_client()
    
    # Login
    login_res = client.post("/auth/login", json={"username":"test", "password": "test"})
    assert login_res.status_code == 200
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create workout
    workout_res = client.post(
        "/workouts/",
        json={"name": "Push Day", "started_at": "2026-02-13T18:00:00Z"},
        headers=headers,
    )
    
    assert workout_res.status_code == 201
    workout_id = workout_res.get_json()["id"]
    
    # Add exercise
    add_ex_res = client.post(
        f"/workouts/{workout_id}/exercises",
        json={"exercise_id":1},
        headers=headers,
    )
    assert add_ex_res.status_code == 201
    workout_exercise_id = add_ex_res.get_json()["id"]
    
    # Add set
    add_set_res = client.post(
        f"/workouts/workout-exercises/{workout_exercise_id}/sets",
        json={"set_number": 1, "reps": 10, "weight_lbs": 135, "set_type": 1},
        headers=headers,
    )
    assert add_set_res.status_code == 201
    set_id = add_set_res.get_json()["id"]
    
    # Nested get
    nested_res = client.get(f"/workouts/{workout_id}", headers=headers)
    assert nested_res.status_code == 200
    nested = nested_res.get_json()
    assert nested["id"] == workout_id
    assert len(nested["exercises"]) == 1
    assert len(nested["exercises"][0]["sets"]) == 1
    
    # Delete set
    del_set_res = client.delete(
        f"/workouts/workout-exercises/{workout_exercise_id}/sets/{set_id}",
        headers=headers,
    )
    assert del_set_res.status_code == 200
    
    
