import React, { useState, useEffect } from 'react'
import '../App.css'

export default function ProgressBar({ endpoint, barTrigger }) {
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        const getProgress = async () => {
            fetch(endpoint)
                .then(res => res.json())
                .then(data => {
                    const progress = data.progress;
                    setProgress(data.progress);
                    
                    if (progress === 100.0) {
                        clearInterval(interval);
                    }
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
        {barTrigger && (
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
