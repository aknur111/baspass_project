

from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import timedelta, datetime
from typing import Annotated

from pydantic import EmailStr

from src.models.auth_2F import Auth_2Factor
from src.models.passwords import Password
from src.models.token import Token
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.schemas.passwords import ResetPasswordSchema
from src.utils.auth import authenticate_user, create_access_token, generate_confirmation_code, generate_2F_code, \
    send_2F_code, verify_2F_code, get_current_active_user
from src.utils.passwords import generate_password
from src.config.database import get_db
import re
from passlib.context import CryptContext
from src.models.users import User
from src.schemas.users import UserCreate
from src.utils.tokens import create_reset_token, verify_reset_token, send_reset_email
from src.utils.users import send_email_confirmation, get_user_by_email, update_user_password

auth_router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@auth_router.post('/token', response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=1440)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password too short, min 8 chars.")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")

@auth_router.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    exist_user = db.query(User).filter(User.email == user_data.email).first()
    if exist_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # password = generate_password(length=12)

    confirmation_code = generate_confirmation_code()

    hashed_password = hash_password(user_data.password)

    user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        email_confirmation_code=confirmation_code,
        email_confirmation_sent_at=datetime.utcnow()
    )

    db.add(user)
    db.commit()

    send_email_confirmation(user_data.email, confirmation_code)

    return {"message": "The confirmation code sent to your email. Please check your email for the confirmation code"}


@auth_router.get("/generate-password")
def generate_new_password():
    return {"password": generate_password()}

@auth_router.post("/verify-email")
def verify_email(
        email: str,
        confirmation_code: str,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email_confirmation_code != confirmation_code:
        raise HTTPException(status_code=400, detail="Invalid confirmation code")

    if user.email_confirmation_sent_at + timedelta(minutes=10) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Confirmation code expired")

    user.is_email_confirmed = True
    db.commit()

    return {"message": "Email successfully confirmed"}

@auth_router.post("/auth/forgot-password")
def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_reset_token(user.email)
    send_reset_email(user.email, token)
    return {"message": "Reset link sent"}


@auth_router.post("/auth/reset-password")
def reset_password(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    email = verify_reset_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_user_password(db, user, data.new_password)
    return {"message": "Password successfully reset"}

@auth_router.post("/auth/send-2F/")
def send_2F(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    code = generate_2F_code()

    send_2F_code(user.email, code)

    auth_2f = db.query(Auth_2Factor).filter_by(user_id=user.id).first()
    if auth_2f:
        auth_2f.confirmation_2F_code = code
        auth_2f.expired_at = datetime.utcnow() + timedelta(minutes=5)
    else:
        auth_2f = Auth_2Factor(
            user_id=user.id,
            confirmation_2F_code=code,
            expired_at=datetime.utcnow() + timedelta(minutes=5)
        )
        db.add(auth_2f)

    db.commit()

    return {"message": "2FA code sent to email"}
@auth_router.post("/auth/verify-2F/")
# def verify_2F(
#     email: str = Query(..., description="User email"),
#     code: str = Query(..., description="2FA code sent to email"),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(User).filter(User.email == email).first()
#     if not user or not user.auth_2f:
#         raise HTTPException(status_code=404, detail="User or 2FA entry not found")
#
#     if user.auth_2f.confirmation_2F_code != code:
#         raise HTTPException(status_code=401, detail="Invalid 2FA code")
#
#     if datetime.utcnow() > user.auth_2f.expired_at:
#         raise HTTPException(status_code=401, detail="2FA code expired")
#
#     db.query(Password).filter(Password.user_id == user.id).update({Password.is_logged: 1})
#     db.commit()
#
#     return {"message": "2FA verification successful, access granted"}

def verify_2F(email: str, code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.auth_2f:
        raise HTTPException(status_code=404, detail="User or 2FA not found")

    if str(user.auth_2f.confirmation_2F_code) != str(code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")

    if datetime.utcnow() > user.auth_2f.expired_at:
        raise HTTPException(status_code=401, detail="2FA code expired")

    db.query(Password).filter(Password.user_id == user.id).update({Password.is_logged: 1})
    db.commit()

    return {"message": "2FA verification successful and access granted"}