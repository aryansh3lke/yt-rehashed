import { useEffect, useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import { useTheme } from "@mui/material/styles";

const getScoreColor = (value: number, isDarkMode: boolean): string => {
  if (value <= 50) {
    // Red (0) to Orange (30)
    const hue = 30 * (value / 50);
    return `hsl(${hue}, 100%, 50%)`;
  } else {
    // Orange (30) to Green (120)
    const hue = 30 + 90 * ((value - 50) / 50);
    return `hsl(${hue}, 100%, 50%)`;
  }
};

const AnimatedScore = ({ value, label }: { value: number; label: string }) => {
  const [progress, setProgress] = useState(0);
  const theme = useTheme();

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prevProgress) => {
        if (prevProgress >= value) {
          clearInterval(timer);
          return value;
        }
        return prevProgress + 1;
      });
    }, 20);

    return () => {
      clearInterval(timer);
    };
  }, [value]);

  const isDarkMode = theme.palette.mode === "dark";

  return (
    <Box
      sx={{
        position: "relative",
        display: "inline-flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 1,
      }}
    >
      <Box sx={{ position: "relative", display: "inline-flex" }}>
        <CircularProgress
          variant="determinate"
          value={100}
          size={80}
          thickness={4}
          sx={{ color: (theme) => theme.palette.grey[200] }}
        />
        <CircularProgress
          variant="determinate"
          value={progress}
          size={80}
          thickness={4}
          sx={{
            position: "absolute",
            left: 0,
            color: getScoreColor(progress, isDarkMode),
          }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: "absolute",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Typography
            variant="h6"
            component="div"
            sx={{ color: getScoreColor(progress, isDarkMode) }}
          >
            {progress}
          </Typography>
        </Box>
      </Box>
      <Typography variant="body1" color="text.secondary" textAlign="center">
        {label}
      </Typography>
    </Box>
  );
};

export default function ScoresCard({
  credibilityScore,
  contentQualityScore,
  engagementScore,
  animationDelay,
}: {
  credibilityScore: number;
  contentQualityScore: number;
  engagementScore: number;
  animationDelay: number;
}) {
  return (
    <Card
      className="slide-up card-height"
      sx={{
        position: "relative",
        display: "flex",
        flexDirection: "column",
        p: 2,
        animationDelay: `${animationDelay}s`,
        height: "400px",
        minWidth: 300,
        maxWidth: 600,
      }}
    >
      <Typography variant="h6" textAlign="center" gutterBottom>
        Creator Scores
      </Typography>

      <CardContent
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "space-around",
          flex: 1,
          pt: 0,
        }}
      >
        <AnimatedScore value={contentQualityScore} label="Content Quality" />
        <AnimatedScore value={engagementScore} label="Engagement" />
        <AnimatedScore value={credibilityScore} label="Credibility" />
      </CardContent>
    </Card>
  );
}
