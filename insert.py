from db import supabase
from main import hash_password

user = supabase.table("Users").insert({
    "username": "sfterefe",
    "password_hash": hash_password("password123"),
    "driver_license_number": "T-1234-56789-40405",
    "full_name": "Sifan Terefe",
    "profile_score": 67,
}).execute().data[0]


track = supabase.table("Tracks").insert({
    "start_time": "2026-11-05T08:00:00Z",
    "end_time": "2026-11-05T08:31:00Z",
    "track_object": "tracks/sample.gpx.gz",
}).execute().data[0]

score = supabase.table("DriverScores").insert({
    "user_id": user["user_id"],
    "track_id": track["track_id"],
    "score": 67,
    "scoring_notes": "One harsh braking event",
}).execute().data[0]

supabase.table("Penalties").insert([
    {"driving_score_id": score["score_id"],
     "occurred_at": "2026-11-05T08:14:00Z",
     "penalty_type": "hard_brake"},
]).execute()

print("Inserted user", user["user_id"])