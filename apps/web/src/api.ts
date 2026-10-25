const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Character = {
  name: string;
  level: number;
  xp: number;
  strength: number;
  endurance: number;
  agility: number;
  discipline: number;
  appearance: string;
  goal: string | null;
  workouts_per_week: number;
  equipment: string;
};

export type Me = { user: { id: number; username: string | null }; character: Character | null };

export type CharacterInput = {
  name: string;
  appearance: string;
  goal: string | null;
  workouts_per_week: number;
  equipment: string;
};

let token: string | null = null;

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json() as Promise<T>;
}

export async function login(initData: string): Promise<void> {
  const body = await request<{ access_token: string }>("/auth/telegram", {
    method: "POST",
    body: JSON.stringify({ init_data: initData }),
  });
  token = body.access_token;
}

export const getMe = () => request<Me>("/me");

export const createCharacter = (input: CharacterInput) =>
  request<Character>("/characters", { method: "POST", body: JSON.stringify(input) });
