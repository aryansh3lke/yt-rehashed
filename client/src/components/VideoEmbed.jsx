import React from 'react'

export default function VideoEmbed({ videoId }) {
    return (
        <iframe
            className='video-player'
            src={`https://www.youtube.com/embed/${videoId}`}
            loading='lazy'
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
            title="YouTube Video Player">
        </iframe>
    );
}