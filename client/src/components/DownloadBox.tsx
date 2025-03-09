import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import ResolutionButtons from "./ResolutionButtons";
import ProgressBar from "./ProgressBar";
import { PROXY_URL } from "../proxy";
import { Resolution } from "../types/interfaces";
import ErrorAlert from "./ErrorAlert";

export default function DownloadBox({
  downloadResolutions,
  selectedResolution,
  setSelectedResolution,
  isDownloading,
  downloadError,
  setDownloadError,
  downloadVideo,
  animationDelay,
}: {
  downloadResolutions: Resolution[];
  selectedResolution: Resolution;
  setSelectedResolution: React.Dispatch<React.SetStateAction<Resolution>>;
  isDownloading: boolean;
  downloadError: string;
  setDownloadError: React.Dispatch<React.SetStateAction<string>>;
  downloadVideo: (e: React.MouseEvent) => void;
  animationDelay: number;
}) {
  return (
    <section
      className={`slide-up flex flex-col gap-8`}
      style={{ animationDelay: `${animationDelay}s` }}
    >
      <Card
        className="card-height flex w-full flex-col items-center justify-center"
        sx={{ overflowY: "auto", borderRadius: 2 }}
      >
        <CardContent className="flex flex-col items-center justify-center gap-4">
          {downloadError && (
            <ErrorAlert message={downloadError} setMessage={setDownloadError} />
          )}

          <Typography variant="h5" textAlign="center" sx={{ fontWeight: 600 }}>
            Select a resolution to download
          </Typography>

          <div className="w-full">
            <ResolutionButtons
              downloadResolutions={downloadResolutions}
              selectedResolution={selectedResolution}
              setSelectedResolution={setSelectedResolution}
            />
          </div>

          {isDownloading && (
            <ProgressBar
              endpoint={PROXY_URL + "/api/get-progress"}
              barTrigger={isDownloading}
            />
          )}

          <Button
            variant="contained"
            onClick={downloadVideo}
            sx={{ backgroundColor: "red", textTransform: "none" }}
          >
            <Typography className="download-text w-fit">
              Download Video
            </Typography>
          </Button>
        </CardContent>
      </Card>
    </section>
  );
}
