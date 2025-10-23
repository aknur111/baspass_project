from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.endpoints.auth import hash_password
from src.models.auth_2F import Auth_2Factor
from src.models.passwords import Password
from src.schemas.auth_users import UserCreate
from src.schemas.passwords import PasswordCreate, PasswordOut, PasswordUpdateLogPass, PasswordOutForSearch, \
    PasswordPatch
from src.utils.passwords import (
    create_password,
    get_passwords_by_user,
    get_password_by_id,
    delete_password,
    update_password, generate_password
)
from src.utils.auth import get_current_active_user, generate_2F_code, send_email_confirmation, get_current_user
from src.config.database import get_db
from src.models.users import User
from fastapi import Query


router = APIRouter(
    prefix="/passwords",
    tags=["Passwords"]
)

@router.post("/", response_model=PasswordOut)
def add_password(
    password_data: PasswordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not password_data.site_name:
        raise HTTPException(status_code=400, detail="site_name is required")

    return create_password(db, password_data, current_user.id)


@router.get("/", response_model=list[PasswordOut])
# def list_passwords(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_active_user)
# ):
#     return get_passwords_by_user(db, current_user.id)
def list_passwords(
    code: int = Query(..., description="2FA code from email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    auth = db.query(Auth_2Factor).filter(Auth_2Factor.user_id == current_user.id).first()

    if not auth or auth.confirmation_2F_code != code or auth.expired_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired 2FA code")

    passwords = db.query(Password).filter(Password.user_id == current_user.id).all()
    return passwords

@router.delete("/{password_id}", response_model=PasswordOut)
def delete_password_route(
    password_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_password = delete_password(db, password_id, current_user.id)
    if not db_password:
        raise HTTPException(status_code=404, detail="Password not found")
    return db_password

@router.put("/{password_id}", response_model=PasswordOut)
def update_password_route(
    password_id: int,
    password_data: PasswordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    updated = update_password(db, password_id, current_user.id, password_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Password not found")
    return updated

@router.patch("/me/{password_id}", response_model=PasswordPatch)
def partial_update_password(
    password_id: int,
    password_update: PasswordUpdateLogPass,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    password_entry = db.query(Password).filter(
        Password.id == password_id,
        Password.user_id == current_user.id
    ).first()

    if not password_entry:
        raise HTTPException(status_code=404, detail="Password entry not found")

    if password_update.login is not None:
        password_entry.login = password_update.login
    if password_update.password is not None:
        password_entry.password = password_update.password
    if password_update.url is not None:
        password_entry.url = password_update.url
    if password_update.description is not None:
        password_entry.description = password_update.description

    db.commit()
    db.refresh(password_entry)
    return password_entry

@router.get("/search/", response_model=list[PasswordOutForSearch])
# def search_passwords_by_site(
#     site_name: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_active_user)
# ):
#     site_name = site_name.strip()
#
#     results = db.query(Password).filter(
#         Password.user_id == current_user.id,
#         Password.site_name.ilike(f"%{site_name}%")
#     ).all()
#
#     return results

def search_passwords_by_site(
    site_name: str,
    code: int = Query(..., description="2FA code from email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    auth_2f = db.query(Auth_2Factor).filter_by(user_id=current_user.id).first()
    if not auth_2f or auth_2f.confirmation_2F_code != code:
        raise HTTPException(status_code=401, detail="Invalid or missing 2FA code")

    site_name = site_name.strip()
    results = db.query(Password).filter(
        Password.user_id == current_user.id,
        Password.site_name.ilike(f"%{site_name}%")
    ).all()

    return results
