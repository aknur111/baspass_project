from dotenv import load_dotenv
from fastapi import FastAPI
from src.endpoints.auth import auth_router
from src.endpoints.users import user_router
from src.endpoints.passwords import router as password_router
from src.endpoints.image import router as image_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(password_router)
app.include_router(image_router)
load_dotenv()