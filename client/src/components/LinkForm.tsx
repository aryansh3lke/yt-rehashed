import React from "react";
import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";

export default function LinkForm({
  prompt,
  placeholder,
  inputLink,
  setLink,
  onSubmit,
}: {
  prompt: string;
  placeholder: string;
  inputLink: string;
  setLink: React.Dispatch<React.SetStateAction<string>>;
  onSubmit: (e: React.FormEvent) => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-6">
      <p className="text-center text-4xl font-bold md:text-7xl">
        Video Summarizer
      </p>
      <p className="text-wrap text-center text-lg md:text-2xl">{prompt}</p>
      <Paper
        component="form"
        className="w-[500px] max-sm:w-full"
        sx={{ p: "2px 4px", display: "flex", alignItems: "center" }}
      >
        <InputBase
          sx={{ ml: 1, flex: 1 }}
          placeholder={placeholder}
          inputProps={{ "aria-label": "search google maps" }}
          value={inputLink}
          onChange={(e) => setLink(e.target.value)}
        />
        <Divider sx={{ height: 28, m: 0.5 }} orientation="vertical" />
        <Button
          color="primary"
          sx={{ p: "10px", color: "red" }}
          aria-label="submit"
          onClick={onSubmit}
        >
          Summarize
        </Button>
      </Paper>
    </div>
  );
}
