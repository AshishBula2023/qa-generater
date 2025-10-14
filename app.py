# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

class VideoURL(BaseModel):
    url: str

app = FastAPI()

def extract_video_id(url: str):
    import re
    patterns = [
        r"youtu\.be\/([^\?\&]+)",
        r"youtube\.com\/watch\?v=([^\?\&]+)",
        r"youtube\.com\/embed\/([^\?\&]+)",
        r"youtube\.com\/shorts\/([^\?\&]+)"
    ]
    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)
    return None

@app.post("/transcript")
def get_transcript(video: VideoURL):
    video_id = extract_video_id(video.url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t['text'] for t in transcript_list])
        return {"transcript": transcript_text}
    except TranscriptsDisabled:
        return {"error": "Transcript not available"}
    except Exception as e:
        return {"error": str(e)}
