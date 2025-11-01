export function utcToIndianTime(utcDateString?: string): string {
  if (!utcDateString) return "—";

  const utcDate = new Date(utcDateString);
  if (isNaN(utcDate.getTime())) return "Invalid Date";

  // Add 5 hours 30 minutes manually
  const indiaTime = new Date(utcDate.getTime() + 5.5 * 60 * 60 * 1000);

  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  };

  return new Intl.DateTimeFormat("en-IN", options).format(indiaTime);
}
