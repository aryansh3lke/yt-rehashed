import { useState } from "react";
import AppBar from "@mui/material/AppBar";
import Container from "@mui/material/Container";
import Toolbar from "@mui/material/Toolbar";
import Tooltip from "@mui/material/Tooltip";
import MenuItem from "@mui/material/MenuItem";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Button from "@mui/material/Button";
import Link from "@mui/material/Link";
import Drawer from "@mui/material/Drawer";

import GithubIcon from "@mui/icons-material/GitHub";
import MenuIcon from "@mui/icons-material/Menu";
import SummarizeIcon from "@mui/icons-material/Summarize";
import DownloadForOfflineIcon from "@mui/icons-material/DownloadForOffline";
import CheckBoxIcon from "@mui/icons-material/CheckBox";
import FiberManualRecordIcon from "@mui/icons-material/FiberManualRecord";

import ThemeButton from "./ThemeButton";
import { useTheme } from "@mui/material/styles";

import AppLogo from "./AppLogo";

const pages = ["Video Summarizer", "Video Downloader", "Credibility Analyzer"];
const pageIcons = [
  <SummarizeIcon />,
  <DownloadForOfflineIcon />,
  <CheckBoxIcon />,
];

export default function Navbar() {
  const [open, setOpen] = useState<boolean>(false);
  const toggleDrawer = (newOpen: boolean) => () => {
    setOpen(newOpen);
  };
  const theme = useTheme();

  return (
    <AppBar
      position="static"
      sx={{
        width: "100%",
        backgroundColor: theme.palette.mode === "light" ? "#ffffff" : "#121212",
        backgroundImage: "none",
        boxShadow:
          theme.palette.mode === "dark"
            ? "none"
            : "0px 2px 4px rgba(0, 0, 0, 0.1)",
        borderBottom:
          theme.palette.mode === "dark" ? "1.5px solid #303030" : "none",
      }}
      enableColorOnDark
    >
      <Container
        maxWidth="xl"
        sx={{
          color: theme.palette.mode === "light" ? "#121212" : "#ffffff",
        }}
      >
        <Toolbar
          disableGutters
          className="flex items-center justify-between"
          sx={{ width: "100%" }}
        >
          <Tooltip title="" placement="top-start">
            <div className="flex">
              <AppLogo />
            </div>
          </Tooltip>

          <Tooltip title="" placement="top">
            <div className="hidden lg:flex lg:flex-grow lg:flex-row">
              <Box
                sx={{
                  flexGrow: 1,
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  flexDirection: "row",
                }}
              >
                {pages.map((page, index) => (
                  <Box className="flex flex-row items-center">
                    <Button
                      href={`/${page.toLowerCase().replace(/\s/g, "-")}`}
                      key={page}
                      onClick={toggleDrawer(false)}
                      sx={{
                        color: "inherit",
                        textTransform: "none",
                      }}
                    >
                      <p className="text-xl font-semibold">{page}</p>
                    </Button>
                    {index < pages.length - 1 && (
                      <FiberManualRecordIcon
                        fontSize="small"
                        color="secondary"
                      />
                    )}
                  </Box>
                ))}
              </Box>
            </div>
          </Tooltip>

          <Tooltip title="" placement="top-end">
            <div className="hidden lg:flex">
              <Box sx={{ flexGrow: 0 }}>
                <Link
                  href="https://github.com/asshelke/yt-rehashed"
                  color="inherit"
                >
                  <IconButton color="inherit">
                    <GithubIcon />
                  </IconButton>
                </Link>
                <ThemeButton />
              </Box>
            </div>
          </Tooltip>

          <Tooltip title="" placement="top">
            <div className="flex lg:hidden"></div>
          </Tooltip>

          <Tooltip title="" placement="top-end">
            <div className="flex lg:hidden">
              <Box sx={{ flexGrow: 1 }}>
                <Link
                  href="https://github.com/asshelke/yt-rehashed"
                  color="inherit"
                >
                  <IconButton color="inherit">
                    <GithubIcon />
                  </IconButton>
                </Link>
                <ThemeButton />
                <IconButton
                  aria-label="account of current user"
                  aria-controls="menu-appbar"
                  aria-haspopup="true"
                  onClick={toggleDrawer(true)}
                  color="inherit"
                >
                  <MenuIcon />
                </IconButton>
                <Drawer
                  anchor="right"
                  open={open}
                  onClose={toggleDrawer(false)}
                  PaperProps={{
                    sx: {
                      backgroundColor:
                        theme.palette.mode === "light"
                          ? "#ffffff"
                          : "#000000 !important",
                    },
                  }}
                >
                  <Box
                    sx={{ width: 275 }}
                    role="presentation"
                    onClick={toggleDrawer(false)}
                    onKeyDown={toggleDrawer(false)}
                  >
                    {pages.map((page) => (
                      <Link
                        href={`/${page.toLowerCase().replace(/\s/g, "-")}`}
                        underline="none"
                        sx={{
                          color:
                            theme.palette.mode === "light"
                              ? "#121212"
                              : "#ffffff",
                        }}
                      >
                        <MenuItem
                          className="flex flex-row items-center justify-center gap-4"
                          key={page}
                          onClick={toggleDrawer(false)}
                          sx={{
                            py: 2,
                            px: 2,
                            color: "inherit",
                            textTransform: "none",
                          }}
                        >
                          {pageIcons[pages.indexOf(page)]}
                          <p className="text-xl font-semibold">{page}</p>
                        </MenuItem>
                      </Link>
                    ))}
                  </Box>
                </Drawer>
              </Box>
            </div>
          </Tooltip>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
