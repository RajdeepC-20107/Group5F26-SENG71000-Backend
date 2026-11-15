import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import supabase

app = FastAPI()
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

'''Responsible for getting scores, tracks, and penalties for a user AB #52'''
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

'''Handles user login via username or driver license number AB #53'''
class LoginRequest(BaseModel):
    identifier: str
    password: str

@app.post("/login")
def login(req: LoginRequest):
    rows = []
    for column in ("username", "driver_license_number"):
        rows = supabase.table("Users").select("*").eq(column, req.identifier).limit(1).execute().data
        if rows:
            break
    if not rows or not check_password(req.password, rows[0]["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    user = rows[0]
    return {
        "user_id": user["user_id"],
        "full_name": user["full_name"],
        "profile_score": user["profile_score"],
    }