
from bcrypt import hashpw, gensalt, checkpw

import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated

from jwt.exceptions import InvalidTokenError
from src.models.token import TokenData
from src.config.config_loader import settings
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
import jwt
from src.config.database import get_db
from src.models.users import User
from src.utils.users import get_user_by_email, get_user_by_username
from src.models.failed_login import FailedLogin
from datetime import datetime, timedelta

def get_password_hash(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False



SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
def authenticate_user(username: str, password: str, db: Session):
    user = get_user_by_email(db, username)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password. Try again")

    failed = db.query(FailedLogin).filter(FailedLogin.user_id == user.id).first()

    now_utc = datetime.now(timezone.utc)

    if failed and failed.blocked_until and failed.blocked_until > now_utc:
        raise HTTPException(
            status_code=403,
            detail="This account blocked. Please try again after 10 minutes."
        )

    password_ok = verify_password(password, user.password)

    if not password_ok:
        if not failed:
            failed = FailedLogin(
                user_id=user.id,
                attempts=1,
                last_attempt=now_utc
            )
            db.add(failed)
        else:
            failed.attempts += 1
            failed.last_attempt = now_utc
            if failed.attempts >= 5:
                failed.blocked_until = now_utc + timedelta(minutes=10)
        db.commit()
        raise HTTPException(status_code=401, detail="Incorrect email or password. Try again")

    if failed:
        db.delete(failed)
        db.commit()

    return user
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db:Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user



def generate_confirmation_code():
    return str(random.randint(100000, 999999))


def send_email_confirmation(user_email, confirmation_code):
    from_email = "aknur11072005@gmail.com"
    password = "uyqx dncr tvlk bguf"
    to_email = user_email

    subject = "Please confirm your email address"
    body = f"Your confirmation code is {confirmation_code}"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"Confirmation email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def generate_2F_code():
    return str(random.randint(100000, 999999))

def send_2F_code(user_email: str, code: str):
    subject = "Your 2FA Code"
    body = f"Your 2FA code is: {code}"

    send_2F_email_confirmation(to_email=user_email, subject=subject, body=body)


# def send_2F_email_confirmation(user_email, confirmation_code):
#     from_email = "aknur11072005@gmail.com"
#     password = "chfd xlzs zolu jjuf"
#     to_email = user_email
#
#     subject = "2F authentication"
#     body = f"Your confirmation code is {confirmation_code}"
#
#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))
#
#     try:
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(from_email, password)
#             server.sendmail(from_email, to_email, msg.as_string())
#         print(f"2F Confirmation email sent to {to_email}")
#     except Exception as e:
#         print(f"Failed to send email: {e}")

def send_2F_email_confirmation(to_email: str, subject: str, body: str):
    from_email = "aknur11072005@gmail.com"
    password = "uyqx dncr tvlk bguf "

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"2F Confirmation email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def verify_2F_code(user, code: str) -> bool:
    if user.auth_2F.confirmation_2F_code == code and datetime.utcnow() < user.auth_2F.expired_at:
        return True
    return False
