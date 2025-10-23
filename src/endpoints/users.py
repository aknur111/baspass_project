from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from starlette import status

from src.endpoints.auth import validate_password
from src.schemas.auth_users import UserRegister
from src.utils.auth import get_current_active_user
from src.utils.auth import get_password_hash, verify_password
from src.config.database import get_db
from src.models.users import User
from src.schemas.users import UserSchema, UserCreate, UserUpdate, UserPasswordChange
from src.utils.users import get_users, create_user, get_user, delete_user



user_router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@user_router.get('/', response_model=list[UserSchema])
def user_list(db: Session = Depends(get_db)):
    db_users = get_users(db)

    return db_users


@user_router.get('/me', response_model=UserSchema)
def user_list(current_user: User = Depends(get_current_active_user)):
    return current_user



@user_router.get('/{user_id}', response_model=UserSchema)
def user_detail(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@user_router.delete('/{user_id}')
def user_delete(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    delete_user(db, db_user.id)
    return {"message": "User deleted"}


@user_router.post("/", response_model=UserSchema)
def user_post(user: UserCreate, db:Session = Depends(get_db)):
    return create_user(db, user)

@user_router.post("/register", status_code=201)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    validate_password(user_data.password)
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"User {new_user.username} successfully registered"}


# @user_router.patch("/{user_id}", status_code=201)
# def partial_update_user(
#     user_id: int,
#     user_update: UserUpdate,
#     db: Session = Depends(get_db)
# ):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     if user_update.username is not None:
#         user.username = user_update.username
#     if user_update.email is not None:
#         user.email = user_update.email
#     if user_update.password is not None:
#         user.password = get_password_hash(user_update.password)
#
#     db.commit()
#     db.refresh(user)
#     return {"message": "User updated successfully"}


@user_router.patch("/me", status_code=200)
def partial_update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username:
        user.username = user_update.username
    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(user)

    return {"message": "Your profile was successfully updated"}

@user_router.patch("/me/password")
def change_my_password(
    password_data: UserPasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not verify_password(password_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user.password = get_password_hash(password_data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}

