import { t } from "../i18n";
import { EmptyState } from "../ui/ui";

/** Вкладка «Питание». Дневник и рецепты — фаза 4 (флаг FLAGS.nutrition); пока заглушка. */
export function Nutrition() {
  return (
    <main>
      <h1>{t.nutrition.title}</h1>
      {/* Содержимое включается флагом FLAGS.nutrition в фазе 4 */}
      <EmptyState title={t.nutrition.soonTitle} text={t.nutrition.soonText} />
    </main>
  );
}
