import VideoEmbed from "./VideoEmbed";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import Box from "@mui/material/Box";
import CardContent from "@mui/material/CardContent";
import IconButton from "@mui/material/IconButton";
import DownloadIcon from "@mui/icons-material/FileDownload";
import Button from "@mui/material/Button";
import { Caption } from "../types/interfaces";

export default function VideoPlayer({
  videoId,
  captions,
  seekTime,
  setSeekTime,
  displayResolutions,
  animationDelay,
}: {
  videoId: string;
  captions: Caption[];
  seekTime: number;
  setSeekTime: React.Dispatch<React.SetStateAction<number>>;
  displayResolutions: (e: React.MouseEvent) => void;
  animationDelay: number;
}) {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  };
  return (
    <section
      className="slide-up flex flex-col gap-8 md:w-1/2"
      style={{ animationDelay: `${animationDelay}s` }}
    >
      <Box className="mt-5 flex flex-row items-center justify-center gap-2">
        <p className="text-center text-4xl md:text-5xl">Original Video</p>

        <IconButton
          onClick={displayResolutions}
          sx={{ height: "40px", width: "40px" }}
        >
          <DownloadIcon fontSize="large" />
        </IconButton>
      </Box>
      <Card className="card-height" sx={{ borderRadius: 2 }}>
        <CardContent className="flex flex-col items-center gap-2" sx={{ p: 0 }}>
          <Box className="two-thirds-card-height w-full">
            <VideoEmbed videoId={videoId} seekTime={seekTime} />
          </Box>
          <Box
            className="third-card-height flex w-full flex-col justify-start"
            sx={{ overflowY: "auto", borderRadius: 2 }}
          >
            {captions.map((caption, index) => (
              <Box
                className="flex w-full flex-row justify-start gap-4 p-2"
                key={index}
              >
                <Button
                  sx={{ p: 0 }}
                  onClick={() => setSeekTime(caption.start)}
                >
                  <Typography variant="body2" textAlign={"left"}>
                    {formatTime(caption.start)}
                  </Typography>
                </Button>
                <Typography variant="body2" textAlign={"left"}>
                  {caption.text}
                </Typography>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
    </section>
  );
}
