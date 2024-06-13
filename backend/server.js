const express = require('express');
const util = require('util');
const transcriptAPI = require('youtube-transcript-api');
const { exec } = require('child_process');

const app = express();
const PORT = 8080;

const execPromise = util.promisify(exec);
const summarizerScriptPath = '../ml/summarizer.py';

// Middleware to parse JSON bodies
app.use(express.json());

function extractVideoId(url) {
  const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S*\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}

async function executePythonScript(scriptPath, inputString) {
  const command = `python ${scriptPath} "${inputString}"`;

  return execPromise(command)
    .then(({ stdout, stderr }) => {
      if (stderr) {
          throw new Error(`Command stderr: ${stderr}`);
      }
      return stdout.trim();
    });
}

app.post('/api/get-summary', async (req, res) => {
  const videoID = extractVideoId(req.body.videoUrl);

  // invalid youtube url, video id could not be extracted (client fault)
  if (videoID === null) {
    console.error("Error: URL is not a valid YouTube link");
    return res.status(400).json({ message: "Please enter a valid YouTube URL!" });
  }

  transcriptAPI.getTranscript(videoID)
    .then(captions => {
      const transcript = captions.map(caption => caption.text).join(' ');

      executePythonScript(summarizerScriptPath, transcript)
      .then(summary => {
        console.log("\x1b[36m%s\x1b[0m", "Video successfully summarized!");
        return res.status(200).send({ summary: summary , videoID: videoID });
      })
      .catch(error => {
        console.error("Error: Video could not be summarized by ChatGPT")
        return res.status(500).send({ message: "Failed to make a summary of the transcript." });
      });
    })
    .catch(error => {
      console.error("Error: URL does not contain a valid YouTube video ID");
      return res.status(400).send({ message: "YouTube video does not exist for the given URL!" });
    });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});