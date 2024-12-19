# app/auth/utils.py
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from app.dependencies import verify_password, create_access_token
from app.database import users_collection
from app.schemas import UserInDB, TokenData
from app.config import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_user(email: str):
    user_data = users_collection.find_one({"email": email})
    if user_data:
        # Convert the MongoDB _id to a string and include it in the user data
        user_data["id"] = str(user_data["_id"])
        return UserInDB(**user_data)
    return None


def authenticate_user(email: str, password: str):
    user = get_user(email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if email is None or user_id is None:
            raise credential_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credential_exception
    user = get_user(email=token_data.email)
    if user is None:
        raise credential_exception
    return user  # Return the UserInDB object instead of a dictionary

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
