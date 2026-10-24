export const money = (amount: number) =>
  `${new Intl.NumberFormat("fa-IR").format(amount)} ریال`;
export const dateTime = (value: string) =>
  new Intl.DateTimeFormat("fa-IR", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Tehran",
  }).format(new Date(value));
export const time = (value: string) =>
  new Intl.DateTimeFormat("fa-IR", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Tehran",
  }).format(new Date(value));
