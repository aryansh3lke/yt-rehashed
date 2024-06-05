const express = require('express');
const transcriptAPI = require('youtube-transcript-api');

const app = express();
const PORT = 8080;

// Middleware to parse JSON bodies
app.use(express.json());

function extractVideoId(url) {
  const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S*\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}

// API endpoint to handle transcript requests
app.post('/api/get-transcript', async (req, res) => {
  const videoID = extractVideoId(req.body.videoUrl);

  if (videoID === null) {
    res.status(400).json({ message: "Invalid URL" });
  }

  transcriptAPI.getTranscript(videoID)
    .then((transcriptList) => {
      let transcriptStr = "";
      transcriptList.forEach((caption) => {
        transcriptStr += ' ' + caption.text;
      });
      res.status(200).json({ transcript: transcriptStr });
    })
    .catch(error => {
      res.status(500).json({ message : error.message } );
      console.log();
    });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
