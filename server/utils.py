from youtube_transcript_api import YouTubeTranscriptApi
import os
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
import webbrowser

load_dotenv()

# OAuth Flow Setup
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly",
]
REDIRECT_URI = "http://127.0.0.1:8000/callback"

flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
flow.redirect_uri = REDIRECT_URI

# Rotating residential proxies to avoid IP bans for web-scraping
PROXIES = {
    "http": os.getenv("ROTATING_RESIDENTIAL_PROXY", ""),
    "https": os.getenv("ROTATING_RESIDENTIAL_PROXY", ""),
}

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")


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
        captions = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([caption["text"] for caption in captions])
    except:
        return None

    return transcript


def fetch_transcript_with_proxy(video_id):
    """
    Fetch captions for a given YouTube video ID using a rotating residential proxy.

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
            captions = YouTubeTranscriptApi.get_transcript(video_id, proxies=PROXIES)

        transcript = " ".join([caption["text"] for caption in captions])
    except:
        return None

    return transcript


def authenticate_youtube():
    authorization_url, state = flow.authorization_url(
        # Recommended, enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Optional, enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
        # Optional, if your application knows which user is trying to authenticate, it can use this
        # parameter to provide a hint to the Google Authentication Server.
        login_hint="aryan.shelke.2003@gmail.com",
        # Optional, set prompt to 'consent' will prompt the user for consent
        prompt="consent",
    )

    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)


def fetch_transcript_with_google_api(video_id):
    youtube = authenticate_youtube()

    request = youtube.captions().list(part="snippet", videoId=video_id)
    response = request.execute()

    if "items" not in response or not response["items"]:
        return "No captions available."

    captions = []
    for item in response["items"]:
        captions.append(
            f"Caption ID: {item['id']} | Language: {item['snippet']['language']}"
        )

    return "\n".join(captions)
