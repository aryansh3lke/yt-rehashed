from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from re import search
import tiktoken

app = Flask(__name__)
CORS(app)

load_dotenv()
client = OpenAI()

TOKENS_PER_MINUTE_LIMIT = 60000

def extract_video_id(url):
    regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/\n\s]+/\S*/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = search(regex, url)
    return match.group(1) if match else None

def fetch_captions(video_id):
    try:
        captions = YouTubeTranscriptApi.get_transcript(video_id)
    except:
        return None
    return captions

def get_token_count(transcript, encoding_name):
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(transcript))
    return num_tokens

def summarize_transcript(transcript):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a summarizing assistant for Youtube videos that restates the main points."},
            {"role": "user", "content": f"Summarize the following YouTube transcript in 200 to 250 words: {transcript}"}
        ],
        max_tokens=350,
        temperature=0.7
    )

    return completion.choices[0].message.content

@app.route('/')
def hello():
    return "Welcome to the Youtube Rehashed Flask backend!"

@app.route('/api/get-summary', methods=['POST'])
def get_summary():
    video_url = request.json.get('videoUrl')

    video_id = extract_video_id(video_url)
    if video_id is None:
        return jsonify({'message': 'Please enter a valid YouTube URL!'}), 400

    captions = fetch_captions(video_id)
    if captions is None:
        return jsonify({'message': 'YouTube video does not exist!'}), 400
    
    transcript = ' '.join([caption['text'] for caption in captions])
    
    if get_token_count(transcript, "gpt-3.5-turbo") < TOKENS_PER_MINUTE_LIMIT:
        summary = summarize_transcript(transcript)
        if not summary:
            return jsonify({'message': 'Failed to summarize video!'}), 500
        else:
            return jsonify({'summary': summary, "video_id": video_id}), 200
    else:
        return jsonify({'message': 'This video is too long to summarize!'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)