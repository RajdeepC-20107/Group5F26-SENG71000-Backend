import traceback

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from sqlmodel import SQLModel, Field


password_hasher = PasswordHasher()


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    full_name: str = Field(max_length=255, nullable=False)

    @staticmethod
    def hash_password(password: str) -> str:
        return password_hasher.hash(password)

    def verify_password(self, password: str) -> bool:
        try:
            return password_hasher.verify(
                self.password_hash,
                password,
            )
        except (VerifyMismatchError, VerificationError):
            traceback.print_exc()
            return False