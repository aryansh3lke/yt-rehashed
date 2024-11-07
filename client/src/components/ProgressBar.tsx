import { useEffect } from 'react';

export default function ProgressBar({
    progress,
    setProgress,
    endpoint,
    barTrigger
}: {
    progress: number;
    setProgress: React.Dispatch<React.SetStateAction<number>>
    endpoint: string;
    barTrigger: boolean;
}) {
    // create hook for mounting component
    useEffect(() => {
        setProgress(0.0);
        const getProgress = async () => {
            if (progress === 100.0) {
                clearInterval(interval);
            }

            fetch(endpoint)
                .then(res => res.json())
                .then(data => {
                    setProgress(data.progress);
                })
                .catch(error => {
                    console.error('Error fetching status:', error);
                });
        }

        const interval = setInterval(getProgress, 500);

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
