export interface User {
  id: string;
  name: string;
  email: string;
  role: "admin" | "customer";
}
export interface Session {
  access_token: string;
  user: User;
}
export interface Resource {
  id: string;
  name: string;
  description: string;
}
export interface Slot {
  id: string;
  resource_id: string;
  starts_at: string;
  ends_at: string;
  price_irr: number;
}
export interface Reservation {
  id: string;
  slot_id: string;
  amount_irr: number;
  slot: Slot;
  status: "pending" | "confirmed" | "cancelled";
  created_at: string;
}
export interface Payment {
  id: string;
  reservation_id: string;
  status: "pending" | "succeeded";
}
export interface Transaction {
  id: string;
  payment_id: string;
  reference: string;
  amount_irr: number;
  created_at: string;
}
export interface Credentials {
  name?: string;
  email: string;
  password: string;
}
export interface NewSlot {
  resource_id: string;
  starts_at: string;
  ends_at: string;
  price_irr: number;
}
