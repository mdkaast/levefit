/** Неоновый «скелет» бегуна для приветственного экрана (как трекинг тела в референсе). */
const JOINTS: [number, number][] = [
  [118, 38], // голова
  [112, 66], // шея
  [88, 78], // левое плечо
  [140, 74], // правое плечо
  [64, 110], // левый локоть
  [166, 98], // правый локоть
  [44, 142], // левая кисть
  [190, 70], // правая кисть
  [108, 142], // таз
  [78, 194], // левое колено
  [150, 188], // правое колено
  [52, 252], // левая стопа
  [196, 232], // правая стопа
];

const BONES: [number, number][] = [
  [0, 1], [1, 2], [1, 3], [2, 4], [4, 6], [3, 5], [5, 7],
  [1, 8], [2, 8], [3, 8], [8, 9], [8, 10], [9, 11], [10, 12],
];

export function NeonAthlete() {
  return (
    <svg viewBox="0 0 240 280" width="100%" role="img" aria-label="Фигура атлета">
      <defs>
        <linearGradient id="bone" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#b9ff1c" />
          <stop offset="100%" stopColor="#ff3d9a" />
        </linearGradient>
        <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="3" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <g filter="url(#glow)" stroke="url(#bone)" strokeWidth="3" strokeLinecap="round">
        {BONES.map(([a, b]) => (
          <line
            key={`${a}-${b}`}
            x1={JOINTS[a][0]}
            y1={JOINTS[a][1]}
            x2={JOINTS[b][0]}
            y2={JOINTS[b][1]}
          />
        ))}
      </g>
      <g filter="url(#glow)">
        {JOINTS.map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r={i === 0 ? 14 : 6} fill={i === 0 ? "none" : "#b9ff1c"} stroke="#b9ff1c" strokeWidth={i === 0 ? 3 : 0} />
        ))}
      </g>
    </svg>
  );
}
