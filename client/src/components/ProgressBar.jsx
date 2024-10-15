import React, { useEffect } from 'react'
import '../App.css'

export default function ProgressBar({ progress, setProgress, endpoint, barTrigger }) {
    

    useEffect(() => {
        const getProgress = async () => {
            fetch(endpoint)
                .then(res => res.json())
                .then(data => {
                    setProgress(data.progress);
                })
                .catch(error => {
                    console.error('Error fetching status:', error);
                });
        }

        const interval = setInterval(getProgress, 200);

        return () => {
            clearInterval(interval);
        }
    });

  return (
    <div>
        {barTrigger && progress < 100.0 && (
        <div>
            <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }}>
                    <p className="progress-text">{progress.toFixed(2)}%</p>
                </div>
            </div>
        </div>
        )}
    </div>
  )
}
