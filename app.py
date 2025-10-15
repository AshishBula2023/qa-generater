from flask import Flask, request, jsonify
import youtube_dl
from pydub import AudioSegment
import speech_recognition as sr
import os

app = Flask(__name__)

def extract_audio(video_url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return 'video.mp3'

def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError:
            return "API unavailable."

@app.route('/extract_text', methods=['POST'])
def extract_text():
    data = request.get_json()
    url = data.get('url', '')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # ऑडियो एक्सट्रैक्ट
    audio_file = extract_audio(url)
    text = speech_to_text(audio_file)

    # फाइल हटाएं
    if os.path.exists(audio_file):
        os.remove(audio_file)

    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
