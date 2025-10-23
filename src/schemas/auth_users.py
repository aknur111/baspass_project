from typing import List
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str



# class EmailModel(BaseModel):
#     addresses : List[str]
#
# class PasswordResetRequestModel(BaseModel):
#     email: str
# class PasswordResetConfirmModel(BaseModel):
#     new_password: str
#     confirm_new_password: str

