from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.models.passwords import Password
from src.schemas.passwords import PasswordCreate

import string
import secrets

def create_password(db: Session, password_data: PasswordCreate, user_id: int):
    save_password = password_data.password
    db_password = Password(
        user_id=user_id,
        login=password_data.login,
        password=save_password,
        site_name = password_data.site_name,
        description=password_data.description,
        url=str(password_data.url)
    )
    db.add(db_password)
    db.commit()
    db.refresh(db_password)
    return db_password

def get_passwords_by_user(db: Session, user_id: int):
    return db.query(Password).filter(Password.user_id == user_id).all()

def get_password_by_id(db: Session, password_id: int, user_id: int):
    return db.query(Password).filter(
        Password.id == password_id,
        Password.user_id == user_id
    ).first()

def delete_password(db: Session, password_id: int, user_id: int):
    db_password = get_password_by_id(db, password_id, user_id)
    if db_password:
        db.delete(db_password)
        db.commit()
    return db_password

def update_password(db: Session, password_id: int, user_id: int, password_data: PasswordCreate):
    db_password = get_password_by_id(db, password_id, user_id)
    if db_password:
        db_password.login = password_data.login
        db_password.password = password_data.password
        db_password.description = password_data.description
        db_password.url = str(password_data.url)
        db.commit()
        db.refresh(db_password)
    return db_password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encrypt_password(password: str) -> str:
    return pwd_context.hash(password)

def create_new_password(db: Session, password: PasswordCreate, user_id: int):
    return create_password(db=db, password=password, user_id=user_id)

def get_user_passwords(db: Session, user_id: int):
    return get_passwords_by_user(db=db, user_id=user_id)


def generate_password(length=15, use_symbols=True, use_numbers=True, use_uppercase=True, use_lowercase=True):
    characters = ""

    if use_uppercase:
        characters += string.ascii_uppercase
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation

    password = ''.join(secrets.choice(characters) for i in range(length))
    return password
#
# def generate_password(lenght):
#     characters = string.ascii_letters + string.digits + string.punctuation
#     password = ''.join(random.choice(characters) for i in range(lenght))
#     return password
#
# password_lengh = 15
# new_password = generate_password(password_lengh)
#
# print(f"Generated Password: {new_password}")