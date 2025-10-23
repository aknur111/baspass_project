from jose import jwt, JWTError
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

SECRET_KEY = os.getenv("SECRET_KEY", "vjxc wchz zgmd pwrs")
ALGORITHM = "HS256"
RESET_LINK_BASE_URL = "http://localhost:8000/auth/reset-password?token="

def create_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def send_reset_email(user_email: str, token: str):
    from_email = "aknur11072005@gmail.com"
    from_password = "vjxc wchz zgmd pwrs"
    to_email = user_email

    reset_link = f"{RESET_LINK_BASE_URL}{token}"

    subject = "Password Reset Request"
    body = f"""
    Hello,

    You requested to reset your password. Click the link below to proceed:
    {reset_link}
    

    If you didn't request this, please ignore this email.

    This link will expire in 1 hour.
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"Reset email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def verify_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None



#
# def send_email_confirmation(user_email, confirmation_code):
#     from_email = "aknur11072005@gmail.com"
#     password = "chfd xlzs zolu jjuf"
#     to_email = user_email
#
#     subject = "Please confirm your email address"
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
#         print(f"Confirmation email sent to {to_email}")
#     except Exception as e:
#         print(f"Failed to send email: {e}")
#
