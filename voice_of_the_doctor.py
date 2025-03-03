import time
from gtts import gTTS
import elevenlabs
from elevenlabs.client import ElevenLabs
import pygame


def gtts_tts_and_play(input_text, output_filepath="gtts_output.mp3"):
    tts = gTTS(text=input_text, lang="en", slow=False)
    tts.save(output_filepath)
    pygame.mixer.init()
    pygame.mixer.music.load(output_filepath)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()
    return output_filepath

def text_to_speech_with_elevenlabs(input_text, output_filepath="elevenlabs_output.mp3"):
    ELEVENLABS_API_KEY = "idhr apni eleven labs ki api key dalni hai"
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.generate(
        text=input_text,
        voice="Aria",
        output_format="mp3_22050_32",
        model="eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)
    pygame.mixer.init()
    pygame.mixer.music.load(output_filepath)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()
    return output_filepath
