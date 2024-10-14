import React from 'react'

export default function CloseButton({ onClose }) {
  return (
    <button className="close-button" onClick={onClose}>&times;</button>
  )
}
