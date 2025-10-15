from fastapi import FastAPI, HTTPException
from pytube import YouTube
import whisper
import os

app = FastAPI()

# Tiny model for low memory usage
model = whisper.load_model("tiny")

@app.get("/transcript")
def generate_transcript(video_url: str):
    try:
        # Download audio only
        yt = YouTube(video_url)
        stream = yt.streams.filter(only_audio=True).first()
        if not stream:
            raise HTTPException(status_code=400, detail="No audio stream found")
        
        output_file = stream.download(filename="temp_audio.mp4")

        # Transcribe audio using Tiny model
        result = model.transcribe(output_file)
        transcript_text = result["text"]

        # Remove temp file
        os.remove(output_file)

        return {
            "video_title": yt.title,
            "transcript": transcript_text
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
