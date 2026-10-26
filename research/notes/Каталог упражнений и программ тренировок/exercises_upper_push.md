# Каталог упражнений: жимы верхней частью тела (горизонтальный/вертикальный жим, изоляция груди и плеч, трицепс)

Контекст: seed-база для русскоязычного Telegram Mini App (rule-based decision engine: двойная прогрессия, шаг веса округляется до доступного оборудования; LLM только объясняет). Дата: октябрь 2026. Подсказки (cues) и ошибки сформулированы своими словами, дословного копирования нет. Флаги безопасности носят информационный характер и не являются медицинскими рекомендациями.

---

## 1. Каталог записей (цель: 70–100 упражнений и вариантов)

### Takeaway
Ниже 92 структурированные записи: horizontal_push 36, vertical_push 19, chest_isolation 10, shoulder_isolation 9, elbow_extension 18. Научная база, использованная для разметки (углы наклона, ширина хвата, трицепс над головой, махи на блоке и с гантелями), приведена в Cited Findings. Сами записи (подсказки, ошибки, замены, шаги веса) составлены как синтез общепринятой тренерской практики. По каждой записи отдельного источника нет, поэтому весь каталог помещён в Inferences.

### Cited Findings
- Угол скамьи (30 тренированных, 60% 1ПМ, ЭМГ): активность верхней (ключичной) части большой грудной максимальна при наклоне 30°. Средняя и нижняя части наиболее активны при 0° и затихают с ростом наклона. Передняя дельта максимальна при 45–60°. Медиальная головка трицепса держится около 15% MVIC и не зависит от угла. Вывод авторов: при наклоне больше 45° работа смещается на переднюю дельту, 30° оптимален для верха груди (Rodríguez-Ridao et al., 2020, IJERPH 17(19):7339) — [PMC7579505](https://pmc.ncbi.nlm.nih.gov/articles/PMC7579505/)
- Ширина хвата: в среднем 1ПМ широким хватом на 5–6% выше, чем узким. В «мёртвой точке» при широком хвате грудь и плечо дают около 78% усилия, трицепс около 22%; при узком соотношение около 63/37. Хваты в исследовании: узкий 1,0, средний 1,4, широкий 1,7 ширины плеч (биакромиальной); официальных определений нет (Larsen et al., 2020) — [StrengthLog](https://www.strengthlog.com/wide-vs-close-grip-bench-press-strength-ratio-muscles-worked/)
- Нагрузка на плечо в жиме лёжа (10 опытных атлетов, 21 вариант жима, 2024): более узкий хват и сведённые лопатки в целом снижают риск. В обзоре упомянуто, что узкий хват может снижать риск остеолиза дистального конца ключицы и разрывов вращательной манжеты — [Physio-network review](https://physio-network.com/review/effects-of-bench-press-technique-variations-on-musculoskeletal-shoulder-loads-and-potential-injury-risk); оригинал: [PMC11224528](https://pmc.ncbi.nlm.nih.gov/articles/PMC11224528) (полный текст за капчей, подробности про прогиб и траекторию грифа не проверены)
- Трицепс: разгибание над головой на блоке против разгибания на блоке вниз (21 человек, по одному упражнению на каждую руку, 5×10, 2 раза в неделю, 12 недель). Общий прирост трицепса при разгибании над головой примерно в 1,4 раза больше. Предполагаемый механизм — тренировка длинной головки в растянутом положении (Maeo et al., 2022/2023, Eur J Sport Sci) — [BarBend](https://barbend.com/overhead-triceps-extensions-vs-pushdowns-muscle-growth-study); [PubMed 35819335](https://pubmed.ncbi.nlm.nih.gov/35819335/)
- Махи с гантелями против махов на нижнем блоке (24 тренированных, по одному варианту на каждую руку, 8 недель, 12–16 повторений до отказа). Прирост толщины средней дельты одинаковый, около 3,3–4,6%; байесовский анализ поддерживает отсутствие разницы (Larsen et al., 2025, Front Physiol) — [Frontiers](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2025.1611468/full)
- «Хаммер» на русском жаргоне — рычажный тренажёр с навесными блинами (по бренду Hammer Strength). Есть варианты горизонтального и наклонного жима. Фиксированная траектория стабилизирует плечо, поэтому его рекомендуют после травм плеча или спины. Локти около 45° к корпусу — [Лайфхакер](https://lifehacker.ru/zhim-v-xammere/amp/)
- Французский жим: общее название разгибаний с опусканием веса за голову или ко лбу. Вариант лёжа называют «дробитель черепов». Выполняется лёжа, сидя, стоя, со штангой, EZ-грифом, гантелями, на блоке. Типичные ошибки: локти «гуляют» и разводятся, сокращённая амплитуда, движение головой. При боли в локте упражнение прекращают; EZ-гриф может нагружать запястье — [Skillbox](https://skillbox.ru/media/health/french-press/)

### Inferences

#### 1.0. Словарь полей (рекомендуемые enum'ы)
- `movement_pattern`: horizontal_push | vertical_push | chest_isolation | shoulder_isolation | elbow_extension
- `muscles`: chest_mid (грудная, грудинная часть), chest_upper (ключичная), chest_lower, front_delt, side_delt, triceps (все головки), triceps_long, serratus (передняя зубчатая), upper_traps, core, rotator_cuff
- `equipment`: barbell, ez_bar, dumbbell, kettlebell, bench (flat/incline/decline), smith, machine_stack (блочный тренажёр), plate_loaded (рычажный, «Хаммер»), cable, band, bodyweight, dip_bars, rings_trx, landmine, assist_machine (гравитрон)
- `level`: beginner | intermediate | advanced
- `load_type` и шаг по умолчанию (движок округляет к профилю оборудования пользователя):
  - **BB** (штанга): +2,5 кг суммарно (по 1,25 кг на сторону); при наличии фракционных блинов +1 кг; при отсутствии 1,25-кг блинов +5 кг.
  - **EZ**: как штанга, но стартовый вес грифа обычно 7–10 кг (уточнять у пользователя).
  - **DB** (гантели): в зале шаг обычно 2 или 2,5 кг на гантель (ряды 10-12-14 или 10-12,5-15). Разборные дома: 0,5–1 кг на руку. На малых весах относительный скачок большой, поэтому для изоляции нужна прогрессия повторениями.
  - **KB** (гиря): шаг 4 кг (8-12-16-20-24), очень грубый, поэтому прогрессия повторениями и подходами.
  - **STACK** (блочный тренажёр или блок): шаг стека 5–10 кг (часто 5 или 7 кг); у блока полиспаст делит вес, поэтому килограммы на разных станках несопоставимы. Хранить вес per-machine.
  - **PLATE** (рычажный): +5 кг (по 2,5 на сторону) или +2,5 кг на одну сторону для одной руки.
  - **SMITH**: как штанга, но вес грифа 0–15 кг в зависимости от противовеса; e1RM несопоставим со свободной штангой.
  - **BW** (вес тела): лестница — повторения, затем темп или пауза, затем рычаг (изменение угла), затем отягощение +2,5–5 кг (пояс, рюкзак, жилет).
  - **BW+**: вес тела плюс добавленный вес, учитывать добавленный (и при желании массу тела для e1RM).
  - **ASSIST**: гравитрон, прогресс за счёт уменьшения помощи (−5 кг стека).
  - **BAND**: дискретные цвета резин, прогресс повторениями или более тяжёлой резиной; e1RM не считается.
- `reps` по умолчанию: S = сила, H = гипертрофия, E = выносливость. «—» значит, что цель не рекомендуется.
- `e1RM`: Y означает, что упражнение подходит для расчёта e1RM и трекинга прогрессии (стабильная техника, повторения ≤10–12). L — трекинг только по повторениям и тоннажу. N — e1RM не считается.
- Флаги: SH = боль в плече импинджмент-типа или передняя капсула, EL = локоть, WR = запястье. Значения: low / med / high.

#### 1.1. HORIZONTAL_PUSH — штанга и Смит

**1. barbell_bench_press — Жим штанги лёжа («Жим лёжа»)**
- en: Barbell Bench Press; aliases: жим лёжа, жим штанги лёжа на горизонтальной скамье, «жим»
- pattern: horizontal_push | compound | bilateral | beginner→advanced | eq: barbell, flat bench, стойки
- prim: chest_mid, front_delt, triceps; sec: chest_upper, serratus
- load BB, +2,5 кг | reps S 3–6, H 6–12, E 12–20
- cues: лопатки сведены и опущены, ноги в пол; хват такой, чтобы предплечья в нижней точке были вертикальны; опускать гриф к низу груди, локти под углом 45–70° к корпусу; выжимать вверх и немного назад к плечам
- errors: локти под 90° (буквой «Т»); отбив от груди; таз отрывается от скамьи
- regr: dumbbell_bench_press, machine_chest_press, push_up | progr: paused_bench_press, увеличение веса
- subs: noBB → dumbbell_bench_press; DB_home → dumbbell_floor_press / dumbbell_bench_press; BW → push_up / decline_push_up; shoulder → neutral_grip_dumbbell_press, floor_press_barbell, machine_chest_press; elbow/wrist → neutral_grip_dumbbell_press, machine_chest_press
- flags: SH med, EL low, WR med (запястье «заваливается» назад) | e1RM Y (опорный лифт)

**2. barbell_incline_bench_press — Жим штанги на наклонной скамье**
- en: Incline Barbell Bench Press; aliases: жим под углом, наклонный жим штанги
- pattern: horizontal_push (в части баз помечается как chest/upper) | compound | bilateral | intermediate | eq: barbell, incline bench 30–45°
- prim: chest_upper, front_delt; sec: triceps, chest_mid
- load BB +2,5 | reps S 3–6, H 6–12, E 12–15
- cues: наклон около 30° (при 45° и больше нагрузка смещается на дельты); касание под ключицами; лопатки прижаты
- errors: слишком крутой угол; чрезмерный прогиб превращает упражнение в горизонтальный жим
- regr: incline_dumbbell_press, incline_machine_press | progr: вес, пауза
- subs: noBB → incline_dumbbell_press; DB_home → incline_dumbbell_press (или floor press с подъёмом таза — неточно); BW → decline_push_up; shoulder → incline_machine_press, neutral-хват гантелей на наклоне; elbow/wrist → incline_machine_press
- flags: SH med, WR med | e1RM Y (отдельно от плоского жима)

**3. barbell_decline_bench_press — Жим штанги на скамье с отрицательным наклоном**
- en: Decline Barbell Bench Press; aliases: жим лёжа головой вниз, жим на скамье с обратным наклоном (термин неоднозначен: «обратный наклон» иногда путают с положительным)
- pattern: horizontal_push | compound | bilateral | intermediate | eq: barbell, decline bench, лучше со страховкой
- prim: chest_mid, chest_lower; sec: triceps, front_delt
- load BB +2,5 | reps S 3–6, H 6–12, E 12–15
- cues: ноги надёжно зафиксированы валиками; опускать гриф к низу груди; снимать гриф со стоек со страховкой
- errors: опускание к шее; снятие грифа без страховки
- regr: decline_dumbbell_press, chest_dip | progr: вес
- subs: noBB → decline_dumbbell_press; DB_home → dumbbell_floor_press; BW → chest_dip / push_up; shoulder → machine_chest_press; elbow/wrist → machine_chest_press
- flags: SH low-med, WR med; кровь приливает к голове, осторожно при давлении | e1RM Y

**4. close_grip_bench_press — Жим лёжа узким хватом**
- en: Close-Grip Bench Press; aliases: жим узким хватом, ЖУХ (жаргон)
- pattern: horizontal_push (в справочниках часто числится как упражнение на трицепс) | compound | bilateral | intermediate | eq: barbell
- prim: triceps, chest_mid; sec: front_delt
- load BB +2,5 | reps S 4–6, H 6–12, E 12–15
- cues: хват примерно на ширине плеч (не уже); локти ближе к корпусу; касание чуть ниже, чем в классическом жиме
- errors: слишком узкий хват (руки касаются друг друга), что перегружает запястья; локти разводятся
- regr: dumbbell squeeze_press, diamond_push_up | progr: вес, пауза
- subs: noBB → squeeze_press; DB_home → squeeze_press; BW → diamond_push_up; shoulder → machine_dip / pushdown; elbow/wrist → neutral_grip_dumbbell_press
- flags: SH low, EL med, WR med-high | e1RM Y

**5. paused_bench_press — Жим лёжа с паузой на груди**
- en: Paused Bench Press; aliases: жим с паузой, соревновательный жим (условно)
- pattern: horizontal_push | compound | bilateral | intermediate | eq: barbell
- prim/sec: как у №1
- load BB +2,5 | reps S 1–5, H 4–8, E —
- cues: пауза 1–2 секунды на груди без расслабления; напряжённое тело; жать без отбива
- errors: «утопить» гриф в груди и расслабиться; пауза не выдерживается
- regr: barbell_bench_press | progr: длиннее пауза, вес
- subs: см. №1
- flags: как у №1 | e1RM Y (на 3–8% ниже, чем у обычного жима; хранить отдельно — оценка, без источника)

**6. floor_press_barbell — Жим штанги лёжа с пола**
- en: Barbell Floor Press; aliases: жим с пола
- pattern: horizontal_push | compound | bilateral | intermediate | eq: barbell, силовая рама или ассистент
- prim: triceps, chest_mid; sec: front_delt
- load BB +2,5 | reps S 3–6, H 6–10, E —
- cues: опускать штангу, пока трицепс мягко не коснётся пола; пауза; жать без отбива локтями
- errors: удар локтями об пол; неудобный съём штанги без стоек
- regr: dumbbell_floor_press | progr: вес
- subs: noBB/DB_home → dumbbell_floor_press; BW → push_up; shoulder → это само по себе вариант «щадящей» амплитуды; elbow/wrist → neutral DB floor press
- flags: SH low (ограниченная амплитуда), EL med | e1RM Y

**7. smith_bench_press — Жим лёжа в тренажёре Смита**
- en: Smith Machine Bench Press; aliases: жим в Смите, жим в машине Смита
- pattern: horizontal_push | compound | bilateral | beginner | eq: smith, flat bench
- prim: chest_mid, front_delt, triceps; sec: chest_upper
- load SMITH (+2,5) | reps S 4–6, H 6–12, E 12–20
- cues: поставить скамью так, чтобы гриф опускался на низ груди; лопатки сведены; использовать стопоры
- errors: скамья смещена, гриф идёт к шее; полная опора на крюки, без контроля
- regr: machine_chest_press | progr: barbell_bench_press
- subs: noBB → dumbbell_bench_press; остальные как у №1
- flags: SH med (фиксированная траектория может не подходить индивидуально) | e1RM Y (отдельная шкала)

**8. smith_incline_bench_press — Жим на наклонной скамье в Смите**
- en: Smith Machine Incline Press; aliases: наклонный жим в Смите
- pattern: horizontal_push | compound | bilateral | beginner | eq: smith, incline bench
- prim: chest_upper, front_delt; sec: triceps
- load SMITH | reps S 4–6, H 6–12, E 12–15
- cues: угол 30°; касание под ключицами; стопоры на безопасной высоте
- errors: угол 45° и больше превращает упражнение в жим на плечи
- regr: incline_machine_press | progr: barbell_incline_bench_press
- subs: как у №2
- flags: SH med | e1RM Y

#### 1.2. HORIZONTAL_PUSH — гантели

**9. dumbbell_bench_press — Жим гантелей лёжа**
- en: Dumbbell Bench Press; aliases: жим гантелей на горизонтальной скамье
- pattern: horizontal_push | compound | bilateral | beginner | eq: dumbbells, flat bench
- prim: chest_mid, front_delt, triceps; sec: chest_upper, serratus
- load DB (+1–2,5 кг на руку) | reps S 5–8, H 6–15, E 15–20
- cues: укладывать гантели на скамью через колени; локти под 45–60°; опускать до лёгкого растяжения груди; вверху гантели не бить друг о друга
- errors: вес не позволяет безопасно уложиться и встать; гантели «разваливаются» в стороны
- regr: machine_chest_press, push_up | progr: barbell_bench_press, вес
- subs: noBB → это и есть замена; DB_home → dumbbell_floor_press, если нет скамьи; BW → push_up; shoulder → neutral_grip_dumbbell_press; elbow/wrist → neutral_grip_dumbbell_press
- flags: SH med-low, WR low | e1RM Y (при весе гантели ≥ ~10 кг; шаги грубые)

**10. incline_dumbbell_press — Жим гантелей на наклонной скамье**
- en: Incline Dumbbell Press; aliases: жим гантелей под углом
- pattern: horizontal_push | compound | bilateral | beginner | eq: dumbbells, incline bench
- prim: chest_upper, front_delt; sec: triceps
- load DB | reps S 5–8, H 6–15, E 15–20
- cues: 15–30°; лопатки прижаты; опускать к уровню верха груди; локти под гантелями
- errors: угол слишком крутой; укороченная амплитуда
- regr: incline_machine_press, incline_push_up (не путать: это лёгкие отжимания) | progr: barbell_incline_bench_press
- subs: noBB → это и есть замена; DB_home → при наличии регулируемой скамьи; иначе dumbbell_floor_press с подложкой под спину (неточно); BW → decline_push_up; shoulder → neutral-хват на наклоне; elbow/wrist → incline_machine_press
- flags: SH med-low | e1RM Y

**11. decline_dumbbell_press — Жим гантелей на скамье с отрицательным наклоном**
- en: Decline Dumbbell Press; aliases: жим гантелей головой вниз
- pattern: horizontal_push | compound | bilateral | intermediate | eq: dumbbells, decline bench
- prim: chest_lower, chest_mid; sec: triceps
- load DB | reps H 8–15, E 15–20; S —
- cues: надёжно зафиксировать ноги; брать и опускать гантели с помощью партнёра или аккуратно; локти 45°
- errors: неконтролируемый «сброс» гантелей в нижней точке
- regr: dumbbell_bench_press | progr: weighted_dip
- subs: BW → chest_dip; остальное как у №9
- flags: SH low, давление в голове | e1RM L

**12. neutral_grip_dumbbell_press — Жим гантелей нейтральным хватом лёжа**
- en: Neutral-Grip Dumbbell Press (Hammer-grip DB press); aliases: жим гантелей молотковым хватом, параллельным хватом
- pattern: horizontal_push | compound | bilateral | beginner | eq: dumbbells, bench
- prim: chest_mid, triceps; sec: front_delt
- load DB | reps S 5–8, H 8–15, E 15–20
- cues: ладони смотрят друг на друга; локти ближе к корпусу (около 30–45°); опускать к нижней части груди
- errors: локти разводятся, хват «плывёт» в пронацию
- regr: machine_chest_press | progr: вес; close_grip_bench_press
- subs: основная «щадящая» замена для SH/EL/WR в жимах лёжа
- flags: SH low, EL low, WR low | e1RM Y

**13. single_arm_dumbbell_bench_press — Жим гантели одной рукой лёжа**
- en: Single-Arm Dumbbell Bench Press; aliases: однорукий жим гантели
- pattern: horizontal_push | compound | unilateral | intermediate | eq: dumbbell, bench
- prim: chest_mid, front_delt, triceps; sec: core (антиротация)
- load DB | reps H 8–12, E 12–20; S —
- cues: свободной рукой держаться за скамью; таз не разворачивается; амплитуда как в парном жиме
- errors: корпус скатывается к рабочей руке
- regr: dumbbell_bench_press | progr: вес
- subs: home: полезно при одной гантели
- flags: SH med-low | e1RM L (вес на руку)

**14. dumbbell_floor_press — Жим гантелей лёжа на полу**
- en: Dumbbell Floor Press; aliases: жим гантелей с пола
- pattern: horizontal_push | compound | bilateral | beginner | eq: dumbbells (скамья не нужна)
- prim: chest_mid, triceps; sec: front_delt
- load DB | reps S 5–8, H 8–15, E 15–20
- cues: колени согнуты; локти под 45° мягко касаются пола; без отбива
- errors: удар локтями; разведённые на 90° локти
- regr: push_up из удобного положения | progr: dumbbell_bench_press
- subs: ключевая «домашняя» замена жима лёжа без скамьи; shoulder: укороченная амплитуда
- flags: SH low, EL med-low | e1RM Y

**15. squeeze_press — Жим гантелей сведёнными (с прижатыми гантелями)**
- en: Dumbbell Squeeze Press (Crush Press); aliases: жим гантелей, сжатых вместе (название неустоявшееся, отметить как uncertain)
- pattern: horizontal_push | compound | bilateral | beginner | eq: dumbbells, bench или пол
- prim: chest_mid, triceps; sec: front_delt
- load DB (вес заметно ниже, чем в обычном жиме) | reps H 8–15, E 15–20; S —
- cues: гантели сжаты друг с другом всё время; нейтральный хват; опускать к низу груди
- errors: гантели расходятся
- regr: diamond_push_up (по смыслу) | progr: close_grip_bench_press
- subs: замена узкого жима без штанги
- flags: SH low, WR low | e1RM L

#### 1.3. HORIZONTAL_PUSH — тренажёры, блоки, резина

**16. machine_chest_press — Жим от груди в тренажёре сидя**
- en: Machine Chest Press (Seated Chest Press); aliases: жим в тренажёре от груди, жим сидя в рычажном/блочном тренажёре
- pattern: horizontal_push | compound | bilateral | beginner | eq: machine_stack
- prim: chest_mid, front_delt, triceps; sec: chest_upper
- load STACK (5–7 кг шаг) | reps S 6–8, H 8–15, E 15–25
- cues: рукояти на уровне середины груди; лопатки прижаты к спинке; плавный негатив; не «замыкать» локти рывком
- errors: сиденье слишком низко или высоко (рукояти у шеи или у живота); плечи выходят вперёд
- regr: — (стартовое упражнение) | progr: dumbbell_bench_press, barbell_bench_press
- subs: замена для SH/EL/WR при болях; home → band_chest_press / push_up
- flags: SH low, EL low, WR low | e1RM L (зависит от станка)

**17. hammer_chest_press — Жим в «Хаммере» (рычажный тренажёр, горизонтальный)**
- en: Plate-Loaded Chest Press (Hammer Strength Chest Press); aliases: Хаммер, жим в хаммере, рычажный жим
- pattern: horizontal_push | compound | bilateral или unilateral (раздельные рычаги) | beginner | eq: plate_loaded
- prim: chest_mid, front_delt, triceps
- load PLATE (+5 кг пара, +2,5 кг на одну сторону) | reps S 5–8, H 8–12, E 12–20
- cues: сиденье выставить так, чтобы ручки были на уровне груди; локти около 45°; спина прижата
- errors: не дожимать одну сторону (рычаги независимы); бросать вес в негативе
- regr: machine_chest_press | progr: barbell_bench_press
- subs: как у №16
- flags: SH low | e1RM L
- note: «Хаммер» — жаргон по бренду Hammer Strength, распространяется на аналоги ([Лайфхакер](https://lifehacker.ru/zhim-v-xammere/amp/))

**18. incline_machine_press — Жим вверх в тренажёре или Хаммере (наклонный)**
- en: Incline Machine Press (Plate-Loaded Incline Press); aliases: наклонный Хаммер, жим в тренажёре под углом
- pattern: horizontal_push | compound | bilateral | beginner | eq: machine_stack / plate_loaded
- prim: chest_upper, front_delt; sec: triceps
- load STACK/PLATE | reps H 8–15, E 15–20; S 6–8
- cues: рукояти на уровне верха груди; локти под рукоятями; не отрывать поясницу
- errors: высокое сиденье превращает упражнение в жим на плечи
- regr: — | progr: incline_dumbbell_press
- subs: замена наклонного жима при SH/WR
- flags: SH low-med | e1RM L

**19. cable_chest_press — Жим от груди на блоках стоя**
- en: Standing Cable Chest Press; aliases: жим в кроссовере стоя, жим с блоков
- pattern: horizontal_push | compound | bilateral (или поочерёдно) | intermediate | eq: cable (кроссовер)
- prim: chest_mid, front_delt, triceps; sec: core
- load STACK (шаг блока 2,5–5 кг) | reps H 10–15, E 15–25; S —
- cues: шаг вперёд, разножка; корпус слегка наклонён; жать по траектории перед грудью, руки сходятся
- errors: корпус «уезжает» назад за тросами; поясница прогибается
- regr: machine_chest_press | progr: single-arm вариант
- subs: home → band_chest_press
- flags: SH low | e1RM N/L (стабильность ограничивает)

**20. band_chest_press — Жим от груди с резиной (эспандером)**
- en: Resistance Band Chest Press; aliases: жим с резиной стоя, жим эспандера от груди
- pattern: horizontal_push | compound | bilateral | beginner | eq: band (закреплена сзади)
- prim: chest_mid, triceps; sec: front_delt
- load BAND | reps H 12–20, E 20–30
- cues: резина на уровне груди за спиной; разножка; полный выжим без «откидывания» назад
- errors: слабая резина, амплитуда в «мёртвой зоне»
- regr: incline_push_up | progr: более тяжёлая резина, push_up
- subs: домашняя замена машины или кроссовера
- flags: SH low | e1RM N

#### 1.4. HORIZONTAL_PUSH — отжимания (вес тела)

**21. push_up — Отжимания от пола**
- en: Push-Up; aliases: отжимания, отжимания классические, упор лёжа — сгибание-разгибание рук (школьная формулировка)
- pattern: horizontal_push | compound | bilateral | beginner | eq: bodyweight
- prim: chest_mid, triceps, front_delt; sec: serratus, core
- load BW (повторения → темп/пауза → дефицит → отягощение) | reps S (weighted 5–8), H 8–20 (близко к отказу), E 20–50
- cues: тело прямое, ягодицы и пресс напряжены; кисти чуть шире плеч, локти под 30–45° назад; грудь почти касается пола
- errors: провисает поясница или задирается таз; голова «клюёт» вниз; укороченная амплитуда
- regr: incline_push_up, knee_push_up, wall_push_up | progr: decline_push_up, deficit_push_up, weighted_push_up, archer_push_up
- subs: shoulder → incline_push_up, упоры или гантели вместо ладоней (нейтральный хват); wrist → отжимания на кулаках, на упорах или гантелях
- flags: SH low, WR med (разгибание кисти) | e1RM N (L: повторения; при отягощении можно Y)

**22. incline_push_up — Отжимания с упором руками на возвышение**
- en: Incline Push-Up; aliases: отжимания от скамьи, от стола, от опоры
- pattern: horizontal_push | compound | bilateral | beginner | eq: bodyweight + опора
- prim: chest_mid (ниже доля), triceps; sec: front_delt
- load BW: прогресс — снижать высоту опоры | reps H 8–20, E 20–40
- cues: тело прямое; опора на уровне груди или ниже по мере прогресса; касаться опоры грудью
- errors: таз отстаёт от корпуса
- regr: wall_push_up | progr: knee_push_up / push_up
- flags: SH low, WR med-low | e1RM N

**23. knee_push_up — Отжимания с колен**
- en: Kneeling Push-Up; aliases: «женские» отжимания (устаревший ярлык, в приложении не использовать)
- pattern: horizontal_push | compound | bilateral | beginner | eq: bodyweight
- prim: chest_mid, triceps | load BW | reps H 8–20, E 20–30
- cues: прямая линия от колен до головы; таз не сгибать
- errors: «складывание» в тазобедренных
- regr: wall_push_up | progr: push_up
- flags: WR med-low | e1RM N
- note: часть тренеров предпочитает incline_push_up как более полезную регрессию (без источника)

**24. wall_push_up — Отжимания от стены**
- en: Wall Push-Up; aliases: отжимания стоя от стены
- pattern: horizontal_push | compound | bilateral | beginner (вернувшиеся, реабилитация) | eq: bodyweight
- prim: chest_mid, triceps | load BW | reps H 12–20, E 20–40
- cues: чем дальше стопы от стены, тем сложнее; локти 45°
- errors: голова «тянется» к стене раньше груди
- progr: incline_push_up | flags: low | e1RM N

**25. decline_push_up — Отжимания с ногами на возвышении**
- en: Decline Push-Up (Feet-Elevated); aliases: отжимания ноги на скамье
- pattern: horizontal_push | compound | bilateral | intermediate | eq: bodyweight + опора
- prim: chest_upper, front_delt, triceps; sec: core
- load BW: прогресс — повышать опору | reps H 6–20, E 20–40
- cues: корпус не проваливается; стопы на высоте скамьи; амплитуда полная
- errors: поясница провисает; голова тянется вперёд
- regr: push_up | progr: weighted_push_up, pike_push_up (вертикаль)
- note: самая близкая замена жима на наклонной скамье без снарядов
- flags: SH med-low, WR med | e1RM N

**26. diamond_push_up — Отжимания узким упором («алмаз»)**
- en: Diamond / Close-Grip Push-Up; aliases: узкие отжимания, отжимания на трицепс, «алмазные» отжимания
- pattern: horizontal_push (в базах часто triceps) | compound | bilateral | intermediate | eq: bodyweight
- prim: triceps, chest_mid; sec: front_delt
- load BW | reps H 6–15, E 15–30
- cues: ладони под грудью (не обязательно «ромбом» — достаточно ширины плеч); локти идут назад вдоль корпуса
- errors: локти разводятся в стороны; кисть перегружена
- regr: узкие отжимания от опоры | progr: weighted diamond, archer
- subs: wrist → узкие отжимания на гантелях (нейтральный хват)
- flags: WR high, EL med | e1RM N

**27. wide_push_up — Отжимания широкой постановкой рук**
- en: Wide-Grip Push-Up; aliases: широкие отжимания
- pattern: horizontal_push | compound | bilateral | beginner | eq: bodyweight
- prim: chest_mid; sec: front_delt, triceps
- load BW | reps H 8–20, E 20–40
- cues: кисти примерно в 1,5 раза шире плеч; не опускаться ниже комфортной глубины
- errors: локти под 90° (плечи вверх к ушам)
- flags: SH med | e1RM N
- note: ценность как отдельной записи спорна (низкий приоритет)

**28. weighted_push_up — Отжимания с отягощением**
- en: Weighted Push-Up; aliases: отжимания с блином на спине, с рюкзаком, в жилете
- pattern: horizontal_push | compound | bilateral | intermediate | eq: bodyweight + блин, рюкзак, жилет, резина
- prim: chest_mid, triceps, front_delt
- load BW+ (+2,5–5 кг) | reps S 5–8, H 8–15
- cues: блин на лопатках (не на пояснице); опора в упорах увеличивает амплитуду
- errors: груз съезжает; провисание корпуса
- progr: deficit + weight | flags: WR med | e1RM Y/L (добавленный вес)

**29. deficit_push_up — Отжимания на упорах (с дефицитом)**
- en: Deficit Push-Up (on handles/parallettes); aliases: отжимания на упорах, на гантелях, между опорами
- pattern: horizontal_push | compound | bilateral | intermediate | eq: упоры или гантели (гексагональные)
- prim: chest_mid, triceps; sec: front_delt
- load BW | reps H 8–20
- cues: грудь опускается ниже уровня кистей на комфортную глубину; нейтральный хват
- errors: чрезмерная глубина при плохой подвижности плеча
- note: нейтральный хват на упорах разгружает запястье
- flags: SH med (глубокое растяжение), WR low | e1RM N

**30. archer_push_up — Отжимания «лучника»**
- en: Archer Push-Up; aliases: отжимания лучником
- pattern: horizontal_push | compound | unilateral-bias | advanced | eq: bodyweight
- prim: chest_mid, triceps (рабочая сторона) | load BW (рычаг) | reps S 3–8 на сторону, H 6–12
- cues: одна рука сгибается, вторая почти прямая и только поддерживает; корпус не вращается
- errors: таз уходит вбок
- regr: push_up | progr: one_arm_push_up
- flags: SH med, WR med | e1RM N

**31. one_arm_push_up — Отжимания на одной руке**
- en: One-Arm Push-Up; aliases: отжимания на одной руке
- pattern: horizontal_push | compound | unilateral | advanced | eq: bodyweight
- prim: chest_mid, triceps, front_delt; sec: core
- load BW (сначала от возвышения) | reps S 1–5, H 5–10
- cues: ноги широко; корпус слегка развёрнут; рука под плечом
- errors: сильная ротация корпуса
- regr: archer_push_up, one-arm incline push-up | flags: SH med, WR med-high | e1RM N

**32. ring_push_up — Отжимания на кольцах или петлях TRX**
- en: Ring / Suspension Push-Up; aliases: отжимания в петлях, на кольцах
- pattern: horizontal_push | compound | bilateral | intermediate | eq: rings_trx
- prim: chest_mid, triceps; sec: serratus, core, rotator_cuff
- load BW (высота петель / угол тела) | reps H 8–15, E 15–25
- cues: кольца прижаты к корпусу в нижней точке; вверху лёгкий разворот наружу
- errors: кольца «разъезжаются»; амплитуда глубже, чем позволяет плечо
- regr: incline на петлях | progr: ноги на опоре
- flags: SH med, WR low (свободная ротация кисти) | e1RM N

#### 1.5. HORIZONTAL_PUSH — брусья

**33. chest_dip — Отжимания на брусьях с акцентом на грудь**
- en: Chest Dip; aliases: брусья, отжимания на брусьях (наклон вперёд)
- pattern: horizontal_push (в части баз — vertical push / dips; по вектору ближе к «нижней» груди) | compound | bilateral | intermediate | eq: dip_bars
- prim: chest_lower, triceps, front_delt
- load BW → BW+ | reps S (weighted) 4–8, H 6–15, E 15–25
- cues: корпус наклонён вперёд, локти немного в стороны; опускаться до глубины, при которой плечо не уходит вперёд (ориентир: плечо примерно на уровне локтя); плечи опущены
- errors: «провал» в плечах с подъёмом их к ушам; глубокое пружинистое дно; раскачка
- regr: assisted_dip_machine, negative dips, bench_dip (не лучшая регрессия для SH) | progr: weighted_dip, ring_dip
- subs: noBB/home → decline_push_up; shoulder → machine_chest_press, decline_dumbbell_press; elbow → machine_dip
- flags: SH high (передняя капсула, акромиально-ключичный сустав при глубоком опускании), EL med | e1RM L (Y при отягощении, считая массу тела)
- note: о вреде брусьев для плеч мнения противоречивы, преобладают блоги без первичных данных ([Cathe](https://cathe.com/are-triceps-dips-bad-for-your-shoulders/amp), [BullBar](https://bullbarfit.com/blogs/updates/dips-are-not-a-shoulder-exercise-heres-what-the-research-actually-shows))

**34. triceps_dip — Отжимания на брусьях с акцентом на трицепс**
- en: Triceps Dip (upright); aliases: брусья вертикально, отжимания на брусьях на трицепс
- pattern: elbow_extension / horizontal_push (компромисс: хранить как compound с primary triceps) | compound | bilateral | intermediate | eq: dip_bars
- prim: triceps; sec: chest_lower, front_delt
- load BW → BW+ | reps S 4–8, H 6–15, E 15–25
- cues: корпус вертикален; локти назад вдоль корпуса; опускание до примерно 90° в локте
- errors: слишком глубоко; плечи «падают» вперёд
- regr: assisted_dip_machine, machine_dip | progr: weighted_dip
- subs: shoulder → pushdown / machine_dip; home → bench_dip (с оговоркой), diamond_push_up
- flags: SH med-high, EL med | e1RM L/Y

**35. weighted_dip — Отжимания на брусьях с отягощением**
- en: Weighted Dip; aliases: брусья с весом, с поясом
- pattern: horizontal_push | compound | bilateral | advanced | eq: dip_bars + пояс с цепью
- prim: chest_lower, triceps, front_delt
- load BW+ (+2,5–5 кг) | reps S 3–6, H 6–12
- cues: вес висит между ног, не раскачивается; глубина та же, что без веса
- errors: из-за веса уменьшается амплитуда; «проседание» в плечах
- regr: chest_dip | flags: SH high, EL med | e1RM Y (bodyweight + added)

**36. assisted_dip_machine — Отжимания на брусьях в гравитроне**
- en: Assisted Dip (Machine); aliases: гравитрон брусья
- pattern: horizontal_push | compound | bilateral | beginner | eq: assist_machine
- prim: triceps, chest_lower | load ASSIST (прогресс — уменьшать противовес) | reps H 8–15, E 15–20
- cues: колени на платформе; контроль глубины; плечи опущены
- errors: противовес «выбрасывает» вверх
- progr: chest_dip / triceps_dip | flags: SH med | e1RM N (L)
- note: движку нужна инверсия: прогресс = меньше кг

(Отжимания на брусьях в тренажёре сидя (`machine_dip`) и обратные отжимания (`bench_dip`) отнесены к elbow_extension, №82 и №83.)

#### 1.6. VERTICAL_PUSH

**37. barbell_overhead_press — Жим штанги стоя (армейский жим)**
- en: Overhead Press (Standing Barbell Press, Military Press); aliases: армейский жим, жим стоя, ОНР (жаргон)
- pattern: vertical_push | compound | bilateral | intermediate | eq: barbell, стойки
- prim: front_delt, triceps; sec: side_delt, upper_traps, chest_upper, core
- load BB +2,5 (на малых весах +1 кг желательно) | reps S 3–6, H 6–10, E 10–15
- cues: ягодицы и пресс напряжены, без прогиба; гриф с верха груди вверх по прямой, голова уходит назад и «проходит» под гриф; вверху гриф над серединой стопы
- errors: сильный прогиб в пояснице (превращается в жим под углом); жим «вокруг» лица вперёд; толчок ногами
- regr: dumbbell_shoulder_press_seated, landmine_press | progr: вес; push_press для перегрузки
- subs: noBB → dumbbell_shoulder_press_standing; DB_home → то же; BW → pike_push_up; shoulder → landmine_press, neutral_db_shoulder_press; elbow/wrist → machine_shoulder_press, landmine_press
- flags: SH high (импинджмент-подобная боль при подъёме над головой), WR med, поясница | e1RM Y
- note: «армейский» часто употребляют как синоним любого жима стоя; часть авторов — только для строгого варианта, пятки вместе (uncertain)

**38. seated_barbell_press — Жим штанги сидя с груди**
- en: Seated Barbell Overhead Press; aliases: жим штанги сидя, жим сидя с груди
- pattern: vertical_push | compound | bilateral | intermediate | eq: barbell, скамья со спинкой, стойки
- prim: front_delt, triceps; sec: side_delt
- load BB | reps S 4–6, H 6–12
- cues: спинка вертикальна или 80–85°; лопатки прижаты; гриф вверх перед лицом
- errors: отрыв спины, превращение в наклонный жим
- regr: smith_shoulder_press | progr: barbell_overhead_press
- subs: как у №37
- flags: SH high, WR med | e1RM Y

**39. behind_neck_press — Жим штанги из-за головы**
- en: Behind-the-Neck Press; aliases: жим из-за головы, жим из-за шеи
- pattern: vertical_push | compound | bilateral | advanced | eq: barbell/smith
- prim: front_delt, side_delt, triceps; sec: upper_traps
- load BB | reps H 6–12 (силовые не рекомендуются)
- cues: только при хорошей наружной ротации плеча; опускать до уровня ушей или верха шеи, не ниже
- errors: глубокое опускание при плохой подвижности; голова вперёд
- regr: barbell_overhead_press | flags: SH high (сочетание отведения и наружной ротации) | e1RM L
- note: в приложении по умолчанию скрыть или не предлагать новичкам и при SH-флаге

**40. push_press — Жимовой швунг (push press)**
- en: Push Press; aliases: швунг жимовой, жим с подсадом, «швунг» (путают со швунгом толчковым — push jerk; uncertain)
- pattern: vertical_push | compound (взрывное) | bilateral | advanced | eq: barbell
- prim: front_delt, triceps, quads (импульс); sec: core
- load BB | reps S 1–5, H —, E —
- cues: короткий подсед на четверть; взрыв ногами, затем дожим руками; без второго подседа
- errors: подсед с наклоном вперёд; второй подсед (это уже толчковый швунг)
- regr: barbell_overhead_press | flags: SH med, поясница | e1RM Y (отдельная шкала)
- note: для аудитории приложения низкий приоритет; можно оставить как advanced

**41. dumbbell_shoulder_press_seated — Жим гантелей сидя**
- en: Seated Dumbbell Shoulder Press; aliases: жим гантелей сидя вверх, жим гантелей над головой сидя
- pattern: vertical_push | compound | bilateral | beginner | eq: dumbbells, скамья со спинкой
- prim: front_delt, triceps; sec: side_delt
- load DB | reps S 6–8, H 8–15, E 15–20
- cues: спинка 75–90°; гантели стартуют на уровне ушей, локти чуть впереди корпуса (в «плоскости лопатки»); выжимать по дуге вверх
- errors: локти строго в стороны и сзади корпуса; прогиб; гантели бьются вверху
- regr: machine_shoulder_press | progr: dumbbell_shoulder_press_standing, barbell_overhead_press
- subs: shoulder → neutral_db_shoulder_press, landmine_press; BW → pike_push_up
- flags: SH med-high, WR low | e1RM Y

**42. dumbbell_shoulder_press_standing — Жим гантелей стоя**
- en: Standing Dumbbell Shoulder Press; aliases: жим гантелей стоя над головой
- pattern: vertical_push | compound | bilateral | intermediate | eq: dumbbells
- prim: front_delt, triceps; sec: side_delt, core
- load DB | reps S 6–8, H 8–12, E 12–20
- cues: пресс и ягодицы напряжены; рёбра «закрыты»; вверху гантели над плечами
- errors: прогиб поясницы; помощь ногами
- regr: dumbbell_shoulder_press_seated | progr: barbell_overhead_press
- flags: SH med-high, поясница | e1RM Y

**43. arnold_press — Жим Арнольда**
- en: Arnold Press; aliases: жим Арнольда сидя/стоя
- pattern: vertical_push | compound | bilateral | intermediate | eq: dumbbells
- prim: front_delt, triceps; sec: side_delt
- load DB (вес ниже, чем в обычном жиме) | reps H 8–12, E 12–20; S —
- cues: старт — ладони к себе на уровне подбородка; по ходу подъёма разворачивать кисти наружу; вниз в обратном порядке
- errors: разворот только вверху, рывком; локти уходят назад
- regr: dumbbell_shoulder_press_seated | flags: SH med-high (ротация под нагрузкой) | e1RM L
- note: при боли в плечах рекомендуют замены ([MenToday](https://www.mentoday.ru/fitness/training/chem-zamenit-zhim-arnolda-esli-ot-nego-bolyat-plechi/))

**44. neutral_db_shoulder_press — Жим гантелей нейтральным хватом над головой**
- en: Neutral-Grip Dumbbell Shoulder Press; aliases: жим гантелей молотковым хватом вверх
- pattern: vertical_push | compound | bilateral | beginner | eq: dumbbells
- prim: front_delt, triceps; sec: side_delt
- load DB | reps S 6–8, H 8–15, E 15–20
- cues: ладони друг к другу; локти впереди корпуса; жать вверх и чуть внутрь
- errors: локти разводятся, хват разворачивается
- note: «щадящая» вертикальная замена при SH/WR | flags: SH med-low, WR low | e1RM Y

**45. single_arm_dumbbell_press — Жим гантели одной рукой стоя**
- en: Single-Arm Dumbbell Overhead Press; aliases: однорукий жим гантели вверх
- pattern: vertical_push | compound | unilateral | intermediate | eq: dumbbell
- prim: front_delt, triceps; sec: core (anti-lateral flexion)
- load DB | reps H 6–12, E 12–20
- cues: корпус не наклоняется в сторону; свободная рука в стороне или на поясе
- errors: компенсация боковым наклоном
- flags: SH med | e1RM L

**46. landmine_press — Жим штанги одной рукой в «мине» (landmine)**
- en: Landmine Press (Single-Arm); aliases: жим в мине, жим угловой штанги, жим конца штанги, жим в лендмайне (названия неустоявшиеся, uncertain)
- pattern: vertical_push (по углу между вертикалью и горизонталью; ряд баз — shoulders) | compound | unilateral (бывает двумя руками) | beginner-intermediate | eq: landmine или угол комнаты + штанга
- prim: front_delt, chest_upper, triceps; sec: serratus, core
- load BB (вес на свободном конце; эффективный вес ≠ вес блинов) +2,5 | reps H 8–12, E 12–20; S 5–8
- cues: стойка в разножку или с колена; жать вверх-вперёд; лопатка свободно «выходит» вперёд в конце
- errors: прогиб корпуса; жим строго вперёд, как от груди
- regr: incline_dumbbell_press | progr: вес, вариант стоя
- note: часто советуют при дискомфорте в плечах во время жима над головой (без надёжного источника по риску)
- flags: SH low-med, WR low | e1RM L

**47. smith_shoulder_press — Жим сидя в Смите**
- en: Smith Machine Shoulder Press; aliases: жим в Смите сидя, армейский в Смите
- pattern: vertical_push | compound | bilateral | beginner | eq: smith, скамья
- prim: front_delt, triceps | load SMITH | reps S 5–8, H 8–12, E 12–20
- cues: скамья так, чтобы гриф шёл перед лицом; стопоры
- errors: гриф за головой; отрыв спины
- flags: SH med-high | e1RM Y (своя шкала)

**48. machine_shoulder_press — Жим вверх в тренажёре сидя**
- en: Machine Shoulder Press; aliases: жим на плечи в тренажёре, рычажный жим вверх
- pattern: vertical_push | compound | bilateral | beginner | eq: machine_stack / plate_loaded
- prim: front_delt, triceps; sec: side_delt
- load STACK/PLATE | reps S 6–8, H 8–15, E 15–25
- cues: рукояти стартуют на уровне подбородка; спина прижата; без рывков
- errors: сиденье низко, слишком глубокое опускание
- flags: SH med (многие тренажёры позволяют нейтральный хват — выбирать его при SH), WR low | e1RM L

**49. kettlebell_press — Жим гири стоя одной рукой**
- en: Kettlebell Overhead Press; aliases: жим гири, жим гири одной рукой, жим двух гирь
- pattern: vertical_push | compound | unilateral/bilateral | intermediate | eq: kettlebell
- prim: front_delt, triceps; sec: core
- load KB (шаг 4 кг, прогресс повторениями) | reps S 3–6, H 6–12, E 12–20
- cues: гиря в «стойке» на предплечье; кисть прямая; выжимать вверх с лёгким разворотом
- errors: гиря «висит» и тянет кисть назад
- flags: SH med, WR med | e1RM L

**50. pike_push_up — Отжимания «щучкой» (пайк)**
- en: Pike Push-Up; aliases: отжимания в позе «домик», пайк-отжимания (устоявшегося названия нет, uncertain)
- pattern: vertical_push | compound | bilateral | intermediate | eq: bodyweight
- prim: front_delt, triceps; sec: upper_traps
- load BW (рычаг: стопы ближе к рукам, затем стопы на возвышении) | reps H 6–15, E 15–25
- cues: таз высоко, тело «уголком»; голова опускается вперёд от кистей, образуя треугольник; локти под 45°
- errors: опускается грудь, а не голова (превращается в обычные отжимания); локти в стороны
- regr: band_overhead_press | progr: elevated_pike_push_up
- flags: SH med, WR med | e1RM N

**51. elevated_pike_push_up — Отжимания щучкой с ногами на возвышении**
- en: Feet-Elevated Pike Push-Up; aliases: пайк с ног на скамье
- pattern: vertical_push | compound | bilateral | advanced | eq: bodyweight + опора
- prim: front_delt, triceps | load BW | reps S 4–8, H 6–12
- cues: корпус почти вертикален; голова к точке перед кистями
- regr: pike_push_up | progr: handstand_push_up | flags: SH med-high, WR med | e1RM N

**52. handstand_push_up — Отжимания в стойке на руках у стены**
- en: Wall Handstand Push-Up (HSPU); aliases: отжимания вниз головой, отжимания в стойке
- pattern: vertical_push | compound | bilateral | advanced | eq: bodyweight + стена
- prim: front_delt, triceps; sec: upper_traps, core
- load BW (амплитуда, дефицит) | reps S 1–5, H 5–10
- cues: подложка под голову; контролируемое опускание; кисти чуть шире плеч
- errors: падение на голову (риск для шеи)
- regr: elevated_pike_push_up | flags: SH high, WR med-high, шея | e1RM N

**53. band_overhead_press — Жим резины над головой**
- en: Band Overhead Press; aliases: жим эспандера вверх
- pattern: vertical_push | compound | bilateral | beginner | eq: band (под стопами)
- prim: front_delt, triceps | load BAND | reps H 12–20, E 20–30
- cues: резина под серединой стоп; кулаки у плеч; жать до прямых рук
- errors: прогиб; укороченная амплитуда
- progr: dumbbell_shoulder_press_standing | flags: SH med-low | e1RM N

**54. z_press — Жим штанги сидя на полу (Z-жим)**
- en: Z Press; aliases: Z-жим (транслитерация; uncertain)
- pattern: vertical_push | compound | bilateral | advanced | eq: barbell или гантели, пол
- prim: front_delt, triceps; sec: core
- load BB/DB | reps S 4–6, H 6–10
- cues: ноги прямые и разведены; корпус вертикален без опоры
- errors: падение корпуса назад
- note: требует хорошей подвижности бёдер; низкий приоритет | flags: SH med-high | e1RM L

**55. half_kneeling_landmine_press — Жим в мине с колена**
- en: Half-Kneeling Landmine Press; aliases: жим в мине стоя на одном колене
- pattern: vertical_push | compound | unilateral | beginner | eq: landmine
- prim: front_delt, chest_upper, triceps; sec: core, serratus
- load BB (шаг 1,25–2,5) | reps H 8–12, E 12–20
- cues: колено рабочей стороны на полу; ягодица напряжена; жать вперёд-вверх
- errors: корпус отклоняется
- note: регрессия №46, выделять ли в отдельную запись — на усмотрение | flags: SH low | e1RM L

#### 1.7. CHEST_ISOLATION

**56. dumbbell_fly — Разводка гантелей лёжа**
- en: Dumbbell Fly; aliases: разведение гантелей лёжа, разводка гантелей на горизонтальной скамье
- pattern: chest_isolation | isolation | bilateral | beginner | eq: dumbbells, bench
- prim: chest_mid; sec: front_delt, biceps (статически)
- load DB (лёгкие; шаг 1–2 кг) | reps S —, H 10–15, E 15–20
- cues: локти слегка согнуты и фиксированы; опускать по дуге до лёгкого растяжения на уровне груди; сводить «обнимая бочку»
- errors: сгибать руки (превращается в жим); опускать ниже уровня скамьи с тяжёлым весом
- regr: pec_deck | progr: cable_crossover
- subs: noBB → то же; DB_home → floor fly (разводка на полу — ограничивает амплитуду); BW → ring/TRX fly (advanced) или band_fly; shoulder → pec_deck с ограниченной амплитудой; elbow → pec_deck (упор предплечьями)
- flags: SH med (растяжение под нагрузкой), EL med-low (медиальный локоть при прямых руках) | e1RM N (трекинг по повторениям и весу)

**57. incline_dumbbell_fly — Разводка гантелей на наклонной скамье**
- en: Incline Dumbbell Fly; aliases: разводка на наклонной
- pattern: chest_isolation | isolation | bilateral | beginner | eq: dumbbells, incline bench
- prim: chest_upper; sec: front_delt | load DB | reps H 10–15, E 15–20
- cues: угол 15–30°; те же правила, что у №56
- errors: угол крутой; гантели «падают» вниз в конце
- flags: SH med | e1RM N

**58. cable_crossover — Сведение рук в кроссовере (сверху вниз)**
- en: Cable Crossover (High-to-Low Cable Fly); aliases: кроссовер, сведение рук на блоках, сведение в кроссовере
- pattern: chest_isolation | isolation | bilateral | beginner | eq: cable
- prim: chest_mid, chest_lower; sec: front_delt
- load STACK (блок 2,5–5 кг) | reps H 10–15, E 15–25
- cues: шаг вперёд, лёгкий наклон корпуса; руки сводятся вниз и вперёд к уровню пупка; локти мягкие и зафиксированные
- errors: давить тросы вниз, разгибая локти (работает трицепс); корпус раскачивается
- regr: pec_deck | progr: single-arm, пауза в сведении
- subs: home → band_fly; BW → —
- flags: SH low-med | e1RM N

**59. low_to_high_cable_fly — Сведение рук в кроссовере снизу вверх**
- en: Low-to-High Cable Fly; aliases: сведение с нижних блоков, кроссовер снизу
- pattern: chest_isolation | isolation | bilateral | beginner | eq: cable
- prim: chest_upper; sec: front_delt
- load STACK | reps H 12–15, E 15–25
- cues: рукояти от бёдер вверх к уровню подбородка или ключиц; ладони чуть вверх
- errors: подъём выше головы (переключается на дельты)
- flags: SH low | e1RM N

**60. mid_cable_fly — Сведение рук на блоках горизонтально (на уровне груди)**
- en: Mid-Cable Fly (Standing/Seated); aliases: сведение в кроссовере на уровне груди
- pattern: chest_isolation | isolation | bilateral | beginner | eq: cable
- prim: chest_mid | load STACK | reps H 10–15, E 15–25
- cues: блоки на уровне плеча; руки сходятся перед грудью; пауза в сведении
- errors: плечи уходят вперёд и вверх
- note: можно хранить как атрибут «угол» у №58 (см. раздел 3) | flags: SH low | e1RM N

**61. pec_deck — Сведение рук в тренажёре «Бабочка» (Пек-дек)**
- en: Pec Deck / Machine Fly; aliases: бабочка, баттерфляй, пек-дек, сведение в тренажёре
- pattern: chest_isolation | isolation | bilateral | beginner | eq: machine_stack
- prim: chest_mid; sec: front_delt
- load STACK | reps H 10–15, E 15–25; S —
- cues: рукояти на уровне груди; спина прижата; ограничитель амплитуды выставить так, чтобы в начале было комфортное растяжение
- errors: амплитуда «за спину»; рывки
- note: на многих тренажёрах та же машина используется для задней дельты (это тяга — вне этого раздела)
- flags: SH low-med | e1RM N

**62. single_arm_cable_fly — Сведение одной рукой на блоке**
- en: Single-Arm Cable Fly; aliases: сведение одной рукой в кроссовере
- pattern: chest_isolation | isolation | unilateral | intermediate | eq: cable
- prim: chest_mid | load STACK | reps H 12–15, E 15–20
- cues: рука проходит за среднюю линию тела; корпус не вращается
- errors: ротация корпуса
- flags: SH low | e1RM N

**63. band_fly — Сведение рук с резиной**
- en: Band Chest Fly; aliases: сведение эспандера
- pattern: chest_isolation | isolation | bilateral | beginner | eq: band
- prim: chest_mid | load BAND | reps H 15–20, E 20–30
- cues: резина за спиной на уровне груди; дуга, как при разводке; пауза
- note: домашняя замена кроссовера | flags: SH low | e1RM N

**64. dumbbell_pullover — Пуловер с гантелью лёжа**
- en: Dumbbell Pullover; aliases: пуловер, пуловер поперёк скамьи
- pattern: chest_isolation (спорно: ряд источников относит к широчайшим, то есть к pull; во free-exercise-db помечен как push/chest — не проверено) | isolation (плечевое разгибание) | bilateral | intermediate | eq: dumbbell, bench
- prim: chest_mid (или lats — по технике); sec: triceps_long, serratus
- load DB | reps H 10–15, E 15–20
- cues: таз ниже скамьи или лёжа вдоль; руки слегка согнуты; опускать за голову до комфортного растяжения
- errors: чрезмерное растяжение; сгибание локтей (превращается в разгибание на трицепс)
- flags: SH high (подъём руки над головой с нагрузкой) | e1RM N
- note: в замены по pattern не включать автоматически

**65. svend_press — Жим Свенда (сдавливание блина)**
- en: Svend Press (Plate Squeeze Press); aliases: жим Свенда, жим блина от груди со сдавливанием
- pattern: chest_isolation (по факту — изометрическое приведение плюс разгибание) | isolation | bilateral | beginner | eq: блины 5–10 кг
- prim: chest_mid; sec: front_delt
- load PLATE (дискретные блины) | reps H 12–20, E 20–30
- cues: блины сжаты ладонями перед грудью; выжимать вперёд, не ослабляя сдавливания
- errors: ослабление сдавливания
- note: низкая нагрузка; скорее финишер. Название устоялось по имени Svend Karlsen | flags: low | e1RM N

#### 1.8. SHOULDER_ISOLATION (задняя дельта — это тяга, исключена)

**66. dumbbell_lateral_raise — Махи гантелями в стороны**
- en: Dumbbell Lateral Raise; aliases: разведение гантелей в стороны стоя, подъём гантелей через стороны, «махи» (разговорное, самое распространённое)
- pattern: shoulder_isolation | isolation | bilateral | beginner | eq: dumbbells
- prim: side_delt; sec: front_delt, upper_traps
- load DB (шаг 1–2 кг, относительно огромный → прогресс повторениями) | reps S —, H 10–20, E 15–30
- cues: локти слегка согнуты, ведут движение; поднимать до уровня плеч в плоскости лопатки (руки чуть впереди корпуса); плечи не поднимать к ушам
- errors: раскачка корпусом; подъём «трапециями»; вращение гантели «как из чайника» — сомнительная подсказка, не давать
- regr: machine_lateral_raise | progr: cable_lateral_raise, lean_away_lateral_raise
- subs: noBB → то же; DB_home → то же или с бутылками; BW → band_lateral_raise (без снарядов почти нет вариантов); shoulder → cable_lateral_raise с ограничением до 60–70°; elbow/wrist → machine_lateral_raise (упор плечом)
- flags: SH med (при болевой дуге ограничить высоту), EL low | e1RM N
- source: прирост гантели ≈ блок ([Larsen 2025](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2025.1611468/full))

**67. seated_lateral_raise — Махи гантелями сидя**
- en: Seated Dumbbell Lateral Raise; aliases: разведения сидя
- pattern: shoulder_isolation | isolation | bilateral | beginner | eq: dumbbells, bench
- prim: side_delt | load DB | reps H 10–20, E 15–30
- cues: сидя исключаем читинг; остальное как у №66
- note: допустимо хранить как вариант №66 | flags: SH med | e1RM N

**68. cable_lateral_raise — Отведение руки в сторону на нижнем блоке**
- en: Cable Lateral Raise; aliases: махи на блоке, махи в кроссовере одной рукой
- pattern: shoulder_isolation | isolation | unilateral | beginner | eq: cable
- prim: side_delt | load STACK (1-й шаг часто 2,5–5 кг — крупный; прогресс повторениями) | reps H 12–20, E 15–25
- cues: блок внизу; трос проходит спереди или сзади тела; плавный подъём до уровня плеча
- errors: наклон корпуса; рывок
- note: по гипертрофии ≈ гантели ([Frontiers 2025](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2025.1611468/full)) | flags: SH low-med | e1RM N

**69. machine_lateral_raise — Махи в стороны в тренажёре**
- en: Machine Lateral Raise; aliases: разведения в тренажёре на дельты
- pattern: shoulder_isolation | isolation | bilateral | beginner | eq: machine_stack
- prim: side_delt | load STACK | reps H 10–20, E 15–25
- cues: ось вращения тренажёра совпадает с плечевым суставом; давить предплечьем или локтем
- errors: поднимать плечи к ушам
- flags: SH low-med, EL/WR low | e1RM N

**70. lean_away_lateral_raise — Махи одной рукой с отклонением (держась за опору)**
- en: Lean-Away Lateral Raise; aliases: махи с наклоном, махи держась за стойку
- pattern: shoulder_isolation | isolation | unilateral | intermediate | eq: dumbbell + опора
- prim: side_delt | load DB | reps H 10–20
- cues: корпус отклонён на 15–30°; нагрузка в нижней части амплитуды выше
- flags: SH med | e1RM N

**71. band_lateral_raise — Махи в стороны с резиной**
- en: Band Lateral Raise; aliases: разведения с эспандером
- pattern: shoulder_isolation | isolation | bilateral/unilateral | beginner | eq: band
- prim: side_delt | load BAND | reps H 15–25, E 20–30
- cues: резина под стопой; локти чуть согнуты; подъём до плеч
- note: нагрузка максимальна вверху | flags: SH low-med | e1RM N

**72. dumbbell_front_raise — Подъём гантелей перед собой**
- en: Dumbbell Front Raise; aliases: махи вперёд, подъём гантелей вперёд
- pattern: shoulder_isolation | isolation | bilateral/alternating | beginner | eq: dumbbells
- prim: front_delt; sec: chest_upper, serratus
- load DB | reps H 10–15, E 15–25
- cues: подъём до уровня глаз или плеч; без раскачки; хват нейтральный или прямой
- errors: раскачка; подъём выше головы с весом
- note: передняя дельта уже сильно нагружена в жимах — низкий приоритет в программе | flags: SH med | e1RM N

**73. plate_front_raise — Подъём блина перед собой**
- en: Plate Front Raise; aliases: подъём блина вперёд, «руль»
- pattern: shoulder_isolation | isolation | bilateral | beginner | eq: plate
- prim: front_delt | load PLATE (дискретные: 5/10/15/20 кг) | reps H 10–15, E 15–20
- cues: хват по краям блина «на 3 и 9 часов»
- flags: SH med, WR low | e1RM N

**74. cable_front_raise — Подъём руки вперёд на нижнем блоке**
- en: Cable Front Raise; aliases: подъём перед собой с блока
- pattern: shoulder_isolation | isolation | uni/bilateral | beginner | eq: cable
- prim: front_delt | load STACK | reps H 12–15, E 15–25
- flags: SH low-med | e1RM N

**75. upright_row — Тяга штанги к подбородку (протяжка)**
- en: Upright Row; aliases: протяжка, тяга к подбородку, тяга штанги к груди стоя
- pattern: shoulder_isolation (спорно: биомеханически это тяга; в ExRx и многих базах числится как плечевое или трапецевидное; в приложении отметить `pattern_note: pull-like`) | compound | bilateral | intermediate | eq: barbell, ez_bar, dumbbells, cable
- prim: side_delt, upper_traps; sec: front_delt, biceps
- load BB/DB/STACK | reps H 10–15, E 15–20
- cues: хват шире плеч; локти ведут вверх только до уровня плеч; гриф близко к телу
- errors: узкий хват и подъём локтей выше плеч (внутренняя ротация + отведение)
- flags: SH high (классически ассоциируется с импинджментом), WR med | e1RM N
- note: при SH-флаге скрыть; замена — dumbbell_lateral_raise или cable_lateral_raise

#### 1.9. ELBOW_EXTENSION (трицепс)

**76. cable_pushdown_bar — Разгибание рук на верхнем блоке (прямая или V-рукоять)**
- en: Cable Triceps Pushdown (Straight/V-Bar); aliases: разгибание рук на блоке, трицепс на блоке, «французский на блоке» (неверное употребление)
- pattern: elbow_extension | isolation | bilateral | beginner | eq: cable
- prim: triceps (латеральная и медиальная головки); sec: —
- load STACK | reps S —, H 8–15, E 15–25
- cues: локти прижаты к бокам и неподвижны; разгибать до полного выпрямления; плечи опущены
- errors: локти «гуляют» вперёд-назад; «дожим» весом тела, наклоняясь над рукоятью
- regr: band_pushdown | progr: вес; rope_pushdown
- subs: noBB → то же; home → band_pushdown, diamond_push_up; BW → bodyweight_triceps_extension; shoulder → то же (обычно щадяще); elbow/wrist → rope_pushdown (нейтральный хват)
- flags: EL med-low, WR med (прямая рукоять) | e1RM L (трекинг по весу и повторениям)

**77. rope_pushdown — Разгибание рук на блоке с канатом**
- en: Rope Triceps Pushdown; aliases: разгибание с канатом, трицепс с верёвкой
- pattern: elbow_extension | isolation | bilateral | beginner | eq: cable + rope
- prim: triceps | load STACK (обычно ниже, чем с рукоятью) | reps H 10–15, E 15–25
- cues: внизу развести концы каната в стороны; локти неподвижны
- errors: тянуть руки, сгибая плечи
- flags: EL low, WR low | e1RM L

**78. reverse_grip_pushdown — Разгибание рук на блоке обратным хватом**
- en: Reverse-Grip Pushdown; aliases: разгибания обратным хватом
- pattern: elbow_extension | isolation | bilateral/unilateral | intermediate | eq: cable
- prim: triceps (медиальная) | load STACK (низкий) | reps H 12–15, E 15–20
- errors: сгибание кистей
- flags: WR med | e1RM N

**79. single_arm_cable_pushdown — Разгибание одной рукой на блоке**
- en: Single-Arm Cable Pushdown; aliases: разгибание одной рукой
- pattern: elbow_extension | isolation | unilateral | beginner | eq: cable (D-рукоять)
- prim: triceps | load STACK | reps H 10–15, E 15–20
- flags: low | e1RM N

**80. overhead_cable_extension — Разгибание рук из-за головы на блоке (канат)**
- en: Overhead Cable Triceps Extension; aliases: французский жим на блоке, разгибания из-за головы стоя спиной к блоку
- pattern: elbow_extension | isolation | bilateral (или одной рукой) | beginner | eq: cable + rope
- prim: triceps_long, triceps | load STACK | reps H 10–15, E 15–25
- cues: спиной к блоку, разножка, лёгкий наклон корпуса; локти направлены вперёд-вверх, неподвижны; глубокое растяжение за головой
- errors: локти разъезжаются; движение в плечах вместо локтей
- note: даёт примерно в 1,4 раза больший прирост трицепса, чем пушдаун ([Maeo et al. via BarBend](https://barbend.com/overhead-triceps-extensions-vs-pushdowns-muscle-growth-study))
- flags: SH med (рука над головой), EL med | e1RM L

**81. skull_crusher_ez — Французский жим лёжа (EZ-штанга)**
- en: Lying Triceps Extension / Skull Crusher; aliases: французский жим лёжа, «дробитель черепов», французский жим со штангой
- pattern: elbow_extension | isolation | bilateral | intermediate | eq: ez_bar (или прямой гриф), bench
- prim: triceps (с акцентом на длинную, если опускать за голову); sec: —
- load EZ +2,5 | reps S —, H 8–12, E 12–20
- cues: плечи чуть отклонены назад от вертикали; опускать к макушке или за голову, локти не разводить; разгибать, не «бросая» гриф на лоб
- errors: локти расходятся; работает плечо (превращается в пуловер-жим); слишком тяжело, локти болят
- regr: dumbbell_skull_crusher, rope_pushdown | progr: вес; jm_press
- subs: noBB → dumbbell_skull_crusher; home → dumbbell_skull_crusher на полу; BW → bodyweight_triceps_extension; shoulder → pushdown; elbow/wrist → rope_pushdown, dumbbell_skull_crusher (нейтральный хват)
- flags: EL high (самый частый «локтевой» триггер), WR med | e1RM L (Y для опытных)
- source: [Skillbox](https://skillbox.ru/media/health/french-press/)

**82. machine_dip — Отжимания в тренажёре сидя (жим вниз)**
- en: Seated Dip Machine; aliases: брусья в тренажёре, жим вниз сидя, разгибание рук в тренажёре сидя (неоднозначно)
- pattern: elbow_extension (compound-like) | compound | bilateral | beginner | eq: machine_stack / plate_loaded
- prim: triceps; sec: chest_lower | load STACK | reps S 6–8, H 8–15, E 15–20
- cues: локти назад; плечи опущены; полное разгибание
- errors: подъём плеч
- note: замена брусьев при SH | flags: SH low, EL med-low | e1RM L

**83. bench_dip — Обратные отжимания от скамьи**
- en: Bench Dip; aliases: отжимания от скамьи сзади, обратные отжимания
- pattern: elbow_extension | compound | bilateral | beginner (по нагрузке), но SH-рискованный | eq: скамья, стул
- prim: triceps; sec: front_delt, chest
- load BW (ноги согнуты, затем прямые, затем на возвышении, затем блин на бёдрах) | reps H 10–20, E 20–30
- cues: таз близко к скамье; опускаться до 90° в локте, не глубже; плечи назад и вниз
- errors: глубокое опускание с выходом плеча вперёд; таз далеко от опоры
- note: широко распространены дома, но положение (плечо в экстензии и внутренней ротации) часто критикуют. Для SH предложить diamond_push_up / band_pushdown (оценка без первичного источника)
- flags: SH high, WR med | e1RM N

**84. dumbbell_skull_crusher — Французский жим гантелей лёжа**
- en: Dumbbell Lying Triceps Extension; aliases: французский жим с гантелями лёжа
- pattern: elbow_extension | isolation | bilateral | beginner | eq: dumbbells, bench или пол
- prim: triceps | load DB | reps H 10–15, E 15–20
- cues: нейтральный хват (ладони друг к другу); гантели опускать к ушам; локти на ширине плеч
- errors: локти расходятся; гантели над лицом без контроля
- flags: EL med, WR low | e1RM N

**85. seated_db_overhead_extension — Французский жим гантели сидя (двумя руками)**
- en: Seated Dumbbell Overhead Triceps Extension; aliases: французский жим сидя, разгибание гантели из-за головы
- pattern: elbow_extension | isolation | bilateral | beginner | eq: dumbbell, скамья со спинкой
- prim: triceps_long | load DB | reps H 8–15, E 15–20
- cues: гантель за головой держится «чашей» ладоней за диск; локти смотрят вверх, близко к голове; поясница прижата к спинке
- errors: прогиб поясницы; локти в стороны
- flags: SH med, EL med | e1RM L

**86. single_arm_overhead_extension — Французский жим одной рукой из-за головы**
- en: Single-Arm Overhead Dumbbell Extension; aliases: разгибание одной рукой из-за головы
- pattern: elbow_extension | isolation | unilateral | beginner | eq: dumbbell
- prim: triceps_long | load DB | reps H 10–15, E 15–20
- cues: свободной рукой поддерживать рабочий локоть; гантель за голову к противоположному плечу
- flags: SH med, EL med | e1RM N

**87. seated_ez_overhead_extension — Французский жим EZ-штанги сидя**
- en: Seated EZ-Bar Overhead Extension; aliases: французский жим сидя со штангой
- pattern: elbow_extension | isolation | bilateral | intermediate | eq: ez_bar, скамья со спинкой
- prim: triceps_long | load EZ | reps H 8–12, E 12–15
- cues: узкий хват на изгибах; локти вверх; разгибать без отклонения корпуса
- errors: локти «разваливаются»
- flags: SH med-high, EL high, WR med | e1RM L

**88. dumbbell_kickback — Разгибание руки с гантелью в наклоне (кикбэк)**
- en: Dumbbell Triceps Kickback; aliases: кикбэк, отведение руки назад в наклоне
- pattern: elbow_extension | isolation | unilateral (или в паре) | beginner | eq: dumbbell, bench
- prim: triceps | load DB (лёгкий) | reps H 12–20, E 15–25
- cues: плечо параллельно полу, неподвижно; полное разгибание с паузой
- errors: плечо опускается, движение превращается в мах
- note: нагрузка в начале амплитуды мала; кабельный вариант эффективнее (оценка) | flags: low | e1RM N

**89. jm_press — JM-жим**
- en: JM Press; aliases: жим JM, «Джей-Эм жим» (транслитерация, uncertain)
- pattern: elbow_extension (гибрид жима и разгибания) | compound | bilateral | advanced | eq: barbell, smith
- prim: triceps; sec: chest_mid
- load BB | reps S 5–8, H 8–12
- cues: узкий хват; гриф опускается к верхней части груди или подбородку с выносом локтей вперёд; разгибать по траектории назад
- errors: превращается в узкий жим или во французский жим
- flags: EL high, WR med | e1RM L

**90. machine_triceps_extension — Разгибание рук в тренажёре на трицепс**
- en: Machine Triceps Extension; aliases: трицепс-машина
- pattern: elbow_extension | isolation | bilateral | beginner | eq: machine_stack
- prim: triceps | load STACK | reps H 10–15, E 15–25
- cues: локти совмещены с осью вращения; плечи опущены
- flags: EL low-med | e1RM N

**91. band_pushdown — Разгибание рук с резиной**
- en: Band Triceps Pushdown; aliases: разгибание с эспандером (резина закреплена вверху)
- pattern: elbow_extension | isolation | bilateral | beginner | eq: band
- prim: triceps | load BAND | reps H 15–25, E 20–30
- cues: как у №76; резина за дверь или турник
- flags: low | e1RM N

**92. bodyweight_triceps_extension — Разгибания на трицепс с весом тела**
- en: Bodyweight Triceps Extension (Bar/Bench); aliases: «французские отжимания», разгибания от перекладины в Смите или от скамьи (единого названия нет, uncertain; MenToday называет «французские отжимания»: [MenToday](https://www.mentoday.ru/fitness/training/francuzskie-otzhimaniya-prostoe-uprazhnenie-dlya-tricepsov-kotoroe-mozhno-delat-dazhe-na-skameyke/))
- pattern: elbow_extension | isolation | bilateral | intermediate | eq: bodyweight + опора (скамья, гриф в Смите, перила)
- prim: triceps (long) | load BW (угол тела) | reps H 8–15, E 15–25
- cues: тело прямое; кисти на опоре; сгибать только локти, опуская лоб к опоре; разгибать
- errors: проседание таза; движение в плечах
- regr: выше опора | progr: ниже опора
- flags: EL med-high, WR med | e1RM N

#### 1.10. Сводные таблицы замен (по паттерну)

| Ситуация | horizontal_push | vertical_push | chest_isolation | shoulder_isolation | elbow_extension |
|---|---|---|---|---|---|
| Нет штанги (зал) | dumbbell_bench_press, machine_chest_press, hammer_chest_press | dumbbell_shoulder_press_seated, machine_shoulder_press | pec_deck, cable_crossover | cable_lateral_raise | cable_pushdown_bar, overhead_cable_extension |
| Только гантели дома | dumbbell_floor_press, dumbbell_bench_press (если есть скамья), squeeze_press | dumbbell_shoulder_press_standing/seated, neutral_db_shoulder_press | dumbbell_fly (пол/скамья) | dumbbell_lateral_raise | seated_db_overhead_extension, dumbbell_skull_crusher, dumbbell_kickback |
| Только вес тела | push_up и лестница (wall → incline → knee → push_up → decline → deficit → archer → one_arm), chest_dip при наличии брусьев | pike_push_up → elevated_pike → handstand_push_up | (нет полноценной; band_fly при наличии резины; ring fly — advanced) | (нет; band_lateral_raise) | diamond_push_up, bodyweight_triceps_extension, bench_dip (SH!) |
| Проблема плеча (SH) | neutral_grip_dumbbell_press, floor_press_barbell, dumbbell_floor_press, machine_chest_press | landmine_press, half_kneeling_landmine_press, neutral_db_shoulder_press | cable_crossover / pec_deck с ограниченной амплитудой | cable_lateral_raise до 60–70° | rope_pushdown, cable_pushdown_bar, machine_dip |
| Локоть или запястье (EL/WR) | neutral_grip_dumbbell_press, machine_chest_press, push-up на упорах | machine_shoulder_press (нейтральные ручки), landmine_press | pec_deck (упор предплечьем) | machine_lateral_raise | rope_pushdown, dumbbell_skull_crusher нейтральным хватом; избегать skull_crusher_ez, jm_press |

#### 1.11. Правила для движка (выводы, не из источника)
- e1RM считать только для записей с флагом Y и при повторениях ≤10–12. Хранить отдельно для штанги, Смита, гантелей (вес на руку) и каждого тренажёра (`equipment_instance_id`).
- Для изоляции с крупным относительным шагом (махи, разводки, гири, блок с шагом 5 кг) двойная прогрессия по повторениям с широким окном (например 12→20), затем шаг веса и откат к нижней границе.
- Для ASSIST (гравитрон) прогресс означает уменьшение веса — инверсия знака.
- Для BW-лестниц прогрессия = переход на следующую запись (`progression_next_id`), а не вес.
- Флаги SH/EL/WR — триггеры фильтра «Заменить» и подсказки LLM, а не диагноз.

### Gaps
- По каждой записи отдельного первоисточника нет: подсказки, ошибки, диапазоны повторений и шаги веса — синтез общепринятой практики (NSCA, ExRx, тренерские материалы), без построчной проверки. ExRx, sportwiki.to, ironman.ru, atletiq в этой сессии не открывались, поэтому сверка русских названий с ними не выполнена.
- Отчёт по PMC11224528 (нагрузки на плечо при разных вариантах жима) прочитан только по резюме — за капчей не удалось проверить выводы о прогибе и траектории.
- Количественные данные о риске брусьев (chest_dip, bench_dip) и протяжки для плеча найдены только в блогах; рецензируемых данных по частоте травм не найдено.
- Поправочные коэффициенты e1RM между вариантами (пауза или касание, Смит или штанга, гантели или штанга) не найдены в надёжных источниках — указаны как оценки.

---

## 2. Стандартные русские названия и разногласия

### Takeaway
Основные русские названия устоялись: «Жим лёжа», «Жим гантелей на наклонной скамье», «Французский жим», «Отжимания на брусьях», «Махи гантелями в стороны», «Сведение рук в кроссовере», «Бабочка». Разногласия касаются вариантов («армейский», «французский» как зонтичный термин, «отрицательный» и «обратный» наклон, «швунг»), брендового жаргона («Хаммер», «Смит», «гравитрон») и новых упражнений без устоявшегося русского названия (landmine, pike, JM, Z-press, squeeze press).

### Cited Findings
- «Французский жим» — зонтичное название для опускания веса ко лбу или за голову. Есть варианты лёжа, сидя и стоя, со штангой, EZ, гантелями и на блоке; лёжа также называют «дробитель черепов»; англоязычный эквивалент — lying triceps extension. Происхождение термина спорное: версия про французских атлетов против версии про кофейный «френч-пресс» — [Skillbox](https://skillbox.ru/media/health/french-press/)
- «Хаммер» — жаргонное название рычажных тренажёров с блинами по бренду Hammer Strength, распространяется на аналоги других производителей — [Лайфхакер](https://lifehacker.ru/zhim-v-xammere/amp/)
- «Жим Арнольда» — устоявшееся название; в русских медиа широко используется — [MenToday](https://www.mentoday.ru/fitness/training/kak-pravilno-delat-jim-arnolda-chtoby-vyglyadet-kak-terminator/); [Lyfta RU](https://www.lyfta.app/ru/exercise/dumbbell-arnold-press-7rl)
- «Французские отжимания» используются в медиа для разгибаний на трицепс с весом тела от скамьи — [MenToday](https://www.mentoday.ru/fitness/training/francuzskie-otzhimaniya-prostoe-uprazhnenie-dlya-tricepsov-kotoroe-mozhno-delat-dazhe-na-skameyke/)
- Варианты названий французского жима в массовых медиа — [Лайфхакер](https://lifehacker.ru/francuzskij-zhim/amp/), [Спортмастер](https://www.sportmaster.ru/media/articles/francuzskij-zhim-kachaem-tricepsy/), [Лента](https://lenta.ru/articles/2023/12/13/kak-pravilno-vypolnyat-frantsuzskiy-zhim/amp/)

### Inferences
Список спорных и неоднозначных названий (рекомендуемое каноническое название указано первым; остальные — в aliases для поиска):
- «Жим лёжа» = «Жим штанги лёжа». В интерфейсе использовать полное название, «жим лёжа» оставить алиасом. Без уточнения «жим лёжа» в разговоре почти всегда означает штангу.
- «Армейский жим»: одни используют как синоним любого жима штанги стоя, другие — только для строгого варианта (пятки вместе, без прогиба). Канон: «Жим штанги стоя», алиас «армейский жим».
- Отрицательный наклон: варианты «жим на скамье с отрицательным наклоном», «жим головой вниз», «жим на скамье с обратным наклоном». Канон — «с отрицательным наклоном» («обратный» иногда смешивают с наклонным).
- «Махи» и «разведения»: «махи гантелями в стороны», «разведение гантелей в стороны», «подъём гантелей через стороны». Канон «Махи гантелями в стороны», остальные — алиасы. «Разводка» обычно относится к груди (лёжа), «разведение» — к плечам; путаница частая.
- «Сведение в кроссовере», «кроссовер», «сведение рук на блоках» — синонимы; направление (сверху вниз, снизу вверх) указывать явно.
- «Бабочка», «баттерфляй», «пек-дек» — синонимы; «обратная бабочка» — задняя дельта (тяга, исключено).
- Тяга к подбородку и протяжка — синонимы (по классификации спорно, см. №75).
- Швунг: «жимовой швунг» (push press) и «толчковый швунг» (push jerk) часто путают; uncertain.
- Новые упражнения без устоявшегося названия: landmine press («жим в мине», «жим штанги одной рукой от угла»); pike push-up («отжимания щучкой», «пайк»); JM press; Z-press; squeeze/crush press; Svend press («жим Свенда» встречается). Все помечены uncertain.
- «Брусья» = «отжимания на брусьях»; акцент на грудь или трицепс задаётся наклоном корпуса. Предлагаю две записи (см. раздел 3).
- «Гравитрон» — бытовое название тренажёра с противовесом (брендовое, по аналогии с «Хаммером»).

### Gaps
- Не удалось проверить употребление названий в sportwiki.to, ironman.ru, atletiq (страницы не открывались). Для финальной локализации рекомендуется ручная сверка 20–30 ключевых названий.
- Нет данных о частоте употребления вариантов (например, «махи» против «разведений») — только экспертная оценка.

---

## 3. Какие варианты заслуживают отдельной записи (наклон, хват, оборудование)

### Takeaway
Отдельная запись нужна, если вариант меняет (а) основную мышцу или вектор, (б) шкалу нагрузки (e1RM несопоставим) или (в) профиль риска либо требования к оборудованию. Угол скамьи (0/30/отрицательный) и узкий хват — отдельные записи. Ширину хвата (кроме узкого), угол троса в кроссовере и «сидя или стоя» в махах лучше хранить как атрибут варианта.

### Cited Findings
- Наклон около 30° даёт максимум активности ключичной части большой грудной; при 45–60° доминирует передняя дельта; горизонталь лучше нагружает среднюю и нижнюю части. Трицепс от угла не зависит — [Rodríguez-Ridao 2020, PMC7579505](https://pmc.ncbi.nlm.nih.gov/articles/PMC7579505/)
- Узкий хват смещает долю усилия на трицепс (около 37% против 22%) и даёт на 5–6% меньший 1ПМ, чем широкий — [StrengthLog / Larsen 2020](https://www.strengthlog.com/wide-vs-close-grip-bench-press-strength-ratio-muscles-worked/)
- Более узкий хват и сведённые лопатки снижают нагрузку и риск для плеча — [Physio-network](https://physio-network.com/review/effects-of-bench-press-technique-variations-on-musculoskeletal-shoulder-loads-and-potential-injury-risk)
- Положение плеча при разгибании на трицепс (над головой или вдоль тела) влияет на гипертрофию (около 1,4 раза в пользу положения над головой) — [BarBend / Maeo](https://barbend.com/overhead-triceps-extensions-vs-pushdowns-muscle-growth-study)
- Гантели и блок в махах дают сопоставимую гипертрофию — [Frontiers 2025](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2025.1611468/full)

### Inferences
- Отдельные записи: плоский, наклонный и отрицательный жим (штанга и гантели); узкий хват; жим с паузой (если движок ведёт силовые программы); жим с пола (другая амплитуда — другой e1RM); Смит отдельно от свободной штанги; брусья на грудь и брусья на трицепс; разгибания над головой и вниз (разный стимул по данным Maeo); жим гантелей пронированным и нейтральным хватом (разные флаги SH/WR).
- Атрибуты, а не записи: ширина хвата в жиме (кроме узкого), угол наклона 15° или 30° внутри «наклонного», сидя или стоя в махах (можно, но не обязательно), насадка в пушдаунах (прямая, V, канат — но канат влияет на WR, поэтому оставлен отдельной записью), угол троса в кроссовере (оставлены 2–3 записи для понятности пользователю).
- Широкий хват в жиме лёжа отдельной записью не нужен: польза незначительна, нагрузка на плечо выше.
- Для движка: `parent_id` (базовое упражнение) плюс `variant_attrs` (angle, grip, implement, stance) упрощают подбор замен «внутри семейства» перед поиском по паттерну.

### Gaps
- Нет прямых данных о гипертрофии при наклонном и плоском жиме за пределами ЭМГ (ЭМГ — косвенный показатель); не проверены лонгитюдные исследования по наклону.
- Не найдено надёжных данных, что отрицательный наклон даёт уникальный стимул по сравнению с плоским жимом.

---

## 4. Как открытые базы размечают эти упражнения (wger, free-exercise-db, ExerciseDB, MuscleWiki)

### Takeaway
free-exercise-db (yuhonas) — плоская схема с enum'ами force/level/mechanic/equipment/muscles. Её удобно маппить: push плюс chest, shoulders или triceps соответствует нашему разделу. ExerciseDB использует bodyParts, targetMuscles и equipments с более детальными мышцами (например, «Pectoralis Major Clavicular Head»). MuscleWiki фильтрует по оборудованию, сложности и мышцам. API wger в этой сессии получить не удалось (robots или прокси).

### Cited Findings
- free-exercise-db: поля id, name, force, level, mechanic, equipment, primaryMuscles, secondaryMuscles, instructions, category, images; 800+ упражнений, данные в public domain — [README](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/README.md)
- Enum'ы free-exercise-db (schema.json): force = static | pull | push | null; level = beginner | intermediate | expert; mechanic = isolation | compound | null; equipment = medicine ball, dumbbell, body only, bands, kettlebells, foam roll, cable, machine, barbell, exercise ball, e-z curl bar, other, null; muscles = abdominals, abductors, adductors, biceps, calves, chest, forearms, glutes, hamstrings, lats, lower back, middle back, neck, quadriceps, shoulders, traps, triceps; category = powerlifting, strength, stretching, cardio, olympic weightlifting, strongman, plyometrics — [schema.json](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/schema.json)
- ExerciseDB (v2): поля exerciseId, name, imageUrl, videoUrl, equipments[], bodyParts[], exerciseType, targetMuscles[], secondaryMuscles[], keywords, overview, instructions, exerciseTips, variations, relatedExerciseIds. Пример целевой мышцы — «Pectoralis Major Clavicular Head», bodyPart «Chest», equipment «Barbell». Объём указан противоречиво: 1500+ или 5000+ — [GitHub exercisedb-api](https://github.com/JakobDrist/exercisedb-api)
- MuscleWiki: оборудование (Barbell, Dumbbells, Bodyweight и др.), сложность Beginner, Intermediate, Advanced, фильтры Category, Muscles, Goals — [MuscleWiki workouts](https://musclewiki.com/workouts?page=2)

### Inferences
- Маппинг нашей схемы на free-exercise-db: horizontal_push или vertical_push → force=push, mechanic=compound; chest_isolation → push, isolation, primaryMuscles=chest; shoulder_isolation → push или pull (махи там, вероятно, push или null — не проверено), primary=shoulders; elbow_extension → push, isolation, triceps. В free-exercise-db нет разделения на переднюю и среднюю дельту и на части груди, поэтому наша детализация (chest_upper, side_delt) — дополнительный слой.
- level «expert» в free-exercise-db соответствует нашему «advanced».
- Для импорта картинок и инструкций (public domain) удобнее всего free-exercise-db; ExerciseDB — коммерческий или RapidAPI-продукт с иной лицензией (проверить).
- wger: по памяти (не проверено в этой сессии) категории называются Arms, Chest, Shoulders и т.д.; мышцы с латинскими названиями; оборудование включает Barbell, Dumbbell, SZ-Bar, Bench, Incline bench, Kettlebell, Pull-up bar, Gym mat, Swiss Ball. Считать неподтверждённым.

### Gaps
- wger API (wger.de/api/v2/...) недоступен из среды (robots_disallowed, прокси 403) — категории и оборудование wger не подтверждены.
- Полные списки bodyParts, targetMuscles и equipment у ExerciseDB не получены (только пример).
- Конкретные теги отдельных упражнений (например, как MuscleWiki помечает махи или брусья) не проверены по каждой записи.
