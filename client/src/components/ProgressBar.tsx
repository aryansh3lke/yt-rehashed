import { useState, useEffect } from "react";
import LinearProgress, {
  LinearProgressProps,
} from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function LinearProgressWithLabel(
  props: LinearProgressProps & { value: number },
) {
  const getCurrentTask = () => {
    if (props.value < 40) {
      return "Downloading video stream";
    } else if (props.value < 80) {
      return "Downloading audio stream";
    } else {
      return "Merging streams";
    }
  };
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: 2,
      }}
    >
      <Box sx={{ width: "100%", mr: 1 }}>
        <LinearProgress variant="determinate" {...props} />
      </Box>
      <Box sx={{ minWidth: 35 }}>
        <Typography
          variant="body2"
          textAlign={"center"}
          sx={{ color: "text.secondary" }}
        >
          {getCurrentTask()} ({`${Math.round(props.value)}%`})
        </Typography>
      </Box>
    </Box>
  );
}

export default function ProgressBar({
  endpoint,
  barTrigger,
}: {
  endpoint: string;
  barTrigger: boolean;
}) {
  const [progress, setProgress] = useState<number>(0.0);
  const [downloadComplete, setDownloadComplete] = useState<boolean>(false);
  // create hook for mounting component
  useEffect(() => {
    const getProgress = async () => {
      if (progress === 100.0) {
        clearInterval(interval);
        setDownloadComplete(true);
        setProgress(0.0);
      }

      fetch(endpoint)
        .then((res) => res.json())
        .then((data) => {
          setProgress(data.progress);
        })
        .catch((error) => {
          console.error("Error fetching status:", error);
        });
    };

    const interval = setInterval(getProgress, 500);

    return () => {
      clearInterval(interval);
    };
  });

  return (
    <>
      {!downloadComplete && (
        <Box sx={{ width: "100%", px: 10 }}>
          <LinearProgressWithLabel value={progress} />
        </Box>
      )}
    </>
  );
}
