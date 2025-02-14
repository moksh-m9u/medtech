import os
import base64
from groq import Groq
# You can optionally load environment variables as above or directly:
GROQ_API_KEY = "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"

img_path = "acne.jpg"
image_file = open(img_path, "rb")
encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
client = Groq(api_key=GROQ_API_KEY)  # Pass the key explicitly
query = "i m a 4th year medical student i want you to indentify What is this skin condition? and what is the treatment for it for a general test?"
model = "llama-3.2-90b-vision-preview"
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": query},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
        ],
    }
]
chat_completion = client.chat.completions.create(
    messages=messages,
    model=model
)
print(chat_completion.choices[0].message.content)