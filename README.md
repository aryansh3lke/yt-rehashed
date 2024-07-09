# YT Rehashed

A tool to quickly generate quality summaries of YouTube videos. Summarize your videos here: [ytrehashed.com](ytrehashed.com)

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
4. [Usage](#usage)
4. [Installation](#installation)
5. [Contact](#contact)

## Introduction

This full-stack React-Flask web application is designed to help users quickly grasp the content of YouTube videos through summaries generated with the help of OpenAI's API and ChatGPT-3.5-turbo. This tool is especially useful for students, researchers, and anyone who wants to save time while consuming long-form video content.

## Features

- Summarizes videos with only a link (no transcript needed)
- Displays original video next to the video summary
- Video downloader to download original video at different resolutions
- Supports all lengths of Youtube videos up to 1 hour
- Generates a summary of the top 100 popular comments
- Displays the original comments section next to the comment summary

## Usage

Enter the link of your YouTube video and wait about 5-10 seconds for the video, comments, and summaries to show up.

![Before](images/usage-before.png)

![After](images/usage-after.png)

## Installation

Follow these steps to set up YT Rehashed locally:

#### 1. Clone the repository

`git clone https://github.com/asshelke/yt-rehashed.git`

#### 2. Navigate to the client directory (frontend)

`cd client`

#### 3. Install all necessary React dependencies

`npm install`

#### 4. Start the React frontend server

`npm start`

#### 5. Navigate to the server directory (backend)

`cd server`

#### 6. Install all necessary Python dependencies

`pip install -r requirements.txt`

#### 7. Obtain an OpenAI API Key

https://platform.openai.com/api-keys

> IMPORTANT: You will need to deposit some money into your OpenAI account to use the API.

#### 8. Add an environment variable for the key in a .env file

`OPENAI_API_KEY=[add your key here]`

> NOTE: Make sure to place the `.env` file in the `/server/` directory.

#### 9. Start the Flask backend server

`python app.py`

#### 10. View the website locally

http://localhost:3000

## Contact

Aryan Shelke

Email: aryan.shelke.2003.@gmail.com

LinkedIn: [linkedin.com/in/aryanshelke](linkedin.com/in/aryanshelke)
