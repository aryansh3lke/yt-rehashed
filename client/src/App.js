import './App.css';
import React, { useState } from 'react';

function App() {
  const [inputLink, setLink] = useState("");
  const [summary, setSummary] = useState("");
  const [videoID, setVideoID] = useState("");
  const [buffering, setBuffering] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    let videoUrl = inputLink;
    setLink("");
    setSummary("");
    setVideoID("");
    setBuffering(true);

    fetch('https://yt-rehashed-server.vercel.app/api/get-summary', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ videoUrl })
    })
      .then(response => response.json()
      .then(data => ({ status: response.status, body: data })))
      .then(({ status, body }) => {
        if (status !== 200) {
          throw new Error(body.message);
        }
        setBuffering(false);
        setSummary(body.summary);
        setVideoID(body.video_id);
      })
      .catch(error => {
        setBuffering(false);
        window.alert(error.message);
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