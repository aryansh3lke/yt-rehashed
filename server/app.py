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

    Examples:
        >>> get_youtube_video_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'Rick Astley - Never Gonna Give You Up (Official Music Video)'
        >>> get_youtube_video_title("invalid_url")
        None
    """

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
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
    Extract YouTube handle from different URL formats:
        - https://youtube.com/@username
        - https://www.youtube.com/@username
        - https://youtube.com/c/username
        - https://www.youtube.com/channel/UCxxxxxxxxxx
        - @username

    Args:
        url (str): The URL of the YouTube channel.




    Returns: handle in @username format or None if not found
    """
    if not url:
        return None

    # If it's already in @handle format, return as is
    if url.startswith("@"):
        return url

    # Try to extract handle from URL
    handle_patterns = [
        r"youtube\.com/(@[\w-]+)",  # matches @username in URL
        r"youtube\.com/c/([\w-]+)",  # matches /c/username format
        r"youtube\.com/channel/([\w-]+)",  # matches channel ID format
    ]

    for pattern in handle_patterns:
        match = re.search(pattern, url)
        if match:
            handle = match.group(1)
            # Add @ prefix if not present (for /c/ format)
            return handle if handle.startswith("@") else f"@{handle}"

    return None


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
        ydl_opts = {}

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

        # Options for downloading video only
        video_opts = {
            "format": f"bestvideo[height<={video_resolution[:-1]}][vcodec^=avc1]",  # Limit resolution and choose best video with H.264 codec
            "outtmpl": f"downloads/{sanitized_title}_video.mp4",
            "progress_hooks": [video_progress_hook],
            "quiet": True,
        }

        # Options for downloading audio only
        audio_opts = {
            "format": "bestaudio[ext=m4a]",  # Choose best audio
            "outtmpl": f"downloads/{sanitized_title}_audio.m4a",
            "progress_hooks": [audio_progress_hook],
            "quiet": True,
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

        video_title = get_youtube_video_title(video_id)
        return jsonify({"video_id": video_id, "video_title": video_title}), 200
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/api/get-creator-info", methods=["GET"])
def get_creater_info():
    """
    Returns the video id and title for the given video link

    HTTP Method: GET

    Request Parameters:
        channel_url (str): The URL of the creator's YouTube channel.

    Responses:
        200: Channel info including statistics, background, and crediblity score
        400: Missing parameters or invalid link.
        500: An error occurred when fetching channel info or analyzing credibility.

    Example:
        GET /api/get-creator-info?channel_url=https://www.youtube.com/@mrbeast
    """
    channel_url = request.args.get("channel_url")

    if channel_url is None:
        return jsonify({"error": "Channel URL is missing!"}), 400

    # Extract handle from URL
    handle = extract_youtube_handle(channel_url)

    if handle is None:
        return jsonify({"error": "Invalid Channel URL!"}), 400

    creator_info = {"channel": channel_url}

    # Fetch channel ID based on handle
    try:
        id_response = requests.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={handle}&key={YOUTUBE_API_KEY}"
        ).json()
        if "items" in id_response and len(id_response["items"]) > 0:
            id = id_response["items"][0]["id"]
            creator_info["id"] = id
            creator_info["handle"] = handle

        else:
            print(f"Could not find the channel for the handle {handle}")
    except:
        return jsonify({"error": "Creator handle does not exist!"}), 400

    # Fetch channel statistics based on ID
    try:
        statistics_response = requests.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={id}&key={YOUTUBE_API_KEY}"
        ).json()

        if "items" in statistics_response and len(statistics_response["items"]) > 0:
            creator_info["statistics"] = statistics_response["items"][0]["statistics"]
        else:
            return (
                jsonify({"error": f"Channel statistics do not exist for {handle}!"}),
                500,
            )
    except:
        return jsonify({"error": "Channel statistics could not be fetched!"}), 500

    # Fetch channel avatar
    try:
        avatar_response = requests.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={id}&key={YOUTUBE_API_KEY}"
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
            creator_info["avatar"] = "https://www.youtube.com/img/desktop/yt_1200.png"
    except Exception as e:
        print(f"Error fetching avatar: {str(e)}")
        creator_info["avatar"] = "https://www.youtube.com/img/desktop/yt_1200.png"

    # Fetch Channel Title
    try:
        title_response = requests.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={id}&key={YOUTUBE_API_KEY}"
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
        Analyze the current credibility of the following creator as of {datetime.now().strftime('%Y-%m-%d')}: 
        {creator_info["title"]} ({creator_info["handle"]})
        Current subscriber count: {creator_info["statistics"].get("subscriberCount", "Unknown")}

        Return your analysis in the following JSON format:
        {{
            "points": [
                // List of 3-5 specific points about the creator's current credibility
                // Each point should focus on recent events, current status, and up-to-date information
                // IMPORTANT: Recent controversies or misleading content should be heavily weighted
                // For smaller creators, focus on their expertise, content quality, and community trust
            ],
            "score": // A number between 0 and 100 representing current credibility
        }}
        
        Consider the following factors in your analysis, with special emphasis on recent events:
        - Any recent controversies, misleading content, or factual inaccuracies (these should HEAVILY impact the score)
        - Recent retractions, corrections, or apologies for incorrect information
        - Current educational background or expertise in their niche
        - Recent verification of claims and use of reliable sources
        - Current track record of maintaining journalistic integrity
        - Recent public perception and professional critiques
        - Current content quality and accuracy
        - Recent changes in content style or direction
        - Current standing in their niche
        - Recent partnerships or business ventures
        - Current community interactions and controversies
        - Recent growth trends and subscriber engagement
        - For smaller creators:
          * Focus on their expertise in their specific niche
          * Consider their content quality relative to their experience level
          * Evaluate their community engagement and trust
          * Look at their consistency and dedication
          * Consider their potential for growth and improvement
        
        Scoring Guidelines:
        - Start at 100 points
        - Subtract 30-50 points for any recent major controversies or proven instances of deliberate misinformation
        - Subtract 20-30 points for current lack of relevant expertise
        - Subtract 15-25 points for recent patterns of unverified claims
        - Subtract 10-20 points for each recent instance of retracted misinformation
        - Add back points only for consistently demonstrated recent expertise
        - For smaller creators:
          * Be more lenient with production quality deductions
          * Consider their growth potential and dedication
          * Focus on their expertise in their specific niche
          * Consider their community engagement and trust
        
        The score should reflect current credibility and err on the side of being harsh rather than lenient.
        For smaller creators, focus on their potential and dedication rather than just current metrics.
        Ensure the response is valid JSON.
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
