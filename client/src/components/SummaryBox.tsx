export default function SummaryBox({
  summaryTitle,
  summaryText,
  animationDelay
}: {
  summaryTitle: string,
  summaryText: string,
  animationDelay: number
}) {
  return (
    <section className="main-box-outer slide-up" style={{ animationDelay: `${animationDelay}s`}}>
        <h2 className="section-title">{summaryTitle}</h2>
        <div className="main-box-inner text-box">
            <p className="summary">{summaryText}</p>
        </div>
    </section>
  )
}
