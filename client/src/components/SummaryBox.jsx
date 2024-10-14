import React from 'react'

export default function SummaryBox({ summaryTitle, summaryText }) {
  return (
    <section className="main-box-outer">
        <h2 className="section-title">{summaryTitle}</h2>
        <div className="main-box-inner text-box">
            <p className="summary">{summaryText}</p>
        </div>
    </section>
  )
}
