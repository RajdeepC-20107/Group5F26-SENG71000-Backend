import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import supabase

app = FastAPI()
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

"""Responsible for getting scores, tracks, and penalties for a user AB #52"""

@app.get("/users/{user_id}/scores")
def get_scores(user_id: int):
    user = (
        supabase.table("Users")
        .select("user_id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")

    result = (
        supabase.table("DriverScores")
        .select("score_id, score, scoring_notes, "
                "Tracks(start_time, end_time, track_object), "
                "Penalties(occurred_at, penalty_type)")
        .eq("user_id", user_id)
        .execute()
    )

    return result.data or []

"""Handles user login via username or driver license number AB #53"""

class LoginRequest(BaseModel):
    identifier: str
    password: str

@app.post("/login")
def login(req: LoginRequest):
    rows = (
        supabase.table("Users")
        .select("*")
        .or_(f"username.eq.{req.identifier},driver_license_number.eq.{req.identifier}")
        .limit(1)
        .execute()
        .data
    )

    if rows and len(rows) == 1:
        user = rows[0]

        if not check_password(req.password, rows[0]["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        return {
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "profile_score": user["profile_score"],
        }
    elif len(rows) == 0:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    else:
        raise HTTPException(status_code=500)
