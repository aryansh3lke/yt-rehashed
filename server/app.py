import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from itertools import islice
from openai import OpenAI, OpenAIError
from os import getenv
from pytubefix import YouTube
from pytubefix.exceptions import VideoUnavailable, RegexMatchError
from re import search
import requests
from requests.exceptions import HTTPError
import tiktoken
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR

app = Flask(__name__)
CORS(app)

load_dotenv()
client = OpenAI()
downloader = YoutubeCommentDownloader()

# Configure S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id = getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = getenv('AWS_SECRET_ACCESS_KEY'),
    region_name = getenv('AWS_S3_REGION')
)
bucket_name = getenv('AWS_S3_BUCKET_NAME')

# ChatGPT-3.5-turbo Model
CHATGPT_TOKEN_LIMIT = 16385
RESPONSE_TOKEN_LIMIT = 500
REQUEST_TOKEN_LIMIT = CHATGPT_TOKEN_LIMIT - RESPONSE_TOKEN_LIMIT
CHATGPT_SYSTEM_ROLE = """
    You are a summarizing assistant for YouTube videos that restates the main 
    points of the video and summarizes viewer comments.
"""

def extract_video_id(url):
    """
    Extract the YouTube video ID from a given URL.

    This function uses a regular expression to parse the YouTube video ID from a variety of YouTube URL formats. 
    It can handle URLs from the main YouTube site and the shortened youtu.be format.

    Args:
        url (str): The URL of the YouTube video.

    Returns:
        str: The extracted video ID if found, otherwise None.

    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=abc123XYZ")
        'abc123XYZ'
        >>> extract_video_id("https://youtu.be/abc123XYZ")
        'abc123XYZ'
        >>> extract_video_id("https://www.youtube.com/v/abc123XYZ?version=3&autohide=1")
        'abc123XYZ'
        >>> extract_video_id("invalid_url")
        None
    """
    
    regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/\n\s]+/\S*/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = search(regex, url)
    return match.group(1) if match else None

def fetch_captions(video_id):
    """
    Fetch captions for a given YouTube video ID.

    This function uses the YouTubeTranscriptApi to retrieve the captions (subtitles) for a specified YouTube video.
    If the captions cannot be retrieved, it returns None.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        list: A list of caption dictionaries if captions are found.
        None: If an error occurs or captions are not available.

    Examples:
        >>> fetch_captions("abc123XYZ")
        [{'start': 0.0, 'duration': 4.0, 'text': 'Hello world'}, ...]
        >>> fetch_captions("invalid_id")
        None
    """

    try:
        captions = YouTubeTranscriptApi.get_transcript(video_id)
    except:
        return None
    
    return captions

def get_comments(video_url, comment_count=100):
    """
    Fetch and format popular comments from a given YouTube video URL.

    This function retrieves a specified number of popular comments from a YouTube video and formats them
    into a list and a concatenated string.

    Args:
        video_url (str): The URL of the YouTube video.
        comment_count (int, optional): The number of comments to retrieve. Defaults to 100.

    Returns:
        tuple:
            - list: A list of comment dictionaries if comments are found.
            - str: A string containing the formatted comments.
            - (None, None): If an error occurs or comments are not available.

    Examples:
        >>> get_comments("https://www.youtube.com/watch?v=abc123XYZ")
        ([{'text': 'Great video!'}, ...], '1) Great video!\n2) Very informative!\n...')
        >>> get_comments("invalid_url")
        (None, None)
    """

    try:
        popular_comments = downloader.get_comments_from_url(video_url, sort_by=SORT_BY_POPULAR)
        comments, comments_str = [], ""
        for index, comment in enumerate(islice(popular_comments, comment_count)):
            comments.append(comment)
            comments_str += str(index + 1) + ") " + comment['text'] + "\n"
        
        return comments, comments_str.strip()
    except:
        return None, None

def get_token_count(prompt, encoding_name):
    """
    Count the number of tokens in a given prompt using a specified encoding.

    This function encodes a prompt using a specified encoding and returns the number of tokens.

    Args:
        prompt (str): The input text to encode.
        encoding_name (str): The name of the encoding to use.

    Returns:
        int: The number of tokens in the encoded prompt.

    Examples:
        >>> get_token_count("Hello, how are you?", "gpt-3.5-turbo")
        5
    """

    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(prompt))
    return num_tokens

