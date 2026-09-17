from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from pwdlib import PasswordHash

from src.config import Settings

PASSWORDS = PasswordHash.recommended()
# Equalize the expensive hash check for an unknown email and a wrong password.
DUMMY_HASH = PASSWORDS.hash("not-a-real-account-password")
ISSUER = "policy-desk"


def issue_token(user_id: int, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=settings.jwt_expiry_minutes),
            "iss": ISSUER,
            "aud": ISSUER,
        },
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )


def unauthorized() -> HTTPException:
    return HTTPException(
        401, "Invalid or expired credentials. Please sign in again.", headers={"WWW-Authenticate": "Bearer"}
    )


def decode_token(token: str, settings: Settings) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=["HS256"],
            issuer=ISSUER,
            audience=ISSUER,
            options={"require": ["exp", "iat", "sub", "iss", "aud"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise unauthorized() from None
