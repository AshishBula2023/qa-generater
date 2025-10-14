# 🎙 YouTube Speech-to-Text API

FastAPI-based API that:
- Accepts YouTube video URL (POST /speech_to_text)
- Downloads only audio
- Converts to WAV
- Generates transcript using Google Speech Recognition

## 🚀 How to run locally
```bash
pip install -r requirements.txt
uvicorn app:app --reload
