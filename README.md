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

The user also has the option to download the given video at any of the available resolutions, and a separate page exists just for this feature if the user only wants to download videos. With the YT-DLP library, the audio and video streams are downloaded separately since combined streams are not available at high resolutions. FFmpeg is then used to merge these individual streams and the download is streamed back to the user as a blob.

One of the newest features is the creator analyzer which allows users to score their favorite or unkown content creators on different metrics and get an in depth credibility analysis. Currently, the creator analyzer is in its early stages and has not been fully developed but can be utilized in its beta version. On the analyzer's page, the YouTube Data API is used to fetch the statistics and channel avatar for the creator after the creator's handle or id is extracted from the input link. Then, ChatGPT is utilized to analysis the content quality, engagement, and crediblity of the creator.

## Features

- High quality video and comment summaries by just submitting a link
- Fast video downloads for all available resolutions
- Video player, transcript and top comments displayed next to the summaries
- Support for all long-form Youtube videos up to 1 hour
- Creator analyzer to assess channels on content quality, engagement, and credibility

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

### Libraries/APIs

<b>Transcript Extraction:</b> [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)\
<b>Comment Extraction:</b> [YouTube Comment Downloader](https://github.com/egbertbouman/youtube-comment-downloader)\
<b>Text Summarization, Creator Analysis:</b> [OpenAI API (ChatGPT 3.5-turbo)](https://github.com/openai/openai-python)\
<b>Video Downloading:</b> [YoutubeDL](https://github.com/yt-dlp/yt-dlp), [FFmpeg](https://www.ffmpeg.org)
<b>Creator Statistics:</b> [YouTube Data API](https://developers.google.com/youtube/v3)

## Usage

### Video Summarizer

#### 1. Enter the link of your YouTube video and click the summarize button.

![video-summarizer-link](https://github.com/user-attachments/assets/659d189b-43eb-44ee-ac62-63f77811ddb1)

#### 2. After about 10-15 seconds, the original video, comments, and summaries will show up.

![vide-summarizer-result](https://github.com/user-attachments/assets/2c3f727b-70b6-4a25-b333-995e274c8643)

#### 3. Download the original video at different resolutions.

![video-summarizer-resolutions](https://github.com/user-attachments/assets/b9a996cc-fa69-4e9a-a49e-bdc27b5cf65d)

### Video Downloader

#### 1. If you only want to download videos, there is a separate page for this feature.

![video-downloader-page](https://github.com/user-attachments/assets/7de3674b-5e48-484d-8305-2d9358c864ab)

### Creator Analyzer

#### 1. Enter the link of a YouTube channel for the creator you want to analyze.

![creator-analyzer-link](https://github.com/user-attachments/assets/bae3309c-52c1-44fc-ab43-8212c1796385)

#### 2. After about 5 seconds, the creator's statistics, scores on different metrics, background info, and credibility analysis will show up.

![creator-analyzer-results](https://github.com/user-attachments/assets/2858b545-04b4-4dcb-849d-907af85aa09b)


## Installation

Follow these steps to set up YT Rehashed locally:

#### 1. Clone the repository

`git clone https://github.com/aryansh3lke/yt-rehashed.git`

#### 2. Navigate to the server directory (backend)

`cd server`

#### 3. Obtain an OpenAI API Key

https://platform.openai.com/api-keys

> IMPORTANT: You need to deposit some money into your OpenAI account to use the API.

#### 4. Obtain a YouTube Data API Key

https://developers.google.com/youtube/v3/getting-started

#### 5. Add a .env file with the following environment variables

```
# Development/Production
ENV=development

# Transcript and Comment Summarization, Creator Analysis
OPENAI_API_KEY=<your-api-key>

# Youtube Data API to extract creator statistics and other info
YOUTUBE_API_KEY=<your-api-key>

# YouTube Transcript API (Required in production to avoid IP bans)
ROTATING_RESIDENTIAL_PROXY=<your-proxy>
```

> IMPORTANT: Make sure to set `ENV=production` and obtain rotating residential proxy when deploying the Flask server in production.

#### 6. Navigate to the client directory (frontend)

`cd ../client`

#### 7. Install all necessary Node and Python dependencies

`npm run init`

#### 8. Run the React and Flask servers concurrently

`npm run stack`

#### 9. View the website locally

http://localhost:3000
