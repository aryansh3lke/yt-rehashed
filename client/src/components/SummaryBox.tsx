import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";

export default function SummaryBox({
  summaryTitle,
  summaryText,
  animationDelay,
}: {
  summaryTitle: string;
  summaryText: string;
  animationDelay: number;
}) {
  return (
    <section
      className="slide-up flex flex-col gap-8 md:w-1/2"
      style={{ animationDelay: `${animationDelay}s` }}
    >
      <p className="mt-5 text-wrap text-center text-4xl md:text-5xl">
        {summaryTitle}
      </p>
      <Card className="card-height" sx={{ overflowY: "auto", borderRadius: 2 }}>
        <CardContent>
          <Typography variant="body1" className="p-2 text-start">
            {summaryText}
          </Typography>
        </CardContent>
      </Card>
    </section>
  );
}
