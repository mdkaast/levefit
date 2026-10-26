import { describe, expect, it } from "vitest";
import { createQueue, newId, type QueuedOp, type SendResult } from "./offline";

function memoryStorage(initial?: string) {
  const data = new Map<string, string>(initial ? [["levefit.queue", initial]] : []);
  return {
    getItem: (key: string) => data.get(key) ?? null,
    setItem: (key: string, value: string) => void data.set(key, value),
    dump: () => data.get("levefit.queue"),
  };
}

const set = (id: string, reps = 8): QueuedOp => ({
  id,
  kind: "set",
  workoutId: 1,
  payload: { exercise_id: 1, reps, client_id: id },
});

describe("офлайн-очередь", () => {
  it("отправляет по порядку и очищается", async () => {
    const sent: string[] = [];
    const q = createQueue(memoryStorage(), async (op) => {
      sent.push(op.id);
      return "sent";
    });
    expect(await q.submit(set("a"))).toBe("sent");
    expect(await q.submit(set("b"))).toBe("sent");
    expect(sent).toEqual(["a", "b"]);
    expect(q.pending()).toEqual([]);
  });

  it("при отсутствии связи оставляет записи и отправляет их позже в том же порядке", async () => {
    let online = false;
    const sent: string[] = [];
    const storage = memoryStorage();
    const q = createQueue(storage, async (op): Promise<SendResult> => {
      if (!online) return "retry";
      sent.push(op.id);
      return "sent";
    });
    expect(await q.submit(set("a"))).toBe("queued");
    expect(await q.submit(set("b"))).toBe("queued");
    expect(q.pending().map((o) => o.id)).toEqual(["a", "b"]);
    expect(JSON.parse(storage.dump() ?? "[]")).toHaveLength(2);

    online = true;
    await q.flush();
    expect(sent).toEqual(["a", "b"]);
    expect(q.pending()).toEqual([]);
  });

  it("новая запись не обгоняет старую: порядок подходов сохраняется", async () => {
    let online = false;
    const sent: string[] = [];
    const q = createQueue(memoryStorage(), async (op): Promise<SendResult> => {
      if (!online) return "retry";
      sent.push(op.id);
      return "sent";
    });
    await q.submit(set("first"));
    online = true;
    expect(await q.submit(set("second"))).toBe("sent");
    expect(sent).toEqual(["first", "second"]);
  });

  it("запись переживает перезапуск приложения", async () => {
    const storage = memoryStorage();
    const offline = createQueue(storage, async () => "retry");
    await offline.submit(set("a"));
    const restarted = createQueue(storage, async () => "sent");
    expect(restarted.pending().map((o) => o.id)).toEqual(["a"]);
    await restarted.flush();
    expect(restarted.pending()).toEqual([]);
  });

  it("навсегда отклонённая запись не блокирует очередь, но считается", async () => {
    const q = createQueue(memoryStorage(), async (op): Promise<SendResult> => (op.id === "bad" ? "drop" : "sent"));
    await q.submit(set("bad"));
    await q.submit(set("good"));
    expect(q.pending()).toEqual([]);
    expect(q.droppedCount()).toBe(1);
  });

  it("исключение при отправке трактуется как «повторить позже»", async () => {
    const q = createQueue(memoryStorage(), async () => {
      throw new Error("network");
    });
    expect(await q.submit(set("a"))).toBe("queued");
    expect(q.pending()).toHaveLength(1);
  });

  it("параллельные flush не отправляют одну запись дважды", async () => {
    let calls = 0;
    const q = createQueue(memoryStorage(), async () => {
      calls += 1;
      await Promise.resolve();
      return "sent";
    });
    await q.submit(set("a"));
    await Promise.all([q.flush(), q.flush()]);
    expect(calls).toBe(1);
  });

  it("считает записи по тренировке и сообщает подписчикам", async () => {
    const q = createQueue(memoryStorage(), async () => "retry");
    let notified = 0;
    q.subscribe(() => (notified += 1));
    await q.submit(set("a"));
    await q.submit({ ...set("b"), workoutId: 2 });
    expect(q.pending(1)).toHaveLength(1);
    expect(q.pending(2)).toHaveLength(1);
    expect(notified).toBeGreaterThan(0);
  });

  it("повреждённое хранилище не ломает запуск", () => {
    const q = createQueue(memoryStorage("{не json"), async () => "sent");
    expect(q.pending()).toEqual([]);
  });

  it("создаёт идентификаторы нужной длины", () => {
    expect(newId()).toHaveLength(36);
    expect(newId()).not.toBe(newId());
  });
});
