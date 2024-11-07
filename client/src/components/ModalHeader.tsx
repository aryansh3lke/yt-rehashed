export default function ModalHeader({
  title
}: {
  title: string
}) {
  return (
    <div className="modal-header">
        <h4 className="modal-title">{title}</h4>
    </div>
  )
}
