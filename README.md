# YT Rehashed

An AI tool to quickly generate quality summaries of YouTube videos and download videos at high resolutions. Summarize and download your videos here: [ytrehashed.com](ytrehashed.com)

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Usage](#usage)
5. [Installation](#installation)

## Introduction

This full-stack React-Flask web application is designed to help users quickly grasp the content of YouTube videos through summaries generated with the help of OpenAI's API and ChatGPT-3.5-turbo. This tool is especially useful for students, researchers, and anyone who wants to save time while consuming long-form video content.

When a user submits the link to their YouTube video on the React Router frontend, a REST API call is made to the Flask backend to extract the video's transcript and comments. Rather than reinventing the wheel and webscraping this information, YT Rehashed takes advantage of existing Python libraries that handle each task. Once this information is obtained, ChatGPT is prompted to summarize both the video and the comments section with OpenAI's API. The transcript, comments, and summaries are all returned together to the frontend for the user to see.

The user also has the option to download the given video at any of the available resolutions. With the YT-DLP library, the audio and video streams are downloaded separately since  combined streams are not available at high resolutions. FFmpeg is then used to merge these individual streams and the download is streamed back to the user as a blob.

## Features

- High quality video and comment summaries by just submitting a link
- Fast video downloads for all available resolutions
- Video player and top comments displayed next to the summaries
- Support for all long-form Youtube videos up to 1 hour

## Tech Stack

### Frontend

<b>Framework:</b> [React Router (TypeScript)](https://reactrouter.com)\
<b>Styling:</b> [Tailwind CSS](https://tailwindcss.com), [Material UI](https://mui.com/material-ui)

### Backend

<b>Framework:</b> [Flask (Python)](https://flask.palletsprojects.com/en/stable)

### DevOps

<b>Frontend Deployment:</b> [Vercel](https://vercel.com)\
<b>Backend Deployment:</b> [Railway](https://railway.com)\
<b>Rotating Residential Proxy:</b> [ProxyCheap](https://www.proxy-cheap.com)\
<b>DNS Provider:</b> [Porkbun](https://porkbun.com)

### Libraries

<b>Transcript Extraction:</b> [YouTubeTranscriptAPI](https://github.com/jdepoix/youtube-transcript-api)\
<b>Comment Extraction:</b> [YouTubeCommentDownloader](https://github.com/egbertbouman/youtube-comment-downloader)\
<b>Text Summarization:</b> [OpenAI API (ChatGPT 3.5-turbo)](https://github.com/openai/openai-python)\
<b>Video Downloading:</b> [YoutubeDL](https://github.com/yt-dlp/yt-dlp), [FFmpeg](https://www.ffmpeg.org)

## Usage

### 1. Enter the link of your YouTube video and click the summarize button.

![screencapture-ytrehashed-2025-02-27-20_17_03](https://github.com/user-attachments/assets/ee2dddee-3f80-4bdf-af73-fc73a0800a57)


### 2. After about 10-15 seconds, the original video, comments, and summaries will show up.

![screencapture-ytrehashed-2025-02-27-20_14_20](https://github.com/user-attachments/assets/2c3f727b-70b6-4a25-b333-995e274c8643)


### 3. Download the original video at different resolutions.

![screencapture-ytrehashed-2025-02-27-20_19_38](https://github.com/user-attachments/assets/b9a996cc-fa69-4e9a-a49e-bdc27b5cf65d)


## Installation

Follow these steps to set up YT Rehashed locally:

#### 1. Clone the repository

`git clone https://github.com/asshelke/yt-rehashed.git`

#### 2. Navigate to the server directory (backend)

`cd server`

#### 3. Obtain an OpenAI API Key

https://platform.openai.com/api-keys

> IMPORTANT: You need to deposit some money into your OpenAI account to use the API.

#### 4. Add a .env file with the following environment variables

```
OPENAI_API_KEY=<your-api-key>
ENV=development
```

#### 5. Navigate to the client directory (frontend)

`cd ../client`

#### 6. Install all necessary Node and Python dependencies

`npm run init`

#### 7. Run the React and Flask servers concurrently

`npm run stack`

#### 8. View the website locally

http://localhost:3000
