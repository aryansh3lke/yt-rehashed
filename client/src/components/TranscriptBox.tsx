import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";

import { Caption } from "../types/interfaces";

export default function TranscriptBox({
  captions,
  setSeekTime,
  animationDelay,
}: {
  captions: Caption[];
  setSeekTime: React.Dispatch<React.SetStateAction<number>>;
  animationDelay: number;
}) {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  };
  return (
    <section
      className="slide-up flex w-1/2 flex-col gap-8"
      style={{ animationDelay: `${animationDelay}s` }}
    >
      <Typography variant="h3" fontWeight={400} textAlign="center">
        Video Transcript
      </Typography>
      <Card className="card-height" sx={{ overflowY: "auto", borderRadius: 2 }}>
        <CardContent>
          {captions.map((caption, index) => (
            <Box className="flex w-full flex-row gap-4 p-2" key={index}>
              <Button sx={{ p: 0 }} onClick={() => setSeekTime(caption.start)}>
                <Typography variant="body2" textAlign={"left"}>
                  {formatTime(caption.start)}
                </Typography>
              </Button>
              <Typography variant="body2" textAlign={"left"}>
                {caption.text}
              </Typography>
            </Box>
          ))}
        </CardContent>
      </Card>
    </section>
  );
}
