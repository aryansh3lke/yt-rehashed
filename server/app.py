from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
from itertools import islice
import json
from openai import OpenAI, OpenAIError
import os
import re
import requests
from requests.exceptions import HTTPError
import subprocess
import tiktoken
from waitress import serve
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI API client
client = OpenAI()

# Initialize YouTube Comment Downloader
downloader = YoutubeCommentDownloader()

# Initialize YouTube API key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Rotating residential proxies to avoid IP bans for web-scraping
proxies = {
    "http": os.getenv("ROTATING_RESIDENTIAL_PROXY", ""),
    "https": os.getenv("ROTATING_RESIDENTIAL_PROXY", ""),
}

# Global variables for tracking download progress
combined_progress = 0
progress = {"video": 0, "audio": 0, "ffmpeg": 0}

# ChatGPT-3.5-turbo Model
CHATGPT_TOKEN_LIMIT = 16385
RESPONSE_TOKEN_LIMIT = 500
REQUEST_TOKEN_LIMIT = CHATGPT_TOKEN_LIMIT - RESPONSE_TOKEN_LIMIT
CHATGPT_SUMMARIZING_ROLE = """
    You are a summarizing assistant for YouTube videos that restates the main 
    points of the video and summarizes viewer comments.
"""
CHATGPT_ANALYZING_ROLE = """
    You are an analyzing assistant for YouTube content creators that performs
    a background analysis on the creator's channel and provides a concise
    summary of the creator's background. 
"""
CHATGPT_SCORE_ROLE = """
    You are a scoring assistant for YouTube content creators that scores the creator's
    credibility, content quality, and engagement. You should not include any details
    about the research or analysis you conducted. Your output should be a single
    floating point number between 0 and 100.
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

    regex = r"(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/\n\s]+/\S*/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})"
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
        if os.getenv("ENV", "") == "development":
            captions = YouTubeTranscriptApi.get_transcript(video_id)
        else:
            captions = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)

        transcript = " ".join([caption["text"] for caption in captions])
    except:
        return None

    return captions, transcript


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
        popular_comments = downloader.get_comments_from_url(
            video_url, sort_by=SORT_BY_POPULAR
        )
        comments, comments_str = [], ""
        for index, comment in enumerate(islice(popular_comments, comment_count)):
            comments.append(comment)
            comments_str += str(index + 1) + ") " + comment["text"] + "\n"

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
                {"role": "user", "content": prompt},
            ],
            max_tokens=RESPONSE_TOKEN_LIMIT,
            temperature=0.7,
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
    """

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get("title", None)
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
    return re.sub(r'[\/:*?"<>|]', "", title)


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
    global progress
    video_progress = min(40.0, progress["video"] * 0.4)
    audio_progress = min(40.0, progress["audio"] * 0.4)
    ffmpeg_progress = min(20.0, progress["ffmpeg"] * 0.2)
    combined_progress = video_progress + audio_progress + ffmpeg_progress


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
        if char.isnumeric() or char == ".":
            clean_str += char

    if os.getenv("OS", "") == "macOS":
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
    if d["status"] == "downloading":
        try:
            progress["video"] = float(clean_hook_str(d["_percent_str"]))
            update_combined_progress()
        except ValueError as e:
            print(f"Error converting video progress to float: {e}")
            progress["video"] = 0


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
    if d["status"] == "downloading":
        try:
            progress["audio"] = float(clean_hook_str(d["_percent_str"]))
            update_combined_progress()
        except ValueError as e:
            print(f"Error converting audio progress to float: {e}")
            progress["audio"] = 0


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
    match = re.search(r"time=(\d+:\d+:\d+.\d+)", line)
    if match:
        time_str = match.group(1)
        h, m, s = map(float, time_str.split(":"))
        total_seconds = h * 3600 + m * 60 + s
        progress["ffmpeg"] = (total_seconds / estimated_duration) * 100
        update_combined_progress()


