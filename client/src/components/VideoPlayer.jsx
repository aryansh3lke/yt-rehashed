import React from 'react';
import VideoEmbed from './VideoEmbed';

export default function VideoPlayer({ videoId, displayResolutions, animationDelay }) {
  return (
    <section className="main-box-outer slide-up" style={{ animationDelay: `${animationDelay}s`}}>
        <h2 className="section-title" id="download-title">Original Video
        <button className="download-button" onClick={displayResolutions}>
            <img className="download-icon" src="download.svg" alt="Download"></img>
        </button>
        </h2>
        <div className="main-box-inner video-box">
          <VideoEmbed videoId={videoId} />
        </div>
    </section>
  )
}
