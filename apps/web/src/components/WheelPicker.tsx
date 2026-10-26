import { useEffect, useRef } from "react";
import { haptic } from "../prefs";

const ITEM_H = 48; // высота строки, px; совпадает с --wheel-item в styles.css
const VISIBLE = 5; // сколько строк видно; центральная — выбранная
const REACH = 3; // на сколько строк от центра применяем анимацию

type Props = {
  label: string;
  min: number;
  max: number;
  value: number;
  unit?: string;
  onChange: (value: number) => void;
};

/** Колесо выбора числа: прокрутка с привязкой к строкам, соседние значения уменьшаются и тускнеют. */
export function WheelPicker({ label, min, max, value, unit, onChange }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const current = useRef(value);
  const frame = useRef(0);
  const range = useRef<number[]>([0, 0]);
  const count = max - min + 1;

  function animate(top: number) {
    const list = ref.current;
    if (!list) return;
    const centre = top / ITEM_H;
    const near = [Math.floor(centre) - REACH - 1, Math.ceil(centre) + REACH + 1];
    // Заодно пересчитываем прежний диапазон: строки, ушедшие из него, получают «дальний» вид.
    const from = Math.max(0, Math.min(near[0], range.current[0]));
    const to = Math.min(count - 1, Math.max(near[1], range.current[1]));
    range.current = near;
    for (let i = from; i <= to; i += 1) {
      const row = list.children[i] as HTMLElement | undefined;
      if (!row) continue;
      const d = Math.min(Math.abs(i - centre), REACH);
      row.style.transform = `perspective(240px) rotateX(${(i - centre) * -18}deg) scale(${1 - d * 0.1})`;
      row.style.opacity = String(Math.max(0.12, 1 - d * 0.32));
      row.dataset.active = d < 0.5 ? "true" : "false";
    }
  }

  function onScroll() {
    cancelAnimationFrame(frame.current);
    frame.current = requestAnimationFrame(() => {
      const list = ref.current;
      if (!list) return;
      animate(list.scrollTop);
      const index = Math.min(count - 1, Math.max(0, Math.round(list.scrollTop / ITEM_H)));
      const next = min + index;
      if (next !== current.current) {
        current.current = next;
        haptic("select");
        onChange(next);
      }
    });
  }

  // Ставим колесо на текущее значение при монтировании и при смене значения снаружи.
  useEffect(() => {
    const list = ref.current;
    if (!list) return;
    const target = (Math.min(max, Math.max(min, value)) - min) * ITEM_H;
    current.current = value;
    if (Math.abs(list.scrollTop - target) > 1) list.scrollTop = target;
    animate(target);
  }, [value, min, max]);

  useEffect(() => () => cancelAnimationFrame(frame.current), []);

  function onKey(event: React.KeyboardEvent) {
    const step = event.key === "ArrowUp" ? -1 : event.key === "ArrowDown" ? 1 : 0;
    if (!step) return;
    event.preventDefault();
    const next = Math.min(max, Math.max(min, value + step));
    ref.current?.scrollTo({ top: (next - min) * ITEM_H, behavior: "smooth" });
  }

  return (
    <div className="wheel" style={{ height: ITEM_H * VISIBLE }}>
      <div className="wheel-mark" aria-hidden="true" />
      <div
        ref={ref}
        className="wheel-list"
        role="spinbutton"
        tabIndex={0}
        aria-label={label}
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={value}
        onScroll={onScroll}
        onKeyDown={onKey}
      >
        {Array.from({ length: count }, (_, i) => (
          <div
            key={i}
            className="wheel-item"
            onClick={() =>
              ref.current?.scrollTo({ top: i * ITEM_H, behavior: "smooth" })
            }
          >
            {min + i}
          </div>
        ))}
      </div>
      {unit && <span className="wheel-unit">{unit}</span>}
    </div>
  );
}
