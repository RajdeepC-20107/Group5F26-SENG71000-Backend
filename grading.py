from sqlalchemy.orm import Session

from Track import Track
from User import User


def profile_score(user: User, db: Session):
    return 100


def track_score(track: Track, db: Session):
    return 100
