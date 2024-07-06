import './App.css';
import React, { useState } from 'react';

const proxyUrl = process.env.REACT_APP_PROXY_URL || 'http://localhost:8000';

function App() {
  const [inputLink, setLink] = useState("");
  const [videoId, setVideoId] = useState("");
  const [videoTitle, setVideoTitle] = useState("");
  const [comments, setComments] = useState([]);
  const [transcriptSummary, setTranscriptSummary] = useState("");
  const [commentSummary, setCommentSummary] = useState("");
  const [loader, setLoader] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const videoUrl = inputLink;

    setLink("");
    setVideoId("");
    setVideoTitle("");
    setComments("")
    setTranscriptSummary("");
    setCommentSummary("");
    setLoader(true);

    fetch(proxyUrl + '/api/get-summary', {
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
        setLoader(false);
        setVideoId(body.video_id);
        setVideoTitle(body.video_title);
        setComments(body.comments);
        setTranscriptSummary(body.transcript_summary);
        setCommentSummary(body.comment_summary);
      })
      .catch(error => {
        setLoader(false);
        window.alert(error.message);
      });
  };

  const handleDownload = async (e) => {
    e.preventDefault();

    fetch(proxyUrl + '/api/download-video', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ videoId })
    })
      .then(response => {
          if (!response.ok) {
              throw new Error('Failed to download video');
          }
          return response.blob();
      })
      .then(blob => {
          const downloadUrl = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = downloadUrl;
          link.setAttribute('download', `${videoTitle}.mp4`); // Default filename for unknown or misconfigured backend
          document.body.appendChild(link);
          link.click();
          link.remove();
      })
      .catch(error => {
          console.error('Error downloading video:', error);
          window.alert('Failed to download video');
      });
  
  }

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
        {loader && (
          <div className="loader"></div>
        )}
        {videoId && (
          <p>Video ID = {videoId}</p>
        )}
        {transcriptSummary && (
          <div className="result">
            <section className="main-box-outer">
              <h2 className="section-title" id="download-title">Original Video
                <button className="download-button" onClick={handleDownload}>
                  <img className="download-icon" src="download.svg" alt="Download"></img>
                </button>
              </h2>
              <div className="main-box-inner video-box">
                <iframe
                  className="video-player"
                  title="YouTube Video Player" 
                  src={"https://www.youtube.com/embed/" + videoId}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen">
                </iframe>
              </div>
            </section>

            <section className="main-box-outer">
              <h2 className="section-title">Video Summary</h2>
              <div className="main-box-inner text-box">
                <p className="summary">{transcriptSummary}</p>
              </div>
            </section>
          </div>
        )}
        {commentSummary && (
          <div className="result">
            <section className="main-box-outer">
              <h2 className="section-title">Popular Comments</h2>
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
            </section>

            <section className="main-box-outer">
              <h2 className="section-title">Comment Summary</h2>
              <div className="main-box-inner text-box">
                <p className="summary">{commentSummary}</p>
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;