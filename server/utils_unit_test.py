from utils import *
from unittest.mock import patch


video_url = "https://www.youtube.com/watch?v=E5BaGpnrgao"
video_id = "E5BaGpnrgao"

# def test_extract_video_id():
#     assert extract_video_id(video_url) == video_id

# def test_fetch_transcript():
#     assert fetch_transcript(video_id) is not None

# def test_fetch_transcript_with_proxy():
#     assert fetch_transcript_with_proxy(video_id) is not None

def test_fetch_transcript_with_google_api():
    assert fetch_transcript_with_google_api(video_id) is not None
