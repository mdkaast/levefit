import { addSet, classifyFailure, rateExercise, type SetInput } from "./api";
import { createQueue, type QueuedOp, type SendResult } from "./offline";

/** Общая очередь записи на устройстве: подходы и оценки не теряются при обрыве связи. */
const storage = {
  getItem(key: string): string | null {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  setItem(key: string, value: string): void {
    try {
      localStorage.setItem(key, value);
    } catch {
      // хранилище недоступно
    }
  },
};

async function send(op: QueuedOp): Promise<SendResult> {
  try {
    if (op.kind === "set") await addSet(op.workoutId, op.payload as SetInput);
    else await rateExercise(op.workoutId, op.exerciseId, op.rating, op.pain);
    return "sent";
  } catch (error) {
    return classifyFailure(error);
  }
}

export const queue = createQueue(storage, send);

if (typeof window !== "undefined") {
  window.addEventListener("online", () => void queue.flush());
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") void queue.flush();
  });
  void queue.flush();
}
