import React, { useState, useEffect } from 'react'
import '../App.css'

export default function DownloadBar({ endpoint }) {
    const [downloadProgress, setDownloadProgress] = useState(0);

    useEffect(() => {
        const interval = setInterval(getDownloadProgress, 50);

        return () => {
            clearInterval(interval);
        }
    });

    async function getDownloadProgress() {
        fetch(endpoint)
            .then(res => res.json())
            .then(data => {
                setDownloadProgress(data.progress);
            })
            .catch(error => {
                console.error('Error fetching status:', error);
            });
    }

  return (
    <div className="progress-bar">
        <div className="download-progress-bar">
            <div className="download-progress" style={{ width: `${downloadProgress}%` }}>
                <p className="download-progress-text">{downloadProgress.toFixed(2)}%</p>
            </div>
        </div>
    </div>
  )
}
