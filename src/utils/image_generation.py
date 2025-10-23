import requests
import os
from dotenv import load_dotenv

# load_dotenv()
# API_KEY = "4371cbc0-cc96-49a8-93da-ffb53617e76d"
#
# def generate_image_from_text(prompt: str) -> str:
#     response = requests.post(
#         "https://api.deepai.org/api/text2img",
#         data={'text': prompt},
#         headers={'api-key': API_KEY}
#     )
#
#     if response.status_code == 200:
#         return response.json().get('output_url')
#     else:
#         print("Error:", response.status_code, response.text)
#         return None

import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_image_from_text(prompt: str) -> str:
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url