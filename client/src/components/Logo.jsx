import React from 'react'

export default function Logo({ logoTitle, logoSrc }) {
  return (
    <div className="logo-title">
          <img className="app-logo" src={logoSrc} alt={`${logoTitle} Logo`}></img>
          <h1>{logoTitle}</h1>
    </div>
  )
}
