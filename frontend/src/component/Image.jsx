export default function Image({ src }) {
  return (
    <img
      src={src}
      style={{
        // border: "8px solid darkred",
        // borderRadius: "8px",
        // margin: "40",
        width: "auto",
        maxWidth: "100%",
        // maxWidth: "49vw",
        maxHeight: "500px",
        minHeight: "500px",
        // height: "auto"
      }}
    />
  );
}
