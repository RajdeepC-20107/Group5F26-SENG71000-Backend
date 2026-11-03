import xml.etree.ElementTree as ET
from datetime import timedelta, timezone, datetime
from pathlib import Path
from typing import Annotated

import jwt
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlmodel import Session

import grading
from Track import Track
from User import User
from database import get_db

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SECRET_KEY = "ce261522995e9a818ebff24415c22221c725bccf400a993d020b83a2b9eebeef"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("sub") is None:
            raise credentials_exception

        return payload

    except jwt.InvalidTokenError:
        raise credentials_exception


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    payload = decode_access_token(token)

    email = payload["sub"]

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    user = db.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user or not user.verify_password(password=form_data.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_gpx_datetimes(path: Path) -> tuple[datetime, datetime] | None:
    times: list[datetime] = []

    for _, element in ET.iterparse(path, events=("end",)):
        if _localname(element.tag) != "trkpt":
            continue

        for child in element:
            if _localname(child.tag) == "time" and child.text:
                times.append(datetime.fromisoformat(child.text.strip()))

        element.clear()

    if not times:
        return None

    return min(times), max(times)


@app.get("/track/{track_id}")
async def get_track(
    track_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    track = db.scalar(
        select(Track).where(Track.track_id == track_id, Track.user_id == current_user.user_id)
    )

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    return {
        "track_id": track.track_id,
        "score": 100,
        "from_date": track.from_date,
        "to_date": track.to_date
    }


@app.get("/profile")
async def get_profile(
        current_user: Annotated[User, Depends(get_current_user)] = None,
        db: Annotated[Session, Depends(get_db)] = None
):
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "profile_score": grading.profile_score(current_user, db)
    }


@app.post("/track/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    user_dir = UPLOAD_DIR / str(current_user.user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    destination = user_dir / file.filename

    with destination.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    date_range = parse_gpx_datetimes(destination)

    if date_range is None:
        from_date = to_date = datetime.now(timezone.utc)
    else:
        from_date, to_date = date_range

    track = Track(
        from_date=from_date,
        to_date=to_date,
        user_id=current_user.user_id,
        object=f"file:///{destination}"
    )

    db.add(track)
    db.commit()
    db.refresh(track)

    return {
        "track_id": track.track_id,
        "filename": file.filename,
        "size": destination.stat().st_size,
    }