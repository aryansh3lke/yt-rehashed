import React from 'react';
import ModalHeader from './ModalHeader';
import CloseButton from './CloseButton';
import Loader from './Loader';
import ResolutionButtons from './ResolutionButtons';
import ProgressBar from './ProgressBar';
import DownloadVideoButton from './DownloadVideoButton';

export default function DownloadModal({ downloadModal, setDownloadModal, 
    downloadLoader, downloadResolutions, selectedResolution, 
    setSelectedResolution, progressEndpoint, isDownloading, downloadVideo, 
    progress, setProgress }) {

  return (
    <div>
      {downloadModal && (
          <div>
            <div className="modal active" id="modal">
              <CloseButton onClose={ () => {setDownloadModal(false)} }/>
              
              <div>
              {downloadLoader ? (
                  <Loader
                    loaderTrigger={downloadLoader}
                    loaderType={"download-loader"}
                  />
                ): (
                  <div>
                    {downloadResolutions && downloadResolutions.length > 0 ? (
                      <div id="download-result">
                        <ModalHeader title={"Select a resolution to download:"}/>

                        <ResolutionButtons
                          downloadResolutions={downloadResolutions}
                          selectedResolution={selectedResolution}
                          setSelectedResolution={setSelectedResolution}
                        />

                        {isDownloading && (
                          <ProgressBar
                          progress={progress}
                          setProgress={setProgress}
                          endpoint={progressEndpoint}
                          barTrigger={isDownloading}
                          />
                        )}

                        <DownloadVideoButton
                          downloadVideo={downloadVideo}
                        />
                      </div>
                    ) : (
                      <h3>No downloads available.</h3>
                    )
                    }
                  </div>
                )}
            </div>
          </div>
          <div id="overlay"></div>
        </div>
        )}
    </div>
  )
}
