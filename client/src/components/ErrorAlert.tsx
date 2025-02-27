import { useState, useEffect } from "react";
import Collapse from "@mui/material/Collapse";
import Alert from "@mui/material/Alert";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";

export default function ErrorAlert({
  message,
  setMessage,
}: {
  message: string;
  setMessage: React.Dispatch<React.SetStateAction<string>>;
}) {
  const [open, setOpen] = useState<boolean>(false);

  useEffect(() => {
    setTimeout(() => setOpen(true), 50); // Small delay for animation to trigger
  }, []);

  return (
    <Collapse in={open} timeout={{ enter: 700, exit: 300 }} easing="ease-out">
      <Alert
        action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="small"
            onClick={() => {
              setOpen(false);
            }}
          >
            <CloseIcon fontSize="inherit" />
          </IconButton>
        }
        severity="error"
        sx={{ mb: 2, maxWidth: "500px" }}
      >
        {message}
      </Alert>
    </Collapse>
  );
}
