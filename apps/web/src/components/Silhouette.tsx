/** Схематичная фигура: выбранные группы мышц подсвечиваются лаймом. */
export function Silhouette({ selected }: { selected: string[] }) {
  const on = (group: string) => (selected.includes(group) ? "on" : undefined);
  return (
    <svg className="silhouette" viewBox="0 0 100 220" width="100%" aria-hidden="true">
      <circle cx="50" cy="16" r="11" />
      <path className={on("shoulders")} d="M24 42c4-5 10-7 16-6v14H22zM76 42c-4-5-10-7-16-6v14h18z" />
      <path className={on("chest")} d="M41 38h18c3 0 5 3 5 6v18c0 3-3 5-6 5H42c-3 0-6-2-6-5V44c0-3 2-6 5-6z" />
      <path className={on("back")} d="M32 46v36c0 2 2 3 4 3V46zM68 46v36c0 2-2 3-4 3V46z" />
      <path className={on("core")} d="M40 70h20v38c0 3-2 5-5 5h-10c-3 0-5-2-5-5z" />
      <path className={on("arms")} d="M16 52h10l-2 56h-8zM84 52H74l2 56h8z" />
      <path className={on("legs")} d="M36 118h13l-2 92H36zM64 118H51l2 92h11z" />
    </svg>
  );
}