def extract_youtube_handle(url):
    """
    Extract YouTube handle or channel ID from different URL formats:
        - https://youtube.com/@username
        - https://www.youtube.com/@username
        - https://youtube.com/c/username
        - https://youtube.com/user/username
        - https://www.youtube.com/channel/UCxxxxxxxxxx
        - @username

    Args:
        url (str): The URL of the YouTube channel.

    Returns:
        tuple: (handle or None, channel_id or None)
        If handle is found, returns (handle, None)
        If channel ID is found, returns (None, channel_id)
        If neither is found, returns (None, None)
    """
    if not url:
        return None, None

    # If it's already in @handle format
    if url.startswith("@"):
        return url, None

    # Try to extract channel ID first
    channel_id_pattern = r"youtube\.com/channel/([\w-]+)"
    channel_match = re.search(channel_id_pattern, url)
    if channel_match:
        return None, channel_match.group(1)

    # Try to extract handle from URL
    handle_patterns = [
        r"youtube\.com/(@[\w-]+)",  # matches @username in URL
        r"youtube\.com/c/([\w-]+)",  # matches /c/username format
        r"youtube\.com/user/([\w-]+)",  # matches /user/username format
    ]

    for pattern in handle_patterns:
        match = re.search(pattern, url)
        if match:
            handle = match.group(1)
            # Add @ prefix if not present (for /c/ and /user/ formats)
            return handle if handle.startswith("@") else f"@{handle}", None

    return None, None


@app.route("/")
def hello():
    return "You have reached the Youtube Rehashed Flask backend server!"


@app.route("/api/get-summaries", methods=["GET"])
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
    video_url = request.args.get("video_url")

    # Check for missing parameters
    if not video_url:
        return jsonify({"error": "Video URL is missing!"}), 400

    # Extract video ID from video URL
    video_id = extract_video_id(video_url)
    if video_id is None:
        return jsonify({"error": "Please enter a valid YouTube URL!"}), 400

    # Fetch YouTube transcript using YouTubeTranscriptAPI
    captions, transcript = fetch_transcript(video_id)
    if transcript is None:
        return (
            jsonify(
                {"error": "YouTube video does not exist or is missing a transcript!"}
            ),
            400,
        )

    # Get web-scraped comments from the YouTube Comment Downloader API
    comments, comments_str = get_comments(video_url)
    if comments is None:
        return (
            jsonify({"error": "Comments could not be retrieved for this video!"}),
            500,
        )

    # Write ChatGPT prompt for generating video summary
    transcript_prompt = f"""
        Summarize the following YouTube transcript in 200-250 words: {transcript}
        Do not include any details about the comments.
    """

    # Ensure that transcript is under token limit with OpenAI's Tiktoken tokenizer
    if get_token_count(transcript_prompt, "gpt-3.5-turbo") < REQUEST_TOKEN_LIMIT:

        # Generate transcript summary
        video_summary, transcript_error = ask_chatgpt(
            transcript_prompt, CHATGPT_SUMMARIZING_ROLE
        )

        if transcript_error is not None:
            return jsonify({"error": transcript_error}), 500

        # Write ChatGPT prompt for generating comment summary
        comments_prompt = f"""
            Here is a summary of a YouTube transcript: {video_summary}
            Summarize the following comments section for this video: {comments_str}
            Do not include any details about the transcript, only the comments.
            Do not give a list, but a paragraph.
        """

        # Ensure that transcript summary and comments together are under token limit
        if get_token_count(comments_prompt, "gpt-3.5-turbo") < REQUEST_TOKEN_LIMIT:

            # Generate comments summary
            comments_summary, comments_error = ask_chatgpt(
                comments_prompt, CHATGPT_SUMMARIZING_ROLE
            )

            if comments_error is not None:
                return jsonify({"error": comments_error}), 500
            else:
                return (
                    jsonify(
                        {
                            "video_id": video_id,
                            "video_title": get_youtube_video_title(video_url),
                            "captions": captions,
                            "comments": comments,
                            "video_summary": video_summary,
                            "comments_summary": comments_summary,
                        }
                    ),
                    200,
                )
        else:
            return jsonify({"error": "This video is too long to summarize!"}), 400
    else:
        return jsonify({"error": "This video is too long to summarize!"}), 400


@app.route("/api/get-resolutions", methods=["GET"])
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
    video_id = request.args.get("video_id")

    # Check for missing parameters
    if not video_id:
        return jsonify({"error": "Video ID is missing!"}), 400

    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get("formats", [])

            resolutions = []

            for f in formats:
                height = f.get("height")
                if height is not None and 144 <= height <= 1080:
                    resolutions.append(f"{height}p")

            resolutions = sorted(set(resolutions), key=lambda x: int(x[:-1]))

            return jsonify({"resolutions": resolutions}), 200

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": f"DownloadError: {str(e)}"}), 400
    except yt_dlp.utils.ExtractorError as e:
        return jsonify({"error": f"ExtractorError: {str(e)}"}), 400
    except yt_dlp.utils.PostProcessingError as e:
        return jsonify({"error": f"PostProcessingError: {str(e)}"}), 400
    except HTTPError as e:
        return jsonify({"error": str(e)}), e.response.status_code


