from fastapi import FastAPI, HTTPException
from pytube import YouTube
import whisper
import os

app = FastAPI()

# Load lightweight model for low memory usage
model = whisper.load_model("tiny")  # tiny, base, small, medium, large

@app.get("/transcript")
def generate_transcript(video_url: str):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(only_audio=True).first()
        output_file = stream.download(filename="temp.mp4")

        # Transcribe using Whisper (low memory mode)
        result = model.transcribe(output_file, fp16=False)
        text = result["text"]

        os.remove(output_file)
        return {"video_title": yt.title, "transcript": text}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
