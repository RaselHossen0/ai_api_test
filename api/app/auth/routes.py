# app/auth/routes.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import OAuth2PasswordRequestFormEmail, Token, UserCreate
from app.dependencies import create_access_token
from app.auth.utils import authenticate_user

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestFormEmail):
    try:
        user = authenticate_user(form_data.email, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=300)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},  # Add user_id to the token payload
            expires_delta=access_token_expires
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to authenticate user: {str(e)}")
    return {"access_token": access_token, "user_id": user.id}
