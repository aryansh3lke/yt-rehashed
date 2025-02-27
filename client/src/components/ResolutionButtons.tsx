import { Resolution } from "../types/interfaces";
import RadioGroup from "@mui/material/RadioGroup";
import Radio from "@mui/material/Radio";
import FormControlLabel from "@mui/material/FormControlLabel";

export default function ResolutionButtons({
  downloadResolutions,
  selectedResolution,
  setSelectedResolution,
}: {
  downloadResolutions: Resolution[];
  selectedResolution: Resolution;
  setSelectedResolution: React.Dispatch<React.SetStateAction<Resolution>>;
}) {
  return (
    <RadioGroup
      className="flex flex-row flex-wrap items-center justify-center gap-2 md:px-10"
      name="resolution-buttons-group"
      row
    >
      {downloadResolutions.map((resolution, index) => (
        <FormControlLabel
          key={resolution}
          id={resolution}
          label={resolution}
          control={<Radio />}
          checked={resolution === selectedResolution}
          onChange={() => {
            setSelectedResolution(resolution);
          }}
          name="options"
        />
      ))}
    </RadioGroup>
  );
}
