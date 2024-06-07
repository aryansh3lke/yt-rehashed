const express = require('express');
const util = require('util');
const transcriptAPI = require('youtube-transcript-api');
const { exec } = require('child_process');

const app = express();
const PORT = 8080;

const execPromise = util.promisify(exec);
const punctuateScriptPath = '../ml/punctuate.py';

// Middleware to parse JSON bodies
app.use(express.json());

function extractVideoId(url) {
  const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S*\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}

async function punctuateText(inputString) {
  const command = `python ${punctuateScriptPath} "${inputString}"`;

  return execPromise(command)
    .then(({ stdout, stderr }) => {
      if (stderr) {
          throw new Error(`Command stderr: ${stderr}`);
      }
      return stdout.trim();
    });
}

app.post('/api/get-summary', async (req, res) => {
  console.log(req.body);
  const videoID = extractVideoId(req.body.videoUrl);
  console.log(videoID);

  // invalid youtube url, video id could not be extracted (client fault)
  if (videoID === null) {
    console.log("no valid id");
    res.status(400).json({ message: "Invalid URL" });
  }

  const captions = await transcriptAPI.getTranscript(videoID)
  if (!captions) {
    return res.status(400).send({ message: "Invalid video ID in URL" });
  }

  const transcript = captions.map(caption => caption.text).join(' ');
  const punctutatedText = await punctuateText(transcript);
  if (!punctutatedText) {
    return res.status(500).send({ message: "Transcript could not be punctuated" });
  }

  return res.status(200).send({ punctuatedTranscript: punctutatedText });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
