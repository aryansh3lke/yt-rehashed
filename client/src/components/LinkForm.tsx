export default function LinkForm({
  prompt,
  placeholder,
  inputLink,
  setLink,
  onSubmit
}: {
  prompt: string,
  placeholder: string,
  inputLink: string,
  setLink: React.Dispatch<React.SetStateAction<string>>,
  onSubmit: (e: React.FormEvent) => void
}) {
  return (
    <div>
        <h3>{prompt}</h3>
        <div className="link-form">
            <input
                className="input-box"
                type="text"
                value={inputLink}
                placeholder={placeholder}
                onChange={(e) => setLink(e.target.value)}>
            </input>
            <button className="submit-button" onClick={onSubmit}>Summarize</button>
        </div>
    </div>
  )
}
