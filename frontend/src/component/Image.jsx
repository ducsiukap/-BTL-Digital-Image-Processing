export default function Image({ src }) {
  return (
    <img
      src={src}
      style={{
        border: "3px solid red",
        borderRadius: "8px",
        margin: "5px",
        maxWidth: "48vw",
        maxHeight: "640px",
      }}
    />
  );
}
