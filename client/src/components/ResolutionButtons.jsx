import React from 'react'

export default function ResolutionButtons({downloadResolutions, selectedResolution, setSelectedResolution}) {
  return (
    <ul className="resolution-buttons">
        {downloadResolutions.map((resolution, index) => (
        <li key={index}>
            <input
            type="radio"
            id={resolution}
            value={resolution}
            checked={resolution === selectedResolution}
            onChange={ (e) => {setSelectedResolution(e.target.value)} }
            name="options"/>
            <label htmlFor={resolution}>{resolution}</label>
        </li>
        ))}
    </ul>
  )
}
