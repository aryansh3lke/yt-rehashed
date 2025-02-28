import Link from "@mui/material/Link";

export default function AppLogo() {
  return (
    <Link
      href="/"
      className="flex flex-row items-center justify-center gap-2"
      underline="none"
      sx={{ color: "inherit" }}
    >
      <img
        src="/logo192.png"
        alt="App Icon"
        className="h-8 w-8 md:h-10 md:w-10"
      />
      <p className="text-nowrap text-center text-2xl font-bold md:text-4xl">
        YT Rehashed
      </p>
    </Link>
  );
}
