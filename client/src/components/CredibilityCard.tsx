import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import VerifiedIcon from "@mui/icons-material/Verified";

interface CredibilityCardProps {
  credibilityPoints: string[];
  animationDelay: number;
}

export default function CredibilityCard({
  credibilityPoints,
  animationDelay,
}: CredibilityCardProps) {
  return (
    <Card
      className="slide-up card-height"
      sx={{
        position: "relative",
        display: "flex",
        flexDirection: "column",
        p: 2,
        animationDelay: `${animationDelay}s`,
        minWidth: 300,
        maxWidth: 600,
      }}
    >
      <Typography variant="h6" textAlign="center" gutterBottom>
        Credibility Analysis
      </Typography>

      <CardContent
        sx={{
          flex: 1,
          padding: 0,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        <List
          sx={{
            flex: 1,
            border: "1px solid",
            borderColor: "divider",
            borderRadius: 1,
            padding: 2,
            overflowY: "auto",
            "&::-webkit-scrollbar": {
              width: "8px",
            },
            "&::-webkit-scrollbar-track": {
              background: "#f1f1f1",
            },
            "&::-webkit-scrollbar-thumb": {
              background: "#888",
              borderRadius: "4px",
            },
            "&::-webkit-scrollbar-thumb:hover": {
              background: "#555",
            },
          }}
        >
          {credibilityPoints.map((point, index) => (
            <ListItem key={index} alignItems="flex-start" disablePadding>
              <ListItemIcon sx={{ minWidth: 36 }}>
                <VerifiedIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary={point}
                sx={{
                  "& .MuiListItemText-primary": {
                    fontSize: "1rem",
                    lineHeight: 1.5,
                  },
                }}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}
