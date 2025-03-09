import React from "react";
import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";

export default function LinkForm({
  title,
  prompt,
  placeholder,
  inputLink,
  setInputLink,
  onSubmit,
  submitText,
}: {
  title: string;
  prompt: string;
  placeholder: string;
  inputLink: string;
  setInputLink: React.Dispatch<React.SetStateAction<string>>;
  onSubmit: (e: React.FormEvent) => void;
  submitText: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-6">
      <p className="text-center text-4xl font-bold md:text-7xl">{title}</p>
      <p className="text-wrap text-center text-lg md:text-2xl">{prompt}</p>
      <Paper
        component="form"
        className="w-[500px] max-sm:w-full"
        sx={{ p: "2px 4px", display: "flex", alignItems: "center" }}
        onSubmit={onSubmit}
      >
        <InputBase
          sx={{ ml: 1, flex: 1 }}
          placeholder={placeholder}
          inputProps={{ "aria-label": "search google maps" }}
          value={inputLink}
          onChange={(e) => setInputLink(e.target.value)}
        />
        <Divider sx={{ height: 28, m: 0.5 }} orientation="vertical" />
        <Button
          color="primary"
          sx={{ p: "10px", color: "red" }}
          aria-label="submit"
          type="submit"
        >
          {submitText}
        </Button>
      </Paper>
    </div>
  );
}