@app.route("/api/get-download", methods=["GET"])
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
    progress = {"video": 0, "audio": 0, "ffmpeg": 0}

    # Save parameters from request
    video_id = request.args.get("video_id")
    video_resolution = request.args.get("video_resolution")

    # Check for missing parameters
    if not video_id:
        return jsonify({"error": "Video ID is missing!"}), 400
    if not video_resolution:
        return jsonify({"error": "Video resolution is missing!"}), 400

    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        sanitized_title = get_youtube_video_title(video_url)

        # Common options for both video and audio downloads
        common_opts = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "quiet": True,
        }

        # Options for downloading video only
        video_opts = {
            **common_opts,
            "format": f"bestvideo[height<={video_resolution[:-1]}][vcodec^=avc1]",  # Limit resolution and choose best video with H.264 codec
            "outtmpl": f"downloads/{sanitized_title}_video.mp4",
            "progress_hooks": [video_progress_hook],
        }

        # Options for downloading audio only
        audio_opts = {
            **common_opts,
            "format": "bestaudio[ext=m4a]",  # Choose best audio
            "outtmpl": f"downloads/{sanitized_title}_audio.m4a",
            "progress_hooks": [audio_progress_hook],
        }

        # Download video
        print(f"Starting video download for {video_url}")
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            estimated_duration = info_dict.get("duration", 0)
            print(f"Video info extracted, duration: {estimated_duration}")
            ydl.download([video_url])
            print("Video download completed")

        # Download audio
        print("Starting audio download")
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([video_url])
            print("Audio download completed")

        # Paths to the downloaded files
        video_file = f"downloads/{sanitized_title}_video.mp4"
        audio_file = f"downloads/{sanitized_title}_audio.m4a"
        output_file = f"downloads/{sanitized_title} [{video_resolution}].mp4"

        print(
            f"Checking if files exist: video={os.path.exists(video_file)}, audio={os.path.exists(audio_file)}"
        )

        # Merge video and audio using ffmpeg without re-encoding
        print("Starting ffmpeg merge")
        ffmpeg_command = [
            "ffmpeg",
            "-i",
            video_file,
            "-i",
            audio_file,
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            output_file,
        ]
        print(f"FFmpeg command: {' '.join(ffmpeg_command)}")
        process = subprocess.Popen(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        for line in process.stdout:
            print(f"FFmpeg output: {line.strip()}")
            ffmpeg_progress_hook(line, estimated_duration)
        process.wait()
        print(f"FFmpeg process completed with return code: {process.returncode}")

        # Cleanup: Delete the separate video and audio files
        print("Cleaning up temporary files")
        os.remove(video_file)
        os.remove(audio_file)

        @after_this_request
        def remove_file(response):
            global combined_progress
            global progress
            try:
                os.remove(output_file)
            except Exception as e:
                print(f"Error removing file: {str(e)}")
            return response

        # Stream the merged video file back to the user
        return send_file(output_file, as_attachment=True)

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": f"DownloadError: {str(e)}"})
    except yt_dlp.utils.ExtractorError as e:
        return jsonify({"error": f"ExtractorError: {str(e)}"})
    except yt_dlp.utils.PostProcessingError as e:
        return jsonify({"error": f"PostProcessingError: {str(e)}"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"FFmpeg error: {str(e)}"})
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"})


@app.route("/api/get-progress", methods=["GET"])
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
    return jsonify({"progress": combined_progress}), 200


@app.route("/api/get-video-info", methods=["GET"])
def get_video_info():
    """
    Returns the video id and title for the given video link

    HTTP Method: GET

    Request Parameters:
        video_url (str): The URL of the YouTube video.

    Responses:
        200: The video ID and title
        400: Missing parameters or invalid link.
        500: An error occurred when fetching the video info.

    Example:
        GET /api/get-video-info?video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """

    # Save parameters from request
    video_url = request.args.get("video_url")

    # Check for missing parameters
    if not video_url:
        return jsonify({"error": "Video URL is missing!"}), 400

    try:
        video_id = extract_video_id(video_url)

        if video_id is None:
            return jsonify({"error": "Please enter a valid YouTube URL!"}), 400

        video_title = get_youtube_video_title(video_url)
        return jsonify({"video_id": video_id, "video_title": video_title}), 200
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/api/get-creator-info", methods=["GET"])
def get_creater_info():
    """
    Returns the channel info for the given channel URL

    HTTP Method: GET

    Request Parameters:
        channel_url (str): The URL of the creator's YouTube channel.

    Responses:
        200: Channel info including statistics, background, and credibility score
        400: Missing parameters or invalid link.
        500: An error occurred when fetching channel info or analyzing credibility.

    Example:
        GET /api/get-creator-info?channel_url=https://www.youtube.com/@mrbeast
    """
    channel_url = request.args.get("channel_url")

    if channel_url is None:
        return jsonify({"error": "Channel URL is missing!"}), 400

    # Extract handle or channel ID from URL
    handle, channel_id = extract_youtube_handle(channel_url)
    creator_info = {"channel": channel_url}

    try:
        # If we have a channel ID, fetch the handle first
        if channel_id:
            channel_response = requests.get(
                f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={YOUTUBE_API_KEY}"
            ).json()

            if "items" in channel_response and len(channel_response["items"]) > 0:
                custom_url = channel_response["items"][0]["snippet"].get("customUrl")
                if custom_url:
                    handle = (
                        custom_url if custom_url.startswith("@") else f"@{custom_url}"
                    )
                creator_info["id"] = channel_id
                creator_info["handle"] = handle
            else:
                return jsonify({"error": "Channel not found!"}), 400
        else:
            # Use handle to get channel ID
            id_response = requests.get(
                f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={handle[1:]}&key={YOUTUBE_API_KEY}"
            ).json()

            if "items" in id_response and len(id_response["items"]) > 0:
                channel_id = id_response["items"][0]["id"]
                creator_info["id"] = channel_id
                creator_info["handle"] = handle
            else:
                return jsonify({"error": "Creator handle does not exist!"}), 400

    except Exception as e:
        print(f"Error fetching channel info: {str(e)}")
        return jsonify({"error": "Failed to fetch channel information"}), 500

    # Fetch channel statistics based on ID
    try:
        statistics_response = requests.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
        ).json()

        if "items" in statistics_response and len(statistics_response["items"]) > 0:
            creator_info["statistics"] = statistics_response["items"][0]["statistics"]
        else:
            return (
                jsonify({"error": f"Channel statistics do not exist for {handle}!"}),
                500,
            )
    except:
        return (
            jsonify({"error": f"Channel statistics could not be fetched!"}),
            500,
        )

    # Fetch channel avatar
    try:
        avatar_response = requests.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={YOUTUBE_API_KEY}"
        ).json()

        if "items" in avatar_response and len(avatar_response["items"]) > 0:
            thumbnails = avatar_response["items"][0]["snippet"]["thumbnails"]
            # Try different thumbnail sizes in order of preference
            if "maxres" in thumbnails:
                creator_info["avatar"] = thumbnails["maxres"]["url"]
            elif "high" in thumbnails:
                creator_info["avatar"] = thumbnails["high"]["url"]
            elif "medium" in thumbnails:
                creator_info["avatar"] = thumbnails["medium"]["url"]
            elif "default" in thumbnails:
                creator_info["avatar"] = thumbnails["default"]["url"]
            else:
                creator_info["avatar"] = (
                    "https://www.youtube.com/img/desktop/yt_1200.png"
                )
        else:
            print(f"No avatar found for channel ID: {channel_id}")
            creator_info["avatar"] = "https://www.youtube.com/img/desktop/yt_1200.png"
    except Exception as e:
        print(f"Error fetching avatar: {str(e)}")
        creator_info["avatar"] = "https://www.youtube.com/img/desktop/yt_1200.png"

    # Verify the avatar URL is accessible
    try:
        avatar_check = requests.head(creator_info["avatar"], timeout=5)
        if avatar_check.status_code != 200:
            print(f"Avatar URL not accessible: {creator_info['avatar']}")
            creator_info["avatar"] = "https://www.youtube.com/img/desktop/yt_1200.png"
    except Exception as e:
        print(f"Error checking avatar URL: {str(e)}")
        creator_info["avatar"] = "https://www.youtube.com/img/desktop/yt_1200.png"

    # Fetch Channel Title
    try:
        title_response = requests.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={YOUTUBE_API_KEY}"
        ).json()
        if "items" in title_response and len(title_response["items"]) > 0:
            creator_info["title"] = title_response["items"][0]["snippet"]["title"]
        else:
            return (
                jsonify({"error": f"Channel title does not exist for {handle}!"}),
                500,
            )
    except:
        return jsonify({"error": "Channel title could not be fetched!"}), 500

    # Generate Background Information
    try:
        background_prompt = f"""
        Give a parapgraph of background information about the following creator:
        {creator_info["title"]} ({creator_info["handle"]})
        """

        background_response, _ = ask_chatgpt(background_prompt, CHATGPT_ANALYZING_ROLE)
        creator_info["background"] = background_response
    except:
        return jsonify({"error": "Background information could not be fetched!"}), 500

    # Generate Credibility Points and Score
    try:
        credibility_prompt = f"""
        You are a YouTube channel credibility analyzer. Analyze the credibility of this creator:
        Channel: {creator_info["title"]} ({creator_info["handle"]})
        Subscriber Count: {creator_info["statistics"].get("subscriberCount", "Unknown")}
        Video Count: {creator_info["statistics"].get("videoCount", "Unknown")}
        Total Views: {creator_info["statistics"].get("viewCount", "Unknown")}

        Provide a factual, well-researched analysis focusing on:
        1. Content accuracy and fact-checking practices
        2. Professional background and expertise in their field
        3. Transparency about sponsorships and potential biases
        4. Track record of corrections when mistakes are made
        5. Quality of sources and research methods
        6. Community engagement and response to criticism
        7. Consistency and reliability of information
        8. Industry recognition and peer reviews

        Return your analysis in the following JSON format:
        {{
            "points": [
                // 3-5 specific, factual points about the creator's credibility
                // Each point must be based on verifiable information
                // Focus on objective measures rather than subjective opinions
                // Include both strengths and areas of concern
                // Cite specific examples where possible
                // Do not use objects or nested structures, only strings
                // Don't put the actual score deduction in the points, just the points
            ],
            "score": // A number between 0 and 100 representing credibility
        }}

        Scoring Guidelines:
        - Start at 70 as a baseline for established creators
        - Add or subtract points based on VERIFIED information only
        - Do not speculate or make assumptions
        - Consider the following factors:
          * Verified expertise and credentials (+10-20)
          * Consistent fact-checking practices (+10-15)
          * Transparent disclosure of sponsorships/biases (+5-10)
          * Professional affiliations and certifications (+5-10)
          * Documented instances of misinformation (-20-30)
          * Lack of transparency about qualifications (-10-15)
          * Pattern of unverified claims (-15-20)
          * Failure to correct proven errors (-10-15)

        The score should be conservative and based only on verifiable information.
        If certain information cannot be verified, do not include it in the scoring.
        """

        credibility_response, _ = ask_chatgpt(
            credibility_prompt, CHATGPT_ANALYZING_ROLE
        )
        credibility_data = json.loads(credibility_response)
        creator_info["credibilityPoints"] = credibility_data["points"]
        creator_info["credibilityScore"] = credibility_data["score"]
    except Exception as e:
        return jsonify({"error": "Credibility analysis could not be completed"}), 500

    # Generate Content Quality Score
    try:
        content_quality_prompt = f"""
        Return a score between 0 and 100 for the following creator's content quality:
        {creator_info["title"]} ({creator_info["handle"]})

        You need to conduct your own research to gather the necessary data using the web.

        Take the following into account:
        - Quality and accuracy of the content
        - Creativity and uniqueness of the content
        - Reasonable upload frequency for their format of content

        Make sure you return only a single floating point number between 0 and 100.
        Do not return any text other than the score.
        """

        content_quality_response, _ = ask_chatgpt(
            content_quality_prompt, CHATGPT_SCORE_ROLE
        )
        creator_info["contentQualityScore"] = re.search(
            r"\d+", content_quality_response
        ).group()
    except Exception as e:
        return (
            jsonify({"error": "Content quality analysis could not be completed"}),
            500,
        )

    # Generate Engagement Score
    try:
        engagement_prompt = f"""
        Calculate a score between 0 and 100 for the following creator's engagement:
        {creator_info["title"]} ({creator_info["handle"]})

        You need to conduct your own research to gather the necessary data using the web.

        Take the following into account:
        - Number of views, likes, comments, and shares
        - Engagement rate (comments per view, likes per view, shares per view)
        - Overall impact and reach of the content

        Make sure you return only a single floating point number between 0 and 100.
        Do not return any text other than the score.
        """

        engagement_response, _ = ask_chatgpt(engagement_prompt, CHATGPT_SCORE_ROLE)
        creator_info["engagementScore"] = re.search(r"\d+", engagement_response).group()
    except Exception as e:
        return jsonify({"error": "Engagement analysis could not be completed"}), 500

    return jsonify({"creator_info": creator_info}), 200


if __name__ == "__main__":
    # development
    if os.getenv("ENV", "") == "development":
        app.run(host="0.0.0.0", port=8000, debug=True)
    # production
    else:
        serve(app, host="0.0.0.0", port=8000)
