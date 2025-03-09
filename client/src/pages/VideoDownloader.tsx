import { useEffect, useState } from "react";

import ErrorAlert from "../components/ErrorAlert";
import LinkForm from "../components/LinkForm";
import Loader from "../components/Loader";
import VideoPlayer from "../components/VideoPlayer";
import DownloadBox from "../components/DownloadBox";

import { Resolution } from "../types/interfaces";
import { generateValidFilename } from "../utils";
import { PROXY_URL } from "../proxy";

export default function VideoDownloader() {
  const [inputLink, setInputLink] = useState<string>("");
  const [videoId, setVideoId] = useState<string>("");
  const [videoTitle, setVideoTitle] = useState<string>("");

  const [downloadLoader, setDownloadLoader] = useState<boolean>(false);
  const [downloadResolutions, setDownloadResolutions] = useState<Resolution[]>(
    [],
  );
  const [selectedResolution, setSelectedResolution] = useState<Resolution>("");
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [downloadError, setDownloadError] = useState<string>("");
  const [alert, setAlert] = useState<string>("");

  useEffect(() => {
    if (videoId !== "") {
      fetchResolutions();
    }
    // eslint-disable-next-line
  }, [videoId]);

  /**
   * Generate a list of available resolutions for a YouTube video based on the
   * provided URL.
   *
   * This function is triggered by clicking the submit button for the link form.
   * It fetches the resolutions from the server based on the video streams that
   * are available through YouTube.
   */
  const displayResolutions = async (e: React.FormEvent) => {
    e.preventDefault();
    const videoUrl: string = inputLink;

    setInputLink("");
    setVideoId("");
    setVideoTitle("");
    setDownloadResolutions([]);
    setSelectedResolution("");
    setDownloadError("");
    setAlert("");

    setDownloadLoader(true);

    fetch(PROXY_URL + `/api/get-video-info?video_url=${videoUrl}`)
      .then((response) =>
        response
          .json()
          .then((data) => ({ status: response.status, body: data })),
      )
      .then(({ status, body }) => {
        if (status !== 200) {
          throw new Error(body.error);
        }

        setVideoId(body.video_id);
        setVideoTitle(body.video_title);
      })
      .catch((error) => {
        setDownloadLoader(false);
        setAlert(error.message);
      });
  };

  /**
   * Fetch the available resolutions for a YouTube video from the server.
   *
   * This function is triggered by opening up the download modal for the first
   * time for the current video. It fetches the resolutions from the server
   * based on the video streams that are available through YouTube.
   */
  const fetchResolutions = async () => {
    fetch(PROXY_URL + `/api/get-resolutions?video_id=${videoId}`)
      .then((response) =>
        response
          .json()
          .then((data) => ({ status: response.status, body: data })),
      )
      .then(({ status, body }) => {
        if (status !== 200) {
          throw new Error(body.error);
        }
        setDownloadLoader(false);
        setDownloadResolutions(body.resolutions);
      })
      .catch((error) => {
        setDownloadLoader(false);
        setAlert(error.message);
      });
  };

  /**
   * Handle the download of a YouTube video based on the selected resolution.
   *
   * This function is triggered by clicking the download button on the download
   * modal. It checks if a resolution is selected and fetches the download URL
   * from the server. If the URL is successfully retrieved, it creates a link
   * element to initiate the download of the video as a file attachment.
   */
  const downloadVideo = async (e: React.MouseEvent) => {
    e.preventDefault();

    if (selectedResolution === "") {
      // throw warning if no resolution is selected
      setDownloadError("Please select a resolution!");
    } else {
      try {
        setIsDownloading(true);
        const response = await fetch(
          PROXY_URL +
            `/api/get-download?video_id=${videoId}&video_resolution=${selectedResolution}`,
        );

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${generateValidFilename(videoTitle)} [${selectedResolution}].mp4`; // You can customize the filename as needed
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        setIsDownloading(false);
      } catch (error) {
        setIsDownloading(false);
        setDownloadError("An error occurred while downloading the video.");
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-center gap-5">
      {alert && <ErrorAlert message={alert} setMessage={setAlert} />}

      <LinkForm
        title="Video Downloader"
        prompt={"Enter your YouTube video link to download your video"}
        placeholder={"https://www.youtube.com/watch?v="}
        inputLink={inputLink}
        setInputLink={setInputLink}
        onSubmit={displayResolutions}
        submitText="Download"
      />

      <Loader loaderTrigger={downloadLoader} loaderType={"summary-loader"} />

      {downloadResolutions.length > 0 && (
        <div className="mb-12 mt-8 flex w-full flex-col items-center justify-center gap-4 lg:flex-row lg:gap-16">
          <div className="w-full lg:w-1/2">
            <VideoPlayer
              videoId={videoId}
              captions={[]}
              displayResolutions={displayResolutions}
              animationDelay={0}
              showHeader={false}
            />
          </div>
          <div className="w-full lg:w-1/2">
            <DownloadBox
              downloadResolutions={downloadResolutions}
              selectedResolution={selectedResolution}
              setSelectedResolution={setSelectedResolution}
              isDownloading={isDownloading}
              downloadError={downloadError}
              setDownloadError={setDownloadError}
              downloadVideo={downloadVideo}
              animationDelay={0.5}
            />
          </div>
        </div>
      )}
    </div>
  );
}
