export function Arrow({
  direction = "left",
}: {
  direction?: "left" | "right";
}) {
  return (
    <svg
      className={`icon ${direction === "right" ? "icon--reversed" : ""}`}
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M20 12H4m0 0 6-6m-6 6 6 6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="square"
        strokeLinejoin="miter"
      />
    </svg>
  );
}
export function Refresh() {
  return (
    <svg
      className="icon"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M20 10a8 8 0 1 0-1.5 7M20 4v6h-6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="square"
      />
    </svg>
  );
}
