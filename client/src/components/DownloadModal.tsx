import Loader from "./Loader";
import ResolutionButtons from "./ResolutionButtons";
import ProgressBar from "./ProgressBar";
import { Resolution } from "../types/interfaces";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import useTheme from "@mui/material/styles/useTheme";
import ErrorAlert from "./ErrorAlert";

export default function DownloadModal({
  downloadModal,
  setDownloadModal,
  downloadLoader,
  downloadResolutions,
  selectedResolution,
  setSelectedResolution,
  downloadError,
  setDownloadError,
  isDownloading,
  downloadVideo,
  progressEndpoint,
}: {
  downloadModal: boolean;
  setDownloadModal: React.Dispatch<React.SetStateAction<boolean>>;
  downloadLoader: boolean;
  downloadResolutions: Resolution[];
  selectedResolution: Resolution;
  setSelectedResolution: React.Dispatch<React.SetStateAction<Resolution>>;
  downloadError: string;
  setDownloadError: React.Dispatch<React.SetStateAction<string>>;
  isDownloading: boolean;
  downloadVideo: (e: React.MouseEvent) => void;
  progressEndpoint: string;
}) {
  const theme = useTheme();

  return (
    <div>
      {downloadModal && (
        <div>
          <Box
            className={`modal active ${theme.palette.mode === "light" ? "bg-white text-black" : "bg-[#121212] text-white"}}`}
            id="modal"
          >
            <IconButton
              onClick={() => setDownloadModal(false)}
              sx={{
                position: "absolute",
                top: 8,
                right: 8,
              }}
            >
              <CloseIcon />
            </IconButton>

            <Box className="my-5 flex w-full flex-col items-center justify-center gap-6">
              {downloadLoader ? (
                <Loader
                  loaderTrigger={downloadLoader}
                  loaderType={"download-loader"}
                />
              ) : (
                <>
                  {downloadResolutions.length > 0 ? (
                    <div className="flex flex-col items-center justify-center gap-4">
                      {downloadError && (
                        <ErrorAlert
                          message={downloadError}
                          setMessage={setDownloadError}
                        />
                      )}

                      <Typography variant="h4" textAlign="center">
                        Select a resolution to download
                      </Typography>

                      <ResolutionButtons
                        downloadResolutions={downloadResolutions}
                        selectedResolution={selectedResolution}
                        setSelectedResolution={setSelectedResolution}
                      />

                      {isDownloading && (
                        <ProgressBar
                          endpoint={progressEndpoint}
                          barTrigger={isDownloading}
                        />
                      )}

                      <Button
                        variant="contained"
                        onClick={downloadVideo}
                        sx={{ backgroundColor: "red", textTransform: "none" }}
                      >
                        <Typography className="download-text">
                          Download Video
                        </Typography>
                      </Button>
                    </div>
                  ) : (
                    <Typography variant="h5">
                      No downloads available.
                    </Typography>
                  )}
                </>
              )}
            </Box>
          </Box>
          <div id="overlay"></div>
        </div>
      )}
    </div>
  );
}
