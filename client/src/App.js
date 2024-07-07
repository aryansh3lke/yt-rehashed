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
  
  const [selectedResolution, setSelectedResolution] = useState("");
  const [summaryLoader, setSummaryLoader] = useState(false);

  const [downloadModal, setDownloadModal] = useState(false);
  const [downloadOptions, setDownloadOptions] = useState(null);
  const [downloadLoader, setDownloadLoader] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const videoUrl = inputLink;

    setLink("");
    setVideoId("");
    setVideoTitle("");
    setComments("")
    setTranscriptSummary("");
    setCommentSummary("");
    setDownloadOptions("");
    setSummaryLoader(true);

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
        setSummaryLoader(false);
        setVideoId(body.video_id);
        setVideoTitle(body.video_title);
        setComments(body.comments);
        setTranscriptSummary(body.transcript_summary);
        setCommentSummary(body.comment_summary);
      })
      .catch(error => {
        setSummaryLoader(false);
        window.alert(error.message);
      });
  };

  const displayDownloads = async (e) => {
    e.preventDefault();

    if (!downloadOptions) {
      setDownloadModal(true);
      setDownloadLoader(true);
      setDownloadOptions([]);
  
      fetch(proxyUrl + '/api/get-downloads', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ videoId })
      })
        .then(response => response.json()
        .then(data => ({ status: response.status, body: data })))
        .then(({ status, body }) => {
          if (status !== 200) {
            throw new Error(body.message);
          }
          setDownloadLoader(false);
          setDownloadOptions(body.resolutions);
        })
        .catch(error => {
          setDownloadLoader(false);
          window.alert(error.message);
        });
    } else {
      setDownloadModal(true);
    }
    
  }

  const downloadVideo = async (e) => {
    e.preventDefault();
    if (selectedResolution === "") {
      window.alert("Please select a resolution!");
    } else {
      fetch(proxyUrl + '/api/download-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ videoId, selectedResolution })
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
            link.setAttribute('download', `${videoTitle} [${selectedResolution}].mp4`); // Default filename for unknown or misconfigured backend
            document.body.appendChild(link);
            link.click();
            link.remove();
        })
        .catch(error => {
            console.error('Error downloading video:', error);
            window.alert('Failed to download video');
        });
    }
  }

  const handleResolutionChange = (e) => {
    setSelectedResolution(e.target.value);
  };

  const closeDownloadPanel = (e) => {
    setDownloadModal(false);
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
        {summaryLoader && (
          <div className="loader"></div>
        )}
        {transcriptSummary && (
          <div className="result">
            <section className="main-box-outer">
              <h2 className="section-title" id="download-title">Original Video
                <button className="download-button" onClick={displayDownloads}>
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
        {downloadModal && (
          <div>
            <div className="modal active" id="modal">
              <button className="close-button" onClick={closeDownloadPanel}>&times;</button>
              <div>
                <div className="modal-header">
                  <h4 className="modal-title">Select a resolution to download:</h4>
              </div>
              {downloadLoader ? (
                  <div id="download-loader" className="loader"></div>
                ): (
                  <div id="download-result">
                    <ul className="resolution-buttons">
                      {downloadOptions.map((resolution) => (
                        <li>
                          <input 
                            type="radio"
                            id={resolution}
                            value={resolution}
                            checked={resolution === selectedResolution}
                            onChange={handleResolutionChange}
                            name="options"/>
                            <label for={resolution}>{resolution}</label>
                        </li>
                      ))}
                    </ul>
                    <button className="submit-button" onClick={downloadVideo}>
                      <p className="download-text">Download Video</p>
                      <img className="download-icon-large inverted-icon" src="download.svg" alt="Download"></img>
                      </button>
                  </div>
                )}
            </div>
          </div>
          <div id="overlay"></div>
        </div>
        )}
      </div>
    </div>
  );
}

export default App;