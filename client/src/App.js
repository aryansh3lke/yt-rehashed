import './App.css';
import React, { useState } from 'react';

function App() {
  const [inputLink, setLink] = useState("");
  const [videoId, setVideoId] = useState("");
  const [comments, setComments] = useState([]);
  const [transcriptSummary, setTranscriptSummary] = useState("");
  const [commentSummary, setCommentSummary] = useState("");
  const [buffering, setBuffering] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    let videoUrl = inputLink;
    setLink("");
    setTranscriptSummary("");
    setCommentSummary("");
    setVideoId("");
    setBuffering(true);

    fetch('http://localhost:8000/api/get-summary', {
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
        setVideoId(body.video_id);
        setComments(body.comments)
        setTranscriptSummary(body.transcript_summary);
        setCommentSummary(body.comment_summary);
      })
      .catch(error => {
        setBuffering(false);
        window.alert(error.message);
      });
  };

  return (
    <div className="app">
      <div className="app-main">
        <div className="logo-title">
          <img className="app-logo" src={process.env.PUBLIC_URL + '/logo512.png'} alt="YT Rehashed Logo"></img>
          <h1>YT Rehashed</h1>
        </div>
        <h3>Enter the link to summarize your YouTube video:</h3>
        <div className="link-form">
          <input
            className="input-box"
            type="text"
            value={inputLink}
            placeholder="https://www.youtube.com/watch?v="
            onChange={(e) => setLink(e.target.value)}>
          </input>
          <button className="submit-button" onClick={handleSubmit}>Summarize</button>
        </div>
        {buffering && (
          <div className="loader"></div>
        )}
        {transcriptSummary && (
          <div className="result">
            <div className="main-box-outer">
              <h2>Original Video</h2>
              <div className="main-box-inner video-box">
                <iframe
                  className="video-player"
                  title="YouTube Video Player" 
                  src={"https://www.youtube.com/embed/" + videoId}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen">
                </iframe>
              </div>
            </div>

            <div className="main-box-outer">
              <h2>Video Summary</h2>
              <div className="main-box-inner text-box">
                <p className="summary">{transcriptSummary}</p>
              </div>
            </div>
          </div>
        )}
        {commentSummary && (
          <div className="result">
            <div className="main-box-outer">
              <h2>Popular Comments</h2>
              <div className="main-box-inner comment-box">
                <ul className="comment-list">
                  {comments.map((comment) => (
                    <li key={comment.cid} className="comment-item">
                      <img className="comment-profile" src={comment.photo} alt={comment.author}></img>
                      <div className="comment-main">
                        <p className="comment-header">
                          <strong>{comment.author}</strong>
                          <small>{comment.time}</small></p>
                        <p className="comment-text">{comment.text.trim()}</p>
                        <div className="comment-likes">
                          <img src={process.env.PUBLIC_URL + '/thumbs-up.svg'} alt={"Like Button"}></img>
                          <small className="comment-like-count">{comment.votes}</small>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="main-box-outer">
              <h2>Comment Summary</h2>
              <div className="main-box-inner text-box">
                <p className="summary">{commentSummary}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;