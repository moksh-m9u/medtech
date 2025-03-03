import logging
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
from io import BytesIO
import os
from groq import Groq

ffmpeg_path = which("ffmpeg")
if ffmpeg_path is None:
    logging.warning("ffmpeg not found! Please install it and add it to PATH.")
else:
    AudioSegment.converter = ffmpeg_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def record_audio(filename="patient_voice_test.mp3", timeout=20, phrase_time_limit=None, duration=None):
    """
    Record audio from the microphone and save it as an MP3 file.
    Returns the saved file path.
    """
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2.0
    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")
            if duration:
                audio_data = recognizer.record(source, duration=duration)
            else:
                audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            file_path = os.path.join(os.getcwd(), filename)
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            logging.info(f"Audio saved to {file_path}")
            return file_path
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

def transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY):
    """
    Transcribe the audio file using Groq's STT model.
    Returns the transcribed text or an error message.
    """
    try:
        client = Groq(api_key=GROQ_API_KEY)
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
        return transcription.text
    except Exception as e:
        return f"Error during transcription: {e}"
