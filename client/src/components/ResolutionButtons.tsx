import { Resolution } from '../types/interfaces';

export default function ResolutionButtons({
  downloadResolutions,
  selectedResolution,
  setSelectedResolution
} : {
  downloadResolutions: Resolution[],
  selectedResolution: Resolution,
  setSelectedResolution: React.Dispatch<React.SetStateAction<Resolution>>
}) {
  return (
    <ul className="resolution-buttons">
        {downloadResolutions.map((resolution, index) => (
        <li key={index}>
            <input
            type="radio"
            id={resolution}
            value={resolution}
            checked={resolution === selectedResolution}
            onChange={ (e) => {setSelectedResolution(e.target.value as Resolution)} }
            name="options"/>
            <label htmlFor={resolution}>{resolution}</label>
        </li>
        ))}
    </ul>
  )
}
