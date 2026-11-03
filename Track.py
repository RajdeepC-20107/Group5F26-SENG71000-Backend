from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class TrackBase(SQLModel):
    from_date: datetime
    to_date: datetime
    user_id: int = Field(foreign_key="users.user_id", index=True)


class Track(TrackBase, table=True):
    __tablename__ = "track"
    track_id: int = Field(default=None, primary_key=True)
    from_date: datetime = Field(default=datetime.now(timezone.utc), index=True)
    to_date: datetime = Field(default=datetime.now(timezone.utc), index=True)
    object: str = Field()
    user_id: int = Field(foreign_key="users.user_id", index=True)
