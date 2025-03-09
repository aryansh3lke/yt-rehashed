import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

export default function BackgroundCard({
  background,
  animationDelay,
}: {
  background: string;
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
        minWidth: 300,
        maxWidth: 600,
      }}
    >
      <Typography variant="h6" textAlign="center" gutterBottom>
        Creator Background
      </Typography>

      <CardContent
        sx={{
          width: "100%",
          pt: 0,
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
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
          <Typography
            variant="body1"
            sx={{
              lineHeight: 1.5,
              flex: 1,
              width: "fit-content",
            }}
          >
            {background}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
