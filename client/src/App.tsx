import { Routes, Route } from "react-router-dom";
import VideoSummarizer from "./pages/VideoSummarizer";
import VideoDownloader from "./pages/VideoDownloader";
import CredibilityAnalyzer from "./pages/CredibilityAnalyzer";
import Navbar from "./components/Navbar";
import { useTheme } from "@mui/material";

function App() {
  const theme = useTheme();

  return (
    <main
      className={`flex min-h-screen flex-col items-center ${theme.palette.mode === "light" ? "bg-white" : "bg-[#121212]"} ${theme.palette.mode === "light" ? "text-black" : "text-white"}`}
    >
      <div className="lg:gap-15 flex w-full flex-1 flex-col items-center gap-5">
        <Navbar />
        <div className="flex flex-col">
          <div className="flex max-w-7xl flex-col gap-20 p-5">
            <Routes>
              <Route path="/" element={<VideoSummarizer />} />
              <Route path="/video-summarizer" element={<VideoSummarizer />} />
              <Route path="/video-downloader" element={<VideoDownloader />} />
              <Route
                path="/credibility-analyzer"
                element={<CredibilityAnalyzer />}
              />
            </Routes>
          </div>
        </div>
      </div>
    </main>
  );
}

export default App;
