/**
 * Каркас 3D-силуэтов (фаза 0). Контракт для будущей замены заглушки на настоящую модель:
 * имена мешей совпадают с ключами мышц, подмена GLB не требует правки экранов.
 */
import { FLAGS } from "../flags";
import { prefersReducedMotion } from "../prefs";

export type Sex = "male" | "female";

/** Ключи групп из макетов (OnFocusF/M); позже совпадут с таблицей `muscle` в БД. */
export const MUSCLE_KEYS = ["chest", "biceps", "triceps", "delts", "abs", "lats", "glutes", "quads"] as const;
export type MuscleKey = (typeof MUSCLE_KEYS)[number];

export type BodyModel = {
  sex: Sex;
  /** Адрес GLB-файла; меши внутри называются ключами MUSCLE_KEYS. */
  url: string;
};

function hasWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") ?? canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

/** 3D показываем, только если флаг включён, есть WebGL и пользователь не просил меньше движения. */
export function canUse3D(): boolean {
  return FLAGS.threeD && !prefersReducedMotion() && hasWebGL();
}

/**
 * Единая точка получения модели. Пока настоящих моделей нет, возвращает null,
 * и экраны показывают 2D-вариант (`Silhouette2D`).
 */
export async function getBodyModel(sex: Sex): Promise<BodyModel | null> {
  if (!canUse3D()) return null;
  void sex;
  return null;
}
