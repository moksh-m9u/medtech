#line 10 and 31 me groq ki api key daalni hai
import base64
from groq import Groq
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
 
def analyze_image_with_query(query, model, encoded_image):
#GROQ API KEY IDHR DAAL DO
    client = Groq(api_key="GROK API KEY HERE")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
            ]
        }
    ]
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model
    )
    return chat_completion.choices[0].message.content

def generate_doctor_response_text(query, model):
    """
    Generate a doctor response using Groq in a text-only mode.
    """
#GROQ KI API KEY IDHR DAAL DENA MANUALLY
    client = Groq(api_key="api key groq wali")
    messages = [
        {"role": "user", "content": [{"type": "text", "text": query}]}
    ]
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model
    )
    return chat_completion.choices[0].message.content