
from pydantic import BaseModel, HttpUrl, constr
from typing import Optional


class PasswordCreate(BaseModel):
    login: str
    password: str
    site_name: str
    description: Optional[str] = None
    url: Optional[HttpUrl] = None


class PasswordOut(BaseModel):
    id: int
    login: str
    site_name: str
    description: Optional[str] = None
    url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class PasswordUpdateLogPass(BaseModel):
    login: Optional[str] = None
    password: Optional[str] = None
    site_name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[HttpUrl] = None

class PasswordOutForSearch(BaseModel):
    id: int
    login: str
    password: str
    site_name: str
    description: Optional[str] = None
    url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class PasswordPatch(BaseModel):
    id: int
    login: str
    password: str

    class Config:
        from_attributes = True



class ResetPasswordSchema(BaseModel):
    token: str
    new_password: constr(min_length=8)
