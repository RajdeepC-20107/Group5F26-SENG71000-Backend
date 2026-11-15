import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import supabase

app = FastAPI()
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

#Responsible for getting scores, tracks, and penalties for a user AB #52
@app.get("/users/{user_id}/scores")
def get_scores(user_id: int):
    result = (
        supabase.table("DriverScores")
        .select("score_id, score, scoring_notes, "
                "Tracks(start_time, end_time, track_object), "
                "Penalties(occurred_at, penalty_type)")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data