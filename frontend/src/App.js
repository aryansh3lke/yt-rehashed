import './App.css';
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [videoLink, setVideoLink] = useState("");
  const [videoSummary, setSummary] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    let url = videoLink;
    setVideoLink("");

    axios.post('/api/get-summary', { videoUrl: url })
      .then(response => {
        setSummary(response.data.punctuatedTranscript);
      })
      .catch(error => {
        console.error(error);
        setSummary("Invalid URL!");
    });
    
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>YT Rehashed</h1>
      </header>
      <p>Enter the link to summarize the YT video:</p><br></br>
      <div>
        <input 
          type="text"
          value={videoLink}
          placeholder="https://www.youtube.com/watch?v="
          onChange={(e) => setVideoLink(e.target.value)}>
        </input>
        <button onClick={handleSubmit}>Summarize</button>
      </div>
      
      {videoSummary && (
        <div>
          <h2>Video Transcript (Punctuated):</h2>
          <p>{videoSummary}</p>
        </div>
      )}
    </div>
  );
}

export default App;
