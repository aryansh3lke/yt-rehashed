import './App.css';
import React, { useState } from 'react';

function App() {
  const [videoLink, setVideoLink] = useState("");
  const [savedLink, setSavedLink] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setSavedLink(videoLink);
    setVideoLink("");
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>YT Rehashed</h1>
      </header>
      <p>Enter the link to summarize the YT video:</p><br></br>
      <input 
        type="text"
        value={videoLink}
        placeholder="https://www.youtube.com/watch?v="
        onChange={(e) => setVideoLink(e.target.value)}>
      </input>
      <button onClick={handleSubmit}>Summarize</button>
      {savedLink && (
        <div>
          <h2>Saved Link:</h2>
          <p>{savedLink}</p>
        </div>
      )}
    </div>
  );
}

export default App;
