import Button from "@mui/material/Button";

export default function DownloadVideoButton({
  downloadVideo,
}: {
  downloadVideo: (e: React.MouseEvent) => void;
}) {
  return (
    <Button
      variant="contained"
      onClick={downloadVideo}
      sx={{ backgroundColor: "red" }}
    >
      <p className="download-text">Download Video</p>
    </Button>
  );
}
