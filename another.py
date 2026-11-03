import base64
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def is_groq_configured() -> bool:
    """Return True only when the Groq API key is present."""
    return bool(os.getenv("GROQ_API_KEY"))


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")
    return Groq(api_key=api_key)


def image_to_base64(image_path):
    """Reads an image from file path and converts it to Base64."""
    image_path = Path(image_path)
    with image_path.open("rb") as image_file:
        return image_file.read()


def analyze_image(image_path):
    """Validate whether an uploaded image looks like a teeth/oral image."""
    if not is_groq_configured():
        raise RuntimeError("GROQ_API_KEY is not configured.")

    image_bytes = image_to_base64(image_path)
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Is this a teeth image? Respond with a JSON object containing "
                        "an 'is_teeth' boolean field."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ]

    response = _get_client().chat.completions.create(
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=50,
    )

    payload = response.choices[0].message.content
    if not payload:
        return {"is_teeth": False}

    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        return {"is_teeth": False}
    return parsed
