// Access Vercel environment variable in production to reach deployed backend server on Railway
export const PROXY_URL =
  process.env.REACT_APP_PROXY_URL || "http://localhost:8000";

// For other branches to test deployment on Railway
// export const PROXY_URL = "https://yt-rehashed-test.up.railway.app";
