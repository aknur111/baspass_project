from fastapi import APIRouter, Query
from src.utils.image_generation import generate_image_from_text

router = APIRouter(prefix="/image", tags=["Image"])

@router.get("/generate/")
@router.get("/generate/")
def generate_image(prompt: str):
    image_url = generate_image_from_text(prompt)
    return {"image_url": image_url}