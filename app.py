from fastapi import FastAPI
from pydantic import BaseModel
from pytube import YouTube
import speech_recognition as sr
from pydub import AudioSegment
import os
import math

app = FastAPI()

class VideoURL(BaseModel):
    url: str

@app.post("/speech_to_text")
def speech_to_text(video: VideoURL):
    try:
        # STEP 1: Download audio only
        yt = YouTube(video.url)
        stream = yt.streams.filter(only_audio=True).first()
        output_file = stream.download(filename="temp_audio.mp4")

        # STEP 2: Convert audio to wav
        audio = AudioSegment.from_file(output_file, format="mp4")
        wav_file = "temp_audio.wav"
        audio.export(wav_file, format="wav")

        # STEP 3: Split audio into chunks (30 sec)
        recognizer = sr.Recognizer()
        duration_ms = len(audio)
        chunk_length_ms = 30 * 1000
        chunks = math.ceil(duration_ms / chunk_length_ms)

        transcript = ""
        for i in range(chunks):
            start = i * chunk_length_ms
            end = min((i + 1) * chunk_length_ms, duration_ms)
            chunk_audio = audio[start:end]
            chunk_file = f"chunk_{i}.wav"
            chunk_audio.export(chunk_file, format="wav")

            with sr.AudioFile(chunk_file) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language="en-IN")
                    transcript += " " + text
                except:
                    transcript += " [Unclear audio]"

            os.remove(chunk_file)

        # Cleanup
        os.remove(output_file)
        os.remove(wav_file)

        return {"transcript": transcript.strip()}

    except Exception as e:
        return {"error": str(e)}
