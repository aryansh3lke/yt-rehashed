export default function CloseButton({ onClose }: { onClose: () => void }) {
  return (
    <button className="close-button" onClick={onClose}>
      &times;
    </button>
  );
}
