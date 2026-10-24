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

export const number = (value: number, digits = 1) =>
  new Intl.NumberFormat("fa-IR", {
    minimumIntegerDigits: digits,
    useGrouping: false,
  }).format(value);

export function dayParts(value: string) {
  const date = new Date(value);
  const zone = { timeZone: "Asia/Tehran" };
  return {
    key: new Intl.DateTimeFormat("en-CA", {
      ...zone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(date),
    weekday: new Intl.DateTimeFormat("fa-IR", {
      ...zone,
      weekday: "long",
    }).format(date),
    label: new Intl.DateTimeFormat("fa-IR", {
      ...zone,
      day: "numeric",
      month: "long",
      year: "numeric",
    }).format(date),
  };
}

export const duration = (start: string, end: string) =>
  `${number(Math.round((new Date(end).getTime() - new Date(start).getTime()) / 60000))} دقیقه`;
