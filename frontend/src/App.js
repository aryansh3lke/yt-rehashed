import './App.css';
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [videoLink, setVideoLink] = useState("");
  const [videoTranscript, setTranscript] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    let url = videoLink;
    setVideoLink("");

    axios.post('/api/get-transcript', { videoUrl: url })
      .then(response => {
        setTranscript(response.data.transcript);
      })
      .catch(error => {
        console.error(error);
        setTranscript("Invalid URL!");
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
      
      {videoTranscript && (
        <div>
          <h2>Video Transcript:</h2>
          <p>{videoTranscript}</p>
        </div>
      )}
    </div>
  );
}

export default App;
