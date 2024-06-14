import './App.css';
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [inputLink, setLink] = useState("");
  const [summary, setSummary] = useState("");
  const [videoID, setVideoID] = useState("");
  const [buffering, setBuffering] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    let url = inputLink;
    setLink("");
    setSummary("");
    setVideoID("");
    setBuffering(true);

    axios.post('/api/get-summary', { videoUrl: url })
      .then(response => {
        setBuffering(false);
        setSummary(response.data.summary);
        setVideoID(response.data.videoID);
      })
      .catch(error => {
        setBuffering(false);
        window.alert(error.response.data.message);
    });
    
  };

  return (
    <div className="App">
      <header className="App-main">
        <div id="logo-title">
          <img className="App-logo" src={process.env.PUBLIC_URL + '/logo512.png'} alt="YT Rehashed Logo"></img>
          <h1>YT Rehashed</h1>
        </div>
        <h3>Enter the link to summarize your YouTube video:</h3>
        <div id="link-form">
          <input
            type="text"
            value={inputLink}
            placeholder="https://www.youtube.com/watch?v="
            onChange={(e) => setLink(e.target.value)}>
          </input>
          <button onClick={handleSubmit}>Summarize</button>
        </div>
        {buffering && (
          <div className="loader"></div>
        )}
        {summary && (
          <div className="result">
            <div id="video-summary">
              <h2>Video Summary</h2>
              <div className="video-container">
              <p id="summary">{summary}</p>
              </div>
            </div>

            <div id="original-video">
              <h2>Original Video</h2>
              <div className="video-container">
                <iframe
                  title="YouTube Video Player" 
                  src={"https://www.youtube.com/embed/" + videoID}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen">
                </iframe>
              </div>
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;