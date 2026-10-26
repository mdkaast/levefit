import { useState } from "react";
import { t } from "../i18n";
import { Segmented } from "../ui/ui";
import { Admin } from "./Admin";
import { Profile } from "./Profile";

type Props = { isAdmin: boolean; onDeleted: () => void };

type View = "profile" | "admin";

/** Вкладка «Атлет»: персонаж и настройки; владельцу дополнительно доступна админ-панель. */
export function Athlete({ isAdmin, onDeleted }: Props) {
  const [view, setView] = useState<View>("profile");
  return (
    <>
      {isAdmin && (
        <div style={{ padding: "16px 16px 0", maxWidth: 560, margin: "0 auto" }}>
          <Segmented
            items={[
              { id: "profile" as const, label: t.nav.athlete },
              { id: "admin" as const, label: t.nav.admin },
            ]}
            value={view}
            onChange={setView}
          />
        </div>
      )}
      {view === "admin" && isAdmin ? <Admin /> : <Profile onDeleted={onDeleted} />}
    </>
  );
}
