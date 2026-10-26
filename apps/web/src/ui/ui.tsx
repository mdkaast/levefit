import { useEffect, useRef, useState, type ButtonHTMLAttributes, type ReactNode } from "react";
import { haptic, prefersReducedMotion } from "../prefs";

/** Единые компоненты интерфейса: токены берутся из CSS-переменных (`styles.css`). */

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "text";
  loading?: boolean;
};

export function Button({ variant = "primary", loading, disabled, className, onClick, ...rest }: ButtonProps) {
  return (
    <button
      type="button"
      {...rest}
      className={`ui-btn ${variant}${className ? ` ${className}` : ""}`}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      onClick={(event) => {
        haptic("light");
        onClick?.(event);
      }}
    />
  );
}

type ChipProps = {
  children: ReactNode;
  selected?: boolean;
  fit?: boolean; // «подходит вам»
  onClick?: () => void;
};

export function Chip({ children, selected, fit, onClick }: ChipProps) {
  const className = `ui-chip${selected ? " selected" : ""}${fit ? " fit" : ""}`;
  if (!onClick) return <span className={className}>{children}</span>;
  return (
    <button
      type="button"
      className={className}
      aria-pressed={selected}
      onClick={() => {
        haptic("select");
        onClick();
      }}
    >
      {children}
    </button>
  );
}

type SegmentedProps<T extends string> = {
  items: readonly { id: T; label: string }[];
  value: T;
  onChange: (id: T) => void;
};

export function Segmented<T extends string>({ items, value, onChange }: SegmentedProps<T>) {
  const index = Math.max(0, items.findIndex((item) => item.id === value));
  return (
    <div className="ui-seg" role="tablist" style={{ ["--n" as string]: items.length, ["--i" as string]: index }}>
      <i aria-hidden="true" />
      {items.map((item) => (
        <button
          key={item.id}
          type="button"
          role="tab"
          aria-selected={item.id === value}
          onClick={() => {
            haptic("select");
            onChange(item.id);
          }}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}

export function Card({ children, accent }: { children: ReactNode; accent?: boolean }) {
  return <div className={`ui-card${accent ? " accent" : ""}`}>{children}</div>;
}

type RowProps = { title: string; hint?: string; trailing?: ReactNode; onClick?: () => void };

/** Строка списка с шевроном (если есть действие). */
export function ListRow({ title, hint, trailing, onClick }: RowProps) {
  const body = (
    <>
      <span className="grow">
        <b>{title}</b>
        {hint && <small>{hint}</small>}
      </span>
      {trailing}
      {onClick && <span className="chev" aria-hidden="true">›</span>}
    </>
  );
  return onClick ? (
    <button type="button" className="ui-row" onClick={onClick}>
      {body}
    </button>
  ) : (
    <div className="ui-row">{body}</div>
  );
}

type StepperProps = {
  value: number;
  min: number;
  max: number;
  step?: number;
  format?: (value: number) => string;
  label: string;
  onChange: (value: number) => void;
};

/** Шаговый счётчик «− значение +» с коротким «отскоком» значения. */
export function Stepper({ value, min, max, step = 1, format, label, onChange }: StepperProps) {
  const [bump, setBump] = useState(0);
  const change = (delta: number) => {
    const next = Math.min(max, Math.max(min, Math.round((value + delta) * 100) / 100));
    if (next === value) return;
    haptic("light");
    setBump((n) => n + 1);
    onChange(next);
  };
  return (
    <div className="ui-stepper" role="group" aria-label={label}>
      <button type="button" aria-label={`${label}: −`} disabled={value <= min} onClick={() => change(-step)}>
        −
      </button>
      <output key={bump} className="num bump">
        {format ? format(value) : value}
      </output>
      <button type="button" aria-label={`${label}: +`} disabled={value >= max} onClick={() => change(step)}>
        +
      </button>
    </div>
  );
}

/** Число, плавно «докручивающееся» до нового значения; при «меньше движения» меняется сразу. */
export function useCountUp(target: number, duration = 700): number {
  const [shown, setShown] = useState(prefersReducedMotion() ? target : 0);
  const from = useRef(shown);
  useEffect(() => {
    if (prefersReducedMotion()) {
      setShown(target);
      return;
    }
    const start = performance.now();
    const origin = from.current;
    let frame = 0;
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      const value = origin + (target - origin) * eased;
      from.current = value;
      setShown(value);
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);
  return shown;
}

export function ProgressBar({ value, label }: { value: number; label?: string }) {
  const percent = Math.round(Math.min(1, Math.max(0, value)) * 100);
  return (
    <div className="ui-bar" role="progressbar" aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100} aria-label={label}>
      <i style={{ width: `${percent}%` }} />
    </div>
  );
}

type RingProps = { value: number; size?: number; label: string; children?: ReactNode };

/** Кольцо прогресса: дуга заполняется по кругу, значение 0..1. */
export function ProgressRing({ value, size = 96, label, children }: RingProps) {
  const stroke = 8;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const v = Math.min(1, Math.max(0, value));
  return (
    <div className="ui-ring" style={{ width: size, height: size }} role="img" aria-label={label}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} className="track" strokeWidth={stroke} fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          className="arc"
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - v)}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <span className="num">{children}</span>
    </div>
  );
}

export function Tag({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "fit" | "info" }) {
  return <span className={`ui-tag ${tone}`}>{children}</span>;
}

/** Блок-подсказка с иконкой «i». */
export function Hint({ children }: { children: ReactNode }) {
  return (
    <p className="ui-hint">
      <span aria-hidden="true">i</span>
      <span>{children}</span>
    </p>
  );
}

export function EmptyState({ title, text, action }: { title: string; text: string; action?: ReactNode }) {
  return (
    <div className="ui-empty">
      <b>{title}</b>
      <p>{text}</p>
      {action}
    </div>
  );
}

export function Skeleton({ height = 16, width = "100%" }: { height?: number; width?: number | string }) {
  return <div className="ui-skel" style={{ height, width }} aria-hidden="true" />;
}
