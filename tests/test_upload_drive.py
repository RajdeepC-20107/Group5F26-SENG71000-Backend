from fastapi.testclient import TestClient

from db import supabase
from scoring import MAX_SCORE, PENALTY_WEIGHTS

# Same test data assumptions as test_scores.py:
# a user with user_id of 1 exists, and no user exists with user_id -1

DRIVE = {
    "start_time": "2026-11-18T08:00:00Z",
    "end_time": "2026-11-18T08:30:00Z",
    "track_object": "tracks/test-upload.gpx.gz",
    "penalties": [
        {"occurred_at": "2026-11-18T08:10:00Z", "penalty_type": "hard_brake"},
        {"occurred_at": "2026-11-18T08:20:00Z", "penalty_type": "speeding"},
    ],
}


def test_upload_drive(client: TestClient):
    original_profile_score = (
        supabase.table("Users").select("profile_score").eq("user_id", 1).execute().data[0]["profile_score"]
    )

    response = client.post("/users/1/drives", json=DRIVE)
    body = response.json()

    try:
        assert response.status_code == 201
        assert body["score"] == MAX_SCORE - PENALTY_WEIGHTS["hard_brake"] - PENALTY_WEIGHTS["speeding"]
        assert body["profile_score"] is not None

        # The new drive shows up in the existing scores endpoint
        scores = client.get("/users/1/scores").json()
        uploaded = [s for s in scores if s["score_id"] == body["score_id"]]
        assert len(uploaded) == 1
        assert uploaded[0]["Tracks"]["track_object"] == DRIVE["track_object"]
        assert len(uploaded[0]["Penalties"]) == 2
    finally:
        # Remove the test drive so the shared database stays as it was
        if response.status_code == 201:
            supabase.table("Penalties").delete().eq("driving_score_id", body["score_id"]).execute()
            supabase.table("DriverScores").delete().eq("score_id", body["score_id"]).execute()
            supabase.table("Tracks").delete().eq("track_id", body["track_id"]).execute()
        supabase.table("Users").update({"profile_score": original_profile_score}).eq("user_id", 1).execute()


def test_upload_drive_nonexistent_user(client: TestClient):
    response = client.post("/users/-1/drives", json=DRIVE)
    assert response.status_code == 404


def test_upload_drive_end_before_start(client: TestClient):
    drive = {**DRIVE, "start_time": DRIVE["end_time"], "end_time": DRIVE["start_time"], "penalties": []}
    response = client.post("/users/1/drives", json=drive)
    assert response.status_code == 422


def test_upload_drive_penalty_outside_drive(client: TestClient):
    drive = {**DRIVE, "penalties": [{"occurred_at": "2026-11-18T09:00:00Z", "penalty_type": "hard_brake"}]}
    response = client.post("/users/1/drives", json=drive)
    assert response.status_code == 422


def test_upload_drive_unknown_penalty_type(client: TestClient):
    drive = {**DRIVE, "penalties": [{"occurred_at": "2026-11-18T08:10:00Z", "penalty_type": "texting_while_parked"}]}
    response = client.post("/users/1/drives", json=drive)
    assert response.status_code == 422


def test_upload_drive_time_without_timezone(client: TestClient):
    drive = {**DRIVE, "start_time": "2026-11-18T08:00:00", "penalties": []}
    response = client.post("/users/1/drives", json=drive)
    assert response.status_code == 422
