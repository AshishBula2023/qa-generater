from flask import Flask, request, jsonify
import youtube_dl
from pydub import AudioSegment
import speech_recognition as sr
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_audio(video_url):
    video_id = video_url.split("v=")[1].split("&")[0][:10]  # यूनिक ID
    ydl_opts = {
        'outtmpl': f'video_{video_id}.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return f'video_{video_id}.mp3'

def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source, duration=10)  # 10 सेकंड लिमिट
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

    logger.debug(f"Processing URL: {url}")
    try:
        audio_file = extract_audio(url)
        logger.debug(f"Audio file extracted: {audio_file}")
        text = speech_to_text(audio_file)
        logger.debug(f"Text extracted: {text}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    if os.path.exists(audio_file):
        os.remove(audio_file)
    return jsonify({'text': text})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
