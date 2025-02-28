import { ThemeOptions } from "@mui/material/styles";

// Define the light theme options
export const lightTheme: ThemeOptions = {
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2", // Primary color for the light theme
    },
    secondary: {
      main: "#f50057", // Secondary color for the light theme
    },
    background: {
      default: "#ffffff", // Standard white background
      paper: "#ffffff", // Paper background color for components like cards
    },
    text: {
      primary: "#000000", // Standard black text
      secondary: "#4f4f4f", // Slightly lighter secondary text for better readability
    },
  },
  typography: {
    fontFamily: "Roboto, sans-serif", // Default font family
    h1: {
      fontWeight: 700, // Example custom style for h1
    },
    h2: {
      fontWeight: 700, // Example custom style for h2
    },
  },
};

// Define the dark theme options
export const darkTheme: ThemeOptions = {
  palette: {
    mode: "dark",
    primary: {
      main: "#90caf9", // Primary color for the dark theme
    },
    secondary: {
      main: "#f48fb1", // Secondary color for the dark theme
    },
    background: {
      default: "#121212", // Dark background color
      paper: "#121212", // Paper background color for components
    },
    text: {
      primary: "#ffffff", // Primary text color in dark theme
      secondary: "#b0bec5", // Secondary text color
    },
  },
  typography: {
    fontFamily: "Roboto, sans-serif", // Default font family
    h1: {
      fontWeight: 700, // Example custom style for h1
    },
    h2: {
      fontWeight: 700, // Example custom style for h2
    },
  },
};