def ask_chatgpt(prompt, system_role):
    """
    Send a prompt to ChatGPT and retrieve the response.

    This function sends a prompt to the OpenAI ChatGPT model with a specified system role and returns the response.

    Args:
        prompt (str): The user's input prompt.
        system_role (str): The role of the system for context setting in the conversation.

    Returns:
        tuple:
            - str: The response from ChatGPT if successful.
            - str: None if successful, or an error message if an error occurs.

    Examples:
        >>> ask_chatgpt("Tell me a joke.", "You are a friendly assistant.")
        ('Why don't scientists trust atoms? Because they make up everything!', None)
        >>> ask_chatgpt("invalid_prompt", "Invalid role")
        (None, 'OpenAIError: Invalid request')
    """

    try:
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        max_tokens=RESPONSE_TOKEN_LIMIT,
        temperature=0.7
    )
        return completion.choices[0].message.content, None
    except OpenAIError as e:
        return None, f"OpenAIError: {str(e)}"
    except Exception as e:
        return None, {str(e)}

@app.route('/')
def hello():
    return "You have reached the Youtube Rehashed Flask backend server!"

@app.route('/api/get-summaries', methods=['GET'])
def get_summaries():
    """
    Return video details, comments, and summaries for given YouTube video.

    HTTP Method: GET

    Request Parameters:
        video_url (str): The URL of the YT video to generate summaries for. (required)

    Responses:
        200: Video ID, video title, comments, and summaries for the given video.
        400: Missing parameters, invalid video URL or ID, or video is too long.
        500: An error occurred when fetching the comments or prompting ChatGPT.
    
    Example:
        GET /api/get-summaries?video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """

    # Save parameters from request
    video_url = request.args.get('video_url')

    # Check for missing parameters
    if not video_url:
        return jsonify({'error': 'Video URL is missing!'}), 400
    
    # Extract video ID from video URL
    video_id = extract_video_id(video_url)
    if video_id is None:
        return jsonify({'error': 'Please enter a valid YouTube URL!'}), 400

    # Fetch captions with the YouTube Transcript API
    captions = fetch_captions(video_id)
    if captions is None:
        return jsonify({'error': 'YouTube video does not exist or is missing a transcript!'}), 400
    
    # Create transcript by merging captions
    transcript = ' '.join([caption['text'] for caption in captions])

    # Get web-scraped comments from YouTube Comment Downloader API
    comments, comments_str = get_comments(video_url)
    if comments is None:
        return jsonify({'error': 'Comments could not be retrieved for this video!'}), 500

    # Write ChatGPT prompt for generating transcript summary
    transcript_prompt = f"""
        Summarize the following YouTube transcript in 200-250 words: {transcript}
        Do not include any details about the comments.
    """

    # Ensure that transcript is under token limit with OpenAI's Tiktoken tokenizer
    if (get_token_count(transcript_prompt, "gpt-3.5-turbo") < REQUEST_TOKEN_LIMIT):
        
        # Generate transcript summary
        transcript_summary, transcript_error = ask_chatgpt(transcript_prompt, CHATGPT_SYSTEM_ROLE)

        if transcript_error is not None:
                return jsonify({'error': transcript_error}), 500

        # Write ChatGPT prompt for generating comment summary
        comments_prompt = f"""
            Here is a summary of a YouTube transcript: {transcript_summary}
            Summarize the following comments section for this video: {comments_str}
            Do not include any details about the transcript, only the comments.
            Do not give a list, but a paragraph.
        """

        # Ensure that transcript summary and comments together are under token limit
        if (get_token_count(comments_prompt, "gpt-3.5-turbo") < REQUEST_TOKEN_LIMIT):
            
            # Generate comments summary
            comments_summary, comments_error = ask_chatgpt(comments_prompt, CHATGPT_SYSTEM_ROLE)

            if comments_error is not None:
                return jsonify({'error': comments_error}), 500
            else:
                return jsonify({'video_id': video_id,
                                'video_title': YouTube(video_url).title,
                                'comments': comments,
                                'transcript_summary': transcript_summary, 
                                'comments_summary': comments_summary}), 200
        else:
            return jsonify({'error': 'This video is too long to summarize!'}), 400
    else:
        return jsonify({'error': 'This video is too long to summarize!'}), 400

