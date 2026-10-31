from groq import Groq
import base64, os, json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def image_to_base64(image_path):
    """Reads an image from file path and converts it to Base64."""
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    return image_bytes

def analyze_image(image_path):
    image_bytes = image_to_base64(image_path)
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    print('sent')
    messages = [{
        "role": "user",
        "content" : [
            {
                "type" : "text","text":"is this a teeth image ? Respond with a JSON object containing a 'is_teeth' boolean field"
            },
            {
                "type":"image_url","image_url" : {"url":f"data:image/jpeg;base64,{base64_image}"}
            }
        ]
    }]

    response = client.chat.completions.create(
        model = "meta-llama/llama-4-maverick-17b-128e-instruct",
        messages = messages,
        response_format={"type":"json_object"},
        temperature=0,
        max_tokens=50
    )

    return  json.loads(response.choices[0].message.content)
