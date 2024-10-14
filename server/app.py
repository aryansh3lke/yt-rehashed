from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
from itertools import islice
from openai import OpenAI, OpenAIError
import os
import re
from requests.exceptions import HTTPError
import subprocess
import tiktoken
from waitress import serve
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

load_dotenv()

app = Flask(__name__)
CORS(app)
client = OpenAI()
downloader = YoutubeCommentDownloader()

# Rotating residential proxies to avoid IP bans for web-scraping
proxies = {
    "http": "http://20rpwnh3:3ohshcothlGQkc7Q@proxy.proxy-cheap.com:31112",
    "https": "http://20rpwnh3:3ohshcothlGQkc7Q@proxy.proxy-cheap.com:31112"
}

# Global variables for tracking download progress
combined_progress = 0
progress = {
    'video': 0,
    'audio': 0,
    'ffmpeg': 0
}

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
    match = re.search(regex, url)
    return match.group(1) if match else None

def fetch_transcript(video_id):
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
        >>> fetch_transcript("abc123XYZ")
        [{'start': 0.0, 'duration': 4.0, 'text': 'Hello world'}, ...]
        >>> fetch_transcript("invalid_id")
        None
    """

    try:
        if os.getenv('ENV', '') == 'development':
            captions = YouTubeTranscriptApi.get_transcript(video_id)
        else:
            captions = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)

        transcript = ' '.join([caption['text'] for caption in captions])
    except:
        return None
    
    return transcript

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

def get_youtube_video_title(video_url):
    """
    Retrieve the title of a YouTube video from its URL.

    This function uses the yt-dlp library to extract the title of a YouTube video from the provided URL.

    Args:
        video_url (str): The URL of the YouTube video.

    Returns:
        str: The title of the YouTube video if successful, or None if the title could not be retrieved.

    Examples:
        >>> get_youtube_video_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'Rick Astley - Never Gonna Give You Up (Official Music Video)'
        >>> get_youtube_video_title("invalid_url")
        None
    """
     
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get('title', None)
        return video_title

def sanitize_title(title):
    """
    Sanitize the video title by removing invalid characters.

    This function removes characters that are not allowed in file names from the provided video title.

    Args:
        title (str): The original video title.

    Returns:
        str: The sanitized video title with invalid characters removed.

    Examples:
        >>> sanitize_title("My Video: How to *Make* Money?")
        'My Video How to Make Money'
        >>> sanitize_title("Invalid/Characters|In*Title")
        'InvalidCharactersInTitle'
    """
    return re.sub(r'[\/:*?"<>|]', '', title)

def update_combined_progress():
    """
    Update the combined progress of the download.

    This function calculates the combined progress based on the individual
    progress of video, audio, and ffmpeg tasks. The combined progress is
    updated as a global variable.

    Returns:
        None
    """

    global combined_progress
    video_progress = min(40.0, progress['video'] * 0.4)
    audio_progress = min(40.0, progress['audio'] * 0.4)
    ffmpeg_progress = min(20.0, progress['ffmpeg'] * 0.2)
    combined_progress =  video_progress + audio_progress + ffmpeg_progress

def clean_hook_str(ansi_str):
    """
    Clean the ANSI escape codes from the progress string.

    This function removes any ANSI escape codes from the progress string
    and extracts the numeric part of the string.

    Args:
        ansi_str (str): The progress string containing ANSI escape codes.

    Returns:
        str: The cleaned progress string containing only numeric characters and a decimal point.

    Examples:
        >>> clean_str = clean_hook_str(' 45.4%')
        '45.4'
    """
    
    clean_str = ""
    for char in ansi_str:
        if char.isnumeric() or char == '.':
            clean_str += char
    
    if os.getenv('ENV', '') == 'development':
        return clean_str[3:]

    return clean_str

def video_progress_hook(d):
    """
    Update the video download progress.

    This function is called during the video download process to update
    the progress of the video download. It cleans the progress string,
    converts it to a float, and updates the global progress dictionary.

    Args:
        d (dict): A dictionary containing the download status and progress.

    Returns:
        None
    """

    global progress
    if d['status'] == 'downloading':
        try:
            progress['video'] = float(clean_hook_str(d['_percent_str']))
            update_combined_progress()
        except ValueError as e:
            print(f"Error converting video progress to float: {e}")
            progress['video'] = 0

def audio_progress_hook(d):
    """
    Update the audio download progress.

    This function is called during the audio download process to update
    the progress of the audio download. It cleans the progress string,
    converts it to a float, and updates the global progress dictionary.

    Args:
        d (dict): A dictionary containing the download status and progress.

    Returns:
        None
    """

    global progress
    if d['status'] == 'downloading':
        try:
            progress['audio'] = float(clean_hook_str(d['_percent_str']))
            update_combined_progress()
        except ValueError as e:
            print(f"Error converting audio progress to float: {e}")
            progress['audio'] = 0

def ffmpeg_progress_hook(line, estimated_duration):
    """
    Update the ffmpeg processing progress.

    This function is called during the ffmpeg processing to update the
    progress of the ffmpeg task. It extracts the time from the ffmpeg
    output line, calculates the progress, and updates the global progress
    dictionary.

    Args:
        line (str): A line of output from the ffmpeg process.
        estimated_duration (float): The estimated duration of the ffmpeg process in seconds.

    Returns:
        None

    Examples:
        >>> line = 'frame=  100 fps=0.0 q=-1.0 Lsize=    1024kB time=00:00:05.00 bitrate=1677.8kbits/s speed=  10x'
        >>> estimated_duration = 10.0
        >>> ffmpeg_progress_hook(line, estimated_duration)
    """

    global progress
    match = re.search(r'time=(\d+:\d+:\d+.\d+)', line)
    if match:
        time_str = match.group(1)
        h, m, s = map(float, time_str.split(':'))
        total_seconds = h * 3600 + m * 60 + s
        progress['ffmpeg'] = (total_seconds / estimated_duration) * 100
        update_combined_progress()

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

    # Fetch YouTube transcript using YouTubeTranscriptAPI
    transcript = fetch_transcript(video_id)
    if transcript is None:
        return jsonify({'error': 'YouTube video does not exist or is missing a transcript!'}), 400
        
    # Get web-scraped comments from the YouTube Comment Downloader API
    comments, comments_str = get_comments(video_url)
    if comments is None:
        return jsonify({'error': 'Comments could not be retrieved for this video!'}), 500

    # Write ChatGPT prompt for generating video summary
    transcript_prompt = f"""
        Summarize the following YouTube transcript in 200-250 words: {transcript}
        Do not include any details about the comments.
    """

    # Ensure that transcript is under token limit with OpenAI's Tiktoken tokenizer
    if (get_token_count(transcript_prompt, "gpt-3.5-turbo") < REQUEST_TOKEN_LIMIT):
        
        # Generate transcript summary
        video_summary, transcript_error = ask_chatgpt(transcript_prompt, CHATGPT_SYSTEM_ROLE)

        if transcript_error is not None:
                return jsonify({'error': transcript_error}), 500

        # Write ChatGPT prompt for generating comment summary
        comments_prompt = f"""
            Here is a summary of a YouTube transcript: {video_summary}
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
                                'video_title': get_youtube_video_title(video_url),
                                'comments': comments,
                                'video_summary': video_summary, 
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
        ydl_opts = {}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])
            
            resolutions = []
            
            for f in formats:
                height = f.get('height')
                if height is not None and 144 <= height <= 1080:
                    resolutions.append(f'{height}p')
            
            resolutions = sorted(set(resolutions), key=lambda x: int(x[:-1]))

            return jsonify({'resolutions': resolutions}), 200
    
    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': f'DownloadError: {str(e)}'}), 400
    except yt_dlp.utils.ExtractorError as e:
        return jsonify({'error': f'ExtractorError: {str(e)}'}), 400
    except yt_dlp.utils.PostProcessingError as e:
        return jsonify({'error': f'PostProcessingError: {str(e)}'}), 400
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
    # Reset progress at the start of the download
    global combined_progress
    global progress
    combined_progress = 0
    progress = {'video': 0, 'audio': 0, 'ffmpeg': 0}    

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
        sanitized_title = get_youtube_video_title(video_url)

        # Options for downloading video only
        video_opts = {
            'format': f'bestvideo[height<={video_resolution[:-1]}][vcodec^=avc1]',  # Limit resolution and choose best video with H.264 codec
            'outtmpl': f'downloads/{sanitized_title}_video.mp4',
            'progress_hooks': [video_progress_hook],
        }
        
        # Options for downloading audio only
        audio_opts = {
            'format': 'bestaudio[ext=m4a]',  # Choose best audio
            'outtmpl': f'downloads/{sanitized_title}_audio.m4a',
            'progress_hooks': [audio_progress_hook],
        }
        
        # Download video
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            estimated_duration = info_dict.get('duration', 0)
            ydl.download([video_url])
        
        # Download audio
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([video_url])
        
        # Paths to the downloaded files
        video_file = f'downloads/{sanitized_title}_video.mp4'
        audio_file = f'downloads/{sanitized_title}_audio.m4a'
        output_file = f'downloads/{sanitized_title} [{video_resolution}].mp4'
        
        # Merge video and audio using ffmpeg without re-encoding
        ffmpeg_command = [
            'ffmpeg', '-i', video_file, '-i', audio_file, '-c:v', 'copy', '-c:a', 'copy', output_file
        ]
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            ffmpeg_progress_hook(line, estimated_duration)
        process.wait()

        # Reset progress at the end of the download
        combined_progress = 0
        progress = {'video': 0, 'audio': 0, 'ffmpeg': 0}
        
        # Cleanup: Delete the separate video and audio files
        os.remove(video_file)
        os.remove(audio_file)

        @after_this_request
        def remove_file(response):
            try:
                os.remove(output_file)
            except Exception as e:
                print(f"Error removing file: {str(e)}")
            return response

        # Stream the merged video file back to the user
        return send_file(output_file, as_attachment=True)
        
    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': f'DownloadError: {str(e)}'})
    except yt_dlp.utils.ExtractorError as e:
        return jsonify({'error':f'ExtractorError: {str(e)}'})
    except yt_dlp.utils.PostProcessingError as e:
        return jsonify({'error':f'PostProcessingError: {str(e)}'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'FFmpeg error: {str(e)}'})
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'})

@app.route('/api/get-progress', methods=['GET'])
def get_progress():
    """
    Return the current combined progress of the download.

    HTTP Method: GET

    Responses:
        200: The current value of combined_progress.
        500: An error occurred while fetching the progress.

    Example:
        GET /api/get-progress
    """
    global combined_progress
    return jsonify({'progress': combined_progress}), 200

if __name__ == "__main__":
    # development
    if os.getenv('ENV', '') == 'development':
        app.run(host='0.0.0.0', port=8000, debug=True)
    # production
    else:
        serve(app, host="0.0.0.0", port=8000)