@app.route('/api/get-resolutions', methods=['GET'])
def get_resolutions():
    """
    Return list of resolutions for available video streams based on given video ID.

    HTTP Method: GET

    Request Parameters:
        video_id (str): The video id of the video to fetch streams for. (required)

    Responses:
        200: A list of resolutions with video streams available to download.
        400: Missing parameters, invalid video ID, or video unavailable.
        500: An error occurred when fetching the available streams.
    
    Example:
        GET /api/get-resolutions?video_id=dQw4w9WgXcQ
    """
    # Save parameters from request
    video_id = request.args.get('video_id')

    # Check for missing parameters
    if not video_id:
        return jsonify({'error': 'Video ID is missing!'}), 400
    
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Fetch all video streams with video and audio tracks combined
        yt = YouTube(video_url)
        streams = yt.streams.filter(
            file_extension="mp4",
            type="video",
            progressive=True)
        
        # Create sorted list of available resolutions if streams found
        if streams:
            resolutions = sorted(list(set([int(stream.resolution[:-1]) for stream in streams])))
            resolutions = [str(res) + 'p' for res in resolutions]
            return jsonify({'resolutions': resolutions}), 200
        else:
            return jsonify({'resolutions': []}), 200

    except VideoUnavailable as e:
        return jsonify({'error': f'VideoUnavailable: {str(e)}'}), 400
    except RegexMatchError as e:
        return jsonify({'error': f'RegexMatchError: {str(e)}'}), 400
    except HTTPError as e:
        return jsonify({'error': str(e)}), e.response.status_code
    
@app.route('/api/get-download', methods=['GET'])
def get_download():
    """
    Return download URL based on given video ID and resolution.

    HTTP Method: GET

    Request Parameters:
        video_id (str): The video id of the video to get the download URL. (required)
        video_resolution (str): The resolution of the video stream to fetch. (required)

    Responses:
        200: A download URL for the requested video and the resolution of the video.
        400: Missing parameters, invalid video ID, video unavailable, or no streams available.
        500: An error occurred when fetching the available streams.
    
    Example:
        GET /api/get-download?video_id=dQw4w9WgXcQ&video_resolution=360p
    """

    # Save parameters from request
    video_id = request.args.get('video_id')
    video_resolution = request.args.get('video_resolution')

    # Check for missing parameters
    if not video_id:
        return jsonify({'error': 'Video ID is missing!'}), 400
    if not video_resolution:
        return jsonify({'error': 'Video resolution is missing!'}), 400
    
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Fetch first available video stream with given resolution
        yt = YouTube(video_url)
        stream = yt.streams.filter(
            file_extension="mp4",
            type="video", 
            res=video_resolution, 
            progressive=True).first()

        # Return download URL for stream if stream found
        if stream:
            return jsonify({'download_url': stream.url, 'video_resolution': video_resolution}), 200
        else:
            return jsonify({'error': 'No streams available to download the video at this resolution!'}), 400

    except VideoUnavailable as e:
        return jsonify({'error': f'VideoUnavailable: {str(e)}'}), 400
    except RegexMatchError as e:
        return jsonify({'error': f'RegexMatchError: {str(e)}'}), 400
    except HTTPError as e:
        return jsonify({'error': str(e)}), e.response.status_code

@app.route('/api/download-video', methods=['GET'])
def download_video():
    """
    Download a video file from a given download URL, upload it to Amazon S3, and
    return a pre-signed URL for the client.

    HTTP Method: GET

    Request Parameters:
        download_url (str): The download URL of the video to stream to the client. (required)
        video_title (str): The title of the video to use for the download's file name. (required)
        video_resolution (str): The resolution of the video to use for the download's file name. (required)

    Responses:
        200: A JSON object containing the pre-signed URL for the uploaded video.
        400: Missing parameters or invalid download URL.
        500: An error occurred during the download or upload process.

    Example:
        GET /api/download-video?download_url=https://example.com/video.mp4&video_title=SampleVideo&video_resolution=720p
    """

    # Save parameters from request
    download_url = request.args.get('download_url')
    video_title = request.args.get('video_title')
    video_resolution = request.args.get('video_resolution')

    # Check for missing parameters
    if not download_url:
        return jsonify({'error': 'Download URL is missing!'}), 400
    if not video_title:
        return jsonify({'error': 'Video title is missing!'}), 400
    if not video_resolution:
        return jsonify({'error': 'Video resolution is missing!'}), 400

    try:
        # Fetch video from the provided URL
        response = requests.get(download_url, stream=True)

        # Raise HTTPError if HTTP request returned unsuccessful status code
        response.raise_for_status()

        # Upload the video to S3
        s3_key = f"{video_title} [{video_resolution}].mp4"
        s3_client.upload_fileobj(response.raw, bucket_name, s3_key)

        # Generate a pre-signed URL for the uploaded video
        pre_signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # URL expiration time in seconds
        )

        return jsonify({'pre_signed_url': pre_signed_url}), 200

    except HTTPError as e:
        return jsonify({'error': str(e)}), e.response.status_code
    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 500
    except ClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    is_debug = getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(host='0.0.0.0', port=8000, debug=is_debug)