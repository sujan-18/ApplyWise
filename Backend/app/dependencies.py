
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.token import SECRET_KEY, ALGORITHM


# Extracts the Bearer token from the Authorization header
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:

    # Get the actual JWT string from the credentials
    token = credentials.credentials

    # Exception returned when authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify the token's signature and expiration
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        # Read the user ID from the JWT payload
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # Convert the user ID from string to integer
        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception

    # Find the user in the database
    statement = select(User).where(User.id == user_id)
    user = db.scalar(statement)

    # Reject the token if the user no longer exists
    if user is None:
        raise credentials_exception

    # Return the authenticated SQLAlchemy User object
    return user
