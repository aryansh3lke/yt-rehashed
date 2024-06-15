FROM python:3.11.7

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OPENAI_API_KEY=sk-proj-5Ry9FbEBcv4mmp6LYoczT3BlbkFJ3mAsn5Gi2a3nbub2Qskl

EXPOSE 8000

CMD ["python", "app.py"]