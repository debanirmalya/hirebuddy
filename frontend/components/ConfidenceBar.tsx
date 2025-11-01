interface Props {
  value?: number;
}

export default function ConfidenceBar({ value }: Props) {
  const pct = Math.max(0, Math.min(100, Math.round((value ?? 0) * 100)));

  let tone = "bg-blue-500"; // Default (primary)
  if (pct >= 80) tone = "bg-green-500"; // Success
  else if (pct < 50) tone = "bg-yellow-400"; // Warning

  return (
    <div
      className="w-full h-2 bg-gray-200 rounded-full overflow-hidden"
      aria-label="confidence"
      title={`${pct}%`}
    >
      <div
        className={`h-full ${tone} transition-all duration-500 ease-out`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
