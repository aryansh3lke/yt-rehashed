from openai import OpenAI
from dotenv import load_dotenv
import sys

load_dotenv()
client = OpenAI()

transcript = sys.argv[1]

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a summarizing assistant for Youtube videos that restates the main points."},
        {"role": "user", "content": f"Summarize the following YouTube transcript in 200 to 250 words: {transcript}"}
    ],
    max_tokens=350,
    temperature=0.7
)

print(completion.choices[0].message.content)