import React from 'react';

export default function VideoPlayer({ videoId, displayResolutions, animationDelay }) {
  return (
    <section className="main-box-outer slide-up" style={{ animationDelay: `${animationDelay}s`}}>
        <h2 className="section-title" id="download-title">Original Video
        <button className="download-button" onClick={displayResolutions}>
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
  )
}
