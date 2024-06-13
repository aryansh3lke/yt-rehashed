import './App.css';
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [inputLink, setLink] = useState("");
  const [summary, setSummary] = useState("");
  const [videoID, setVideoID] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    let url = inputLink;
    setLink("");

    axios.post('/api/get-summary', { videoUrl: url })
      .then(response => {
        setSummary(response.data.summary);
        setVideoID(response.data.videoID);
      })
      .catch(error => {
        console.error(error);
        window.alert(error.response.data.message);
    });
    
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>YT Rehashed</h1>
      </header>
      <p>Enter the link to summarize your YouTube video:</p><br></br>
      <div>
        <input 
          type="text"
          value={inputLink}
          placeholder="https://www.youtube.com/watch?v="
          onChange={(e) => setLink(e.target.value)}>
        </input>
        <button onClick={handleSubmit}>Summarize</button>
      </div>
      
      {summary && (
        <div>
          <h2>Video Summary:</h2>
          <p>{summary}</p>
          <iframe
            title="YouTube Video Player" 
            width="640" 
            height="380" 
            src={"https://www.youtube.com/embed/" + videoID}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen">
          </iframe>
        </div>
      )}
    </div>
  );
}

export default App;