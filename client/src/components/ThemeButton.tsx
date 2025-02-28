import IconButton from "@mui/material/IconButton";
import { useTheme } from "./ThemeContext"; // Assuming you have the ThemeContext set up as before
import LightMode from "@mui/icons-material/LightMode";
import DarkMode from "@mui/icons-material/DarkMode";

export default function ThemeButton() {
  const { mode, toggleTheme } = useTheme(); // Get the current theme mode and the toggle function

  return (
    <IconButton onClick={toggleTheme} color="inherit">
      {/* Toggle between sun and moon icons based on current theme */}
      {mode === "light" ? <DarkMode /> : <LightMode />}
    </IconButton>
  );
}
