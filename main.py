import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import AwareDatetime, BaseModel, model_validator
from db import supabase
from scoring import PenaltyType, calculate_score

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

"""Receives a finished drive from the app, scores it and saves it"""

class PenaltyUpload(BaseModel):
    occurred_at: AwareDatetime
    penalty_type: PenaltyType

class DriveUpload(BaseModel):
    start_time: AwareDatetime
    end_time: AwareDatetime
    track_object: str | None = None
    penalties: list[PenaltyUpload] = []

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        for p in self.penalties:
            if not self.start_time <= p.occurred_at <= self.end_time:
                raise ValueError("Every penalty's occurred_at must be between start_time and end_time")
        return self

def delete_drive(track_id, score_id):
    """Best-effort removal of a partly saved drive so a failed upload leaves nothing behind.
    Each delete is tried separately so one failing doesn't stop the others."""
    steps = []
    if score_id is not None:
        steps.append(("Penalties", "driving_score_id", score_id))
        steps.append(("DriverScores", "score_id", score_id))
    steps.append(("Tracks", "track_id", track_id))
    for table, column, value in steps:
        try:
            supabase.table(table).delete().eq(column, value).execute()
        except Exception:
            pass

def update_profile_score(user_id: int):
    """Sets the user's profile_score to the average of all their drive scores"""
    scores = supabase.table("DriverScores").select("score").eq("user_id", user_id).execute().data
    if not scores:
        return None
    profile_score = round(sum(row["score"] for row in scores) / len(scores))
    supabase.table("Users").update({"profile_score": profile_score}).eq("user_id", user_id).execute()
    return profile_score

@app.post("/users/{user_id}/drives", status_code=201)
def upload_drive(user_id: int, drive: DriveUpload):
    user = (
        supabase.table("Users")
        .select("user_id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")

    score, notes = calculate_score(p.penalty_type for p in drive.penalties)

    track_row = {
        "start_time": drive.start_time.isoformat(),
        "end_time": drive.end_time.isoformat(),
    }
    if drive.track_object is not None:
        track_row["track_object"] = drive.track_object
    track = supabase.table("Tracks").insert(track_row).execute().data[0]

    score_id = None
    try:
        score_row = supabase.table("DriverScores").insert({
            "user_id": user_id,
            "track_id": track["track_id"],
            "score": score,
            "scoring_notes": notes,
        }).execute().data[0]
        score_id = score_row["score_id"]

        if drive.penalties:
            supabase.table("Penalties").insert([
                {"driving_score_id": score_id,
                 "occurred_at": p.occurred_at.isoformat(),
                 "penalty_type": p.penalty_type}
                for p in drive.penalties
            ]).execute()
    except Exception:
        delete_drive(track["track_id"], score_id)
        raise HTTPException(status_code=500, detail="Could not save the drive")

    # The drive is already saved, so a failure here must not make the app retry and upload it twice
    try:
        profile_score = update_profile_score(user_id)
    except Exception:
        profile_score = None

    return {
        "score_id": score_id,
        "track_id": track["track_id"],
        "score": score,
        "scoring_notes": notes,
        "profile_score": profile_score,
    }
