# YT Rehashed

An AI tool to quickly generate quality summaries of YouTube videos and download videos at high resolutions. Summarize and download your videos here: [ytrehashed.com](ytrehashed.com)

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Usage](#usage)
4. [Installation](#installation)

## Introduction

This full-stack React-Flask web application is designed to help users quickly grasp the content of YouTube videos through summaries generated with the help of OpenAI's API and ChatGPT-3.5-turbo. This tool is especially useful for students, researchers, and anyone who wants to save time while consuming long-form video content.

## Features

- Summarizes videos with only a link
- Displays original video next to the video summary
- Video downloader to download original video at the available resolutions
- Supports all lengths of Youtube videos up to 1 hour
- Generates a summary of the top 100 popular comments
- Displays the original comments section next to the comment summary

## Usage

### 1. Enter the link of your YouTube video

![Before](images/usage-before.png)

### 2. After about 5-10 seconds, the original video, comments, and summaries will show up.

![After](images/usage-after.png)

### 3. Download the original video at different resolutions.

![Video Downloader Feature](images/download-feature-2.png)

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
