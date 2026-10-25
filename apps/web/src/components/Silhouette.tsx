import { useState, type KeyboardEvent, type ReactNode } from "react";
import { t } from "../i18n";

type Muscle = "chest" | "back" | "shoulders" | "arms" | "legs" | "core";
type View = "front" | "back";

/** Контуры левой половины тела (x < 100); правая получается зеркальным отражением. */
type Shape = { fill: string[]; detail?: string[] };

const DELTOID = "M85 64 C70 62 55 66 48 82 C44 93 45 104 49 113 C56 110 62 106 66 102 C66 90 72 80 85 76 Z";
const ARMS: Shape = {
  fill: [
    "M49 115 C56 112 62 108 66 104 C69 124 66 144 62 160 L46 158 C46 142 46 128 49 115 Z",
    "M46 162 L62 164 C60 186 56 204 52 224 L40 218 C41 198 43 180 46 162 Z",
  ],
  detail: ["M55 126 C57 138 56 150 55 158", "M50 172 C50 190 47 204 45 214"],
};
const CALF = "M71 320 L93 320 C95 348 92 376 88 404 L75 404 C71 376 69 348 71 320 Z";

const SHAPES: Record<View, Partial<Record<Muscle, Shape>>> = {
  front: {
    shoulders: { fill: [DELTOID], detail: ["M52 90 C58 94 62 100 64 106"] },
    chest: {
      fill: ["M99 80 L86 78 C74 80 66 90 65 102 C66 116 80 125 99 124 Z"],
      detail: ["M69 112 C80 119 90 119 99 116", "M99 82 L99 124"],
    },
    arms: ARMS,
    core: {
      fill: [
        "M99 130 L84 130 C79 148 79 172 83 196 C89 204 95 206 99 206 Z",
        "M81 130 C73 146 72 170 76 192 L82 196 C79 172 79 148 83 130 Z",
      ],
      detail: ["M99 148 L84 148", "M99 166 L83 166", "M99 184 L84 184", "M99 128 L99 206"],
    },
    legs: {
      fill: [
        "M99 214 L72 212 C63 238 62 280 70 314 L94 314 C98 280 99 246 99 214 Z",
        CALF,
      ],
      detail: ["M85 222 C80 250 80 285 85 310", "M82 330 C84 350 83 372 82 392"],
    },
  },
  back: {
    shoulders: { fill: [DELTOID], detail: ["M52 90 C58 94 62 100 64 106"] },
    back: {
      fill: [
        "M99 56 L90 60 C84 66 82 74 86 82 L99 98 Z",
        "M99 100 L86 84 C74 90 66 104 68 124 C72 146 84 164 99 170 Z",
      ],
      detail: ["M99 56 L99 170", "M86 102 C82 122 84 142 91 156"],
    },
    arms: ARMS,
    core: {
      fill: ["M99 150 L86 152 C84 166 86 184 99 196 Z"],
      detail: ["M99 150 L99 196"],
    },
    legs: {
      fill: [
        "M99 196 L74 196 C64 206 64 226 74 234 C84 240 94 238 99 234 Z",
        "M99 240 L72 238 C64 262 64 292 70 314 L94 314 C98 290 99 262 99 240 Z",
        CALF,
      ],
      detail: ["M99 198 L99 236", "M85 246 C82 270 83 294 87 310", "M82 330 C84 350 83 372 82 392"],
    },
  },
};

const ORDER: Muscle[] = ["shoulders", "chest", "back", "arms", "core", "legs"];

function Mirrored({ children }: { children: ReactNode }) {
  return (
    <>
      {children}
      <g transform="translate(200 0) scale(-1 1)">{children}</g>
    </>
  );
}

type Props = { selected: string[]; onToggle: (muscle: string) => void };

export function Silhouette({ selected, onToggle }: Props) {
  const [view, setView] = useState<View>("front");
  const shapes = SHAPES[view];

  const keyHandler = (muscle: Muscle) => (event: KeyboardEvent) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onToggle(muscle);
    }
  };

  return (
    <div className="figure-box">
      <svg className="figure" viewBox="0 0 200 420" role="group" aria-label={t.onboarding.figureHint}>
        <defs>
          <linearGradient id="muscle-on" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#d9ff5c" />
            <stop offset="100%" stopColor="#8fd10a" />
          </linearGradient>
        </defs>

        <g className="static" key={`static-${view}`}>
          <ellipse cx="100" cy="30" rx="16" ry="21" />
          <path d="M92 50 L108 50 L111 66 L89 66 Z" />
          {view === "front" && <path d="M99 200 L78 196 C70 206 68 214 72 218 L99 220 Z" />}
          {view === "front" && <path d="M101 200 L122 196 C130 206 132 214 128 218 L101 220 Z" />}
          <path d="M36 224 C34 236 38 246 44 248 C50 246 52 236 52 226 Z" />
          <path d="M164 224 C166 236 162 246 156 248 C150 246 148 236 148 226 Z" />
          <path d="M74 404 L89 404 L92 416 L70 416 Z" />
          <path d="M126 404 L111 404 L108 416 L130 416 Z" />
        </g>

        <g className="muscles" key={view}>
          {ORDER.filter((m) => shapes[m]).map((muscle) => {
            const shape = shapes[muscle]!;
            const on = selected.includes(muscle);
            return (
              <g
                key={muscle}
                className={`muscle${on ? " on" : ""}`}
                role="button"
                tabIndex={0}
                aria-pressed={on}
                aria-label={t.onboarding.muscles[muscle]}
                onClick={() => onToggle(muscle)}
                onKeyDown={keyHandler(muscle)}
              >
                <Mirrored>
                  {shape.fill.map((d) => (
                    <path key={d} className="fill" d={d} />
                  ))}
                  {shape.detail?.map((d) => (
                    <path key={d} className="detail" d={d} />
                  ))}
                </Mirrored>
              </g>
            );
          })}
        </g>
      </svg>

      <div className="segments figure-switch">
        {(["front", "back"] as const).map((name) => (
          <button
            key={name}
            type="button"
            aria-pressed={view === name}
            onClick={() => setView(name)}
          >
            {name === "front" ? t.onboarding.viewFront : t.onboarding.viewBack}
          </button>
        ))}
      </div>
    </div>
  );
}
