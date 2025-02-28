import CircularProgress from "@mui/material/CircularProgress";
export default function Loader({
  loaderTrigger,
  loaderType,
}: {
  loaderTrigger: boolean;
  loaderType: string;
}) {
  return (
    <>
      {loaderTrigger && (
        <div
          className={`loader-div ${loaderType === "summary-loader" && "mt-24"}`}
        >
          <CircularProgress color="secondary" size={100} />
        </div>
      )}
    </>
  );
}
