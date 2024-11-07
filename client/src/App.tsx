import { Routes, Route } from "react-router-dom";
import Summarizer from "./pages/Summarizer";
import Downloader from "./pages/Downloader";
import Navbar from "./components/Navbar";

function App() {
  return (
    <>
      <Navbar />
      <Routes>
          <Route path="/" element={<Summarizer />} />
          <Route path="/summarizer" element={<Summarizer />} />
          <Route path="/downloader" element={<Downloader />} />
      </Routes>
    </>
  );
}

export default App;