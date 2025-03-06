import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Avatar from "@mui/material/Avatar";
import IconButton from "@mui/material/IconButton";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import PeopleIcon from "@mui/icons-material/People";
import VideoLibraryIcon from "@mui/icons-material/VideoLibrary";
import VisibilityIcon from "@mui/icons-material/Visibility";
import Box from "@mui/material/Box";

interface CreatorCardProps {
  handle: string;
  title: string;
  statistics: {
    subscriberCount: number;
    videoCount: number;
    viewCount: number;
  };
  avatar: string;
  animationDelay: number;
}

const formatNumber = (num: number): string => {
  if (num >= 1000000000000) {
    return `${(num / 1000000000000).toFixed(1)}T`;
  } else if (num >= 1000000000) {
    return `${(num / 1000000000).toFixed(1)}B`;
  } else if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

export default function CreatorCard({
  handle,
  title,
  statistics,
  avatar,
  animationDelay,
}: CreatorCardProps) {
  const channelUrl = `https://youtube.com/${handle}`;

  return (
    <Card
      className="slide-up card-height"
      sx={{
        maxWidth: 300,
        position: "relative",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        p: 2,
        animationDelay: `${animationDelay}s`,
      }}
    >
      {/* External Link Button */}
      <IconButton
        size="small"
        sx={{
          position: "absolute",
          top: 8,
          right: 8,
          zIndex: 1,
          backgroundColor: "transparent",
          "&:hover": {
            backgroundColor: "action.hover",
          },
        }}
        onClick={() => window.open(channelUrl, "_blank")}
        aria-label="open channel"
      >
        <OpenInNewIcon sx={{ fontSize: 20 }} />
      </IconButton>

      {/* Avatar */}
      <Avatar
        src={avatar}
        sx={{
          width: 120,
          height: 120,
          mb: 2,
          border: 3,
          borderColor: "red",
        }}
      />

      {/* Channel Handle */}
      <Typography variant="h6" textAlign="center" gutterBottom>
        {title} ({handle})
      </Typography>

      {/* Statistics */}
      <CardContent sx={{ width: "100%" }}>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <PeopleIcon color="action" sx={{ fontSize: 20 }} />
            <Typography variant="body1">
              {formatNumber(statistics.subscriberCount)} subscribers
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <VideoLibraryIcon color="action" sx={{ fontSize: 20 }} />
            <Typography variant="body1">
              {formatNumber(statistics.videoCount)} videos
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <VisibilityIcon color="action" sx={{ fontSize: 20 }} />
            <Typography variant="body1">
              {formatNumber(statistics.viewCount)} views
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
