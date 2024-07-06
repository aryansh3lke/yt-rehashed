from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from itertools import islice
from openai import OpenAI, OpenAIError
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from re import search
import shutil
import tiktoken
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_comment_downloader import *

app = Flask(__name__)
CORS(app)

load_dotenv()
client = OpenAI()
downloader = YoutubeCommentDownloader()

CHATGPT_TOKEN_LIMIT = 16385
CHATGPT_SUMMARIZATION_PROMPT = "Please provide two summaries in the following format:\n\n---\n\nSummary of the YouTube video transcript (200 to 250 words):\n'transcript'\n\n---\n\nSummary of the YouTube video comments (200 to 250 words):\n'comments'\n\n---"

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

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

def get_comments(video_url, comment_count=100):
    popular_comments = downloader.get_comments_from_url(video_url, sort_by=SORT_BY_POPULAR)
    comments, comments_str = [], ""
    for index, comment in enumerate(islice(popular_comments, comment_count)):
        comments.append(comment)
        comments_str += str(index + 1) + ") " + comment['text'] + "\n"
    
    return (comments, comments_str.strip())

def get_token_count(transcript, comments, encoding_name):
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(transcript + comments + CHATGPT_SUMMARIZATION_PROMPT))
    return num_tokens

def summarize_video(transcript, comments):
    try:
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a summarizing assistant for YouTube videos that restates the main points of the video and summarizes viewer comments."},
            {"role": "user", "content": f"Please provide two summaries in the following format:\n\n---\n\nSummary of the YouTube video transcript (300 to 400 words):\n{transcript}\n\n---\n\nSummary of the YouTube video comments (300 to 400 words):\n{comments}\n\n---"}
        ],
        max_tokens=750,
        temperature=0.7
    )
        return completion.choices[0].message.content
    except OpenAIError as e:
        print(f"An OpenAI API error occurred: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def parse_summaries(video_summaries):
    _, _, video_summaries = video_summaries.partition(':')
    transcript_summary, _, comment_summary = video_summaries.partition(':')
    transcript_summary, _, _ = transcript_summary.partition('Summary of the YouTube video comments')
    return (transcript_summary.strip(), comment_summary.strip())

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
        return jsonify({'message': 'YouTube video does not exist or is missing a transcript!'}), 400
    
    transcript = ' '.join([caption['text'] for caption in captions])

    comments, comments_str = get_comments(video_url)
    
    if get_token_count(transcript, comments_str, "gpt-3.5-turbo") < CHATGPT_TOKEN_LIMIT:
        video_summaries = summarize_video(transcript, comments_str)
        if video_summaries is None:
            return jsonify({'message': 'The summarizer is currently down!'}), 500
        else:
            transcript_summary, comment_summary = parse_summaries(video_summaries)
            video_title = YouTube(video_url).title
            
            return jsonify({'video_id': video_id,
                            'video_title': video_title,
                            'comments': comments,
                            'transcript_summary': transcript_summary, 
                            'comment_summary': comment_summary}), 200
    else:
        return jsonify({'message': 'This video is too long to summarize!'}), 400

@app.route('/api/download-video', methods=['POST'])
def download_video():
    video_id = request.json.get('videoId')
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    download_type = "video"
    
    try:
        yt = YouTube(video_url)
        print(f'Downloading video: {video_url}')
        stream = yt.streams.filter(file_extension="mp4", type=download_type).first()
        if stream:
            download_file_path = stream.download(output_path=DOWNLOAD_FOLDER)
            video_title = yt.title
            
            response = make_response(send_file(
                download_file_path,
                as_attachment=True,
                mimetype='video/mp4'
            ))
            shutil.rmtree("downloads")
            return response, 200
        else:
           return jsonify({'message': 'No streams available to download video!'}), 500
    except VideoUnavailable:
        return jsonify({'message': f'Video {video_url} is unavailable.'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)