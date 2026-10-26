/**
 * Офлайн-очередь записи подходов и оценок (K7, C10).
 *
 * Операции выполняются строго по порядку. Если сети нет, запись остаётся на устройстве и
 * отправляется при возвращении связи; сервер не создаёт дубль, потому что у подхода есть client_id.
 */

export type QueuedOp =
  | { id: string; kind: "set"; workoutId: number; payload: Record<string, unknown> }
  | {
      id: string;
      kind: "rating";
      workoutId: number;
      exerciseId: number;
      rating: "easy" | "normal" | "hard";
      pain: boolean;
    };

type Storage = Pick<globalThis.Storage, "getItem" | "setItem">;

/** Результат отправки: sent — принято, retry — нет связи или сбой сервера, drop — отклонено навсегда. */
export type SendResult = "sent" | "retry" | "drop";

const KEY = "levefit.queue";

export type Queue = ReturnType<typeof createQueue>;

export function createQueue(storage: Storage, send: (op: QueuedOp) => Promise<SendResult>) {
  let ops: QueuedOp[] = [];
  let dropped = 0;
  let flushing: Promise<void> | null = null;
  const listeners = new Set<() => void>();

  try {
    const raw = storage.getItem(KEY);
    if (raw) ops = JSON.parse(raw) as QueuedOp[];
  } catch {
    ops = [];
  }

  const persist = () => {
    try {
      storage.setItem(KEY, JSON.stringify(ops));
    } catch {
      // нет места или хранилище закрыто: очередь живёт, пока открыто приложение
    }
    listeners.forEach((listener) => listener());
  };

  async function run(): Promise<void> {
    while (ops.length > 0) {
      const result = await send(ops[0]).catch((): SendResult => "retry");
      if (result === "retry") return;
      if (result === "drop") dropped += 1;
      ops = ops.slice(1);
      persist();
    }
  }

  return {
    /** Ставит операцию в очередь и пытается отправить всё накопленное по порядку. */
    async submit(op: QueuedOp): Promise<"sent" | "queued"> {
      ops = [...ops, op];
      persist();
      await this.flush();
      return ops.some((queued) => queued.id === op.id) ? "queued" : "sent";
    },
    /** Отправляет накопленное; параллельные вызовы объединяются в один. */
    flush(): Promise<void> {
      flushing ??= run().finally(() => {
        flushing = null;
      });
      return flushing;
    },
    pending(workoutId?: number): QueuedOp[] {
      return workoutId === undefined ? ops : ops.filter((op) => op.workoutId === workoutId);
    },
    /** Сколько операций сервер отклонил насовсем (например, тренировка уже завершена). */
    droppedCount: () => dropped,
    subscribe(listener: () => void): () => void {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}

export function newId(): string {
  const c = globalThis.crypto;
  if (c?.randomUUID) return c.randomUUID();
  // запасной вариант для старых WebView: случайный идентификатор нужной длины
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (ch) => {
    const r = Math.floor(Math.random() * 16);
    return (ch === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}
