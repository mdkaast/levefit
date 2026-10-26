# Каталог упражнений: низ тела и кор (lower body + core) — по состоянию на октябрь 2026

Назначение: стартовые данные (seed) для базы упражнений Telegram Mini App. Записи используются для замены упражнения («Заменить»), флагов безопасности и решений движка прогрессии (двойная прогрессия, шаг веса = минимальное доступное приращение).
Охват: присед, наклон в тазобедренном суставе (hinge), выпады и работа на одной ноге, разгибание бедра (ягодичные), тренажёры на разгибание колена, сгибание ног, икры, приводящие и отводящие, кор (антиэкстензия, антиротация, сгибание), переноски.

Важно для читателя: англоязычные открытые базы и часть русскоязычных сайтов (wger, ExRx, sportwiki) во время сбора были недоступны для прямой загрузки (robots/403). Поэтому схемы баз описаны по их репозиториям на GitHub. Технические подсказки, ошибки, диапазоны повторений и замены в записях — **моя синтез-экспертиза по общепринятой тренерской практике (NSCA/ACE-уровень)**, а не цитаты. Тексты сформулированы своими словами. Утверждения с источником вынесены в разделы «Cited Findings». Всё про противопоказания — справочная информация, не медицинская рекомендация.

---

## Вопрос 1. Каталог записей (≈120 упражнений) и правила полей

### Takeaway
Ниже 121 запись, сгруппированные по 13 паттернам. У каждой записи есть id, русское и английское название, мышцы, оборудование, уровень, тип нагрузки и шаг веса, повторения, подсказки и ошибки, регрессии и прогрессии, замены по 5 сценариям, флаги и пригодность для e1RM. Утверждения о главных мышцах в ключевых паттернах подкреплены исследованиями ЭМГ и гипертрофии (Contreras 2015, Plotkin 2023, Kubo 2019, Maeo 2021). Подсказки и замены — синтез, а не цитаты.

### Cited Findings
(доказательная база для полей primary_muscles / substitution и флагов)
- Хип-траст против приседа со штангой (13 тренированных женщин, ~10ПМ). Хип-траст дал большую среднюю ЭМГ верхней (69.5% против 29.4% MVIC) и нижней (86.8% против 45.4%) порции большой ягодичной и двуглавой бедра (40.8% против 14.9%). По латеральной широкой разницы нет (99.5% против 110%) — [Contreras et al. 2015, J Appl Biomech, PubMed](https://pubmed.ncbi.nlm.nih.gov/26214739/)
- Однако 9 недель тренировок нетренированных (хип-траст n=18, присед n=16, МРТ) дали **сходный** прирост ягодичных. Присед дал больший рост квадрицепса (+3.6 см², ДИ 0.7–6.4) и приводящих (+2.5 см², ДИ 1.2–3.9). Хамстринги почти не росли ни в одной группе. ЭМГ первой сессии не предсказала гипертрофию — [Plotkin et al. 2023, Frontiers in Physiology](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1279170/full)
- Полный присед (~140° в колене) против полуприседа (90°), 10 недель. Объём приводящих +6.2%, ягодичных +6.7% (с преимуществом полного приседа), квадрицепса ~+5%, хамстрингов <1% — [Kubo et al. 2019 в обзоре Stronger By Science](https://www.strongerbyscience.com/squats-adductors/)
- По моделированию, большая приводящая мышца может давать половину и больше момента разгибания бедра в приседе. В приседаниях хамстринги растут слабо: из 25 измерений в 7 группах значимый рост был лишь дважды — [Stronger By Science, «Squats and adductors»](https://www.strongerbyscience.com/squats-adductors/)
- Сгибание ног сидя (бедро ~90°, удлинённые хамстринги) против сгибания лёжа, 12 недель, внутрисубъектный дизайн, 20 нетренированных, 5×10 на 70% 1ПМ. Общий объём хамстрингов +14.1% против +9.3%, длинная головка двуглавой +14.4% против +6.5% — [Maeo et al. 2021 (MSSE), обзор Sci-Sport](https://sci-sport.com/en/hypertrophy-and-hamstring-protection-seated-prone-leg-curl/); первичный источник — [PubMed 33009197](https://pubmed.ncbi.nlm.nih.gov/33009197/)
- Скандинавские сгибания (Nordic hamstring). Метаанализ 15 исследований (8 459 спортсменов): программы с этим упражнением снижают риск травмы хамстрингов, RR 0.49 (ДИ 0.32–0.74) — [van Dyk et al. 2019, BJSM](https://bjsm.bmj.com/content/53/21/1362.abstract). Есть повторный анализ, по которому эффект неубедителен из-за методологии (в части исследований упражнение шло в комплексе) — [Physio Network review](https://www.physio-network.com/research-reviews/thigh/why-methods-matter-in-a-meta-analysis-a-reappraisal-showed-inconclusive-injury-preventive-effect-of-nordic-hamstring-exercise/)
- Копенгагенское приведение (кластерное РКИ, 35 команд). Распространённость проблем с паховой областью 13.5% против 21.3% (OR 0.59) — [Harøy et al. 2019, BJSM](https://bjsm.bmj.com/content/53/3/150.abstract)
- «Большая тройка» Макгилла: curl-up, боковая планка, bird-dog. Схема-пирамида 5-3-1 повторений — [Harvard Health](https://www.health.harvard.edu/staying-healthy/three-moves-for-better-spine-health)
- Гакк-присед: основная нагрузка на квадрицепс. Ягодичные сильнее работают при глубоком приседе и высокой постановке стоп. Нагрузка на поясницу ниже, чем в классике, из-за опоры на спинку. Частые ошибки: подкручивание таза внизу, отрыв пяток, жёсткий замок коленей, рывки, чрезмерный вес — [Спорт Mail.ru](https://sportmail.ru/article/others/69654998/)

### Inferences

#### Справочник полей (рекомендуемая схема БД)
- `load_type`: `barbell` | `dumbbell` (вес одной гантели) | `kettlebell` | `machine_stack` | `plate_loaded` | `cable` | `bodyweight` | `bodyweight_plus` (с отягощением) | `band` | `isometric_time`.
- `increment_default` (минимальный шаг движка до округления к инвентарю пользователя):
  - штанга — 2.5 кг суммарно (блины 1.25 кг), для тяг и приседа у новичков допустимо 5 кг;
  - гантели — 1–2.5 кг на руку (в РФ залах ряды гантелей обычно идут через 2 или 2.5 кг; разборные домашние — 0.5–1.25 кг);
  - гири — 4 кг (8/12/16/20/24/28/32);
  - блок/стек — ~5 кг (бывает 2.5–10; импортные стеки 10 lb ≈ 4.5 кг);
  - плитовые тренажёры (жим ногами, гакк) — 5–10 кг суммарно (по блину на сторону);
  - собственный вес — прогресс повторениями, затем темпом, паузой, амплитудой (дефицит), рычагом и внешним весом;
  - изометрия — +5–10 с.
- `e1rm_trackable`: yes — стабильный нагружаемый лифт с малой вариабельностью техники; partial — можно считать только внутри пользователя (тренажёры: калибровка отличается между залами); no — изометрия, вес тела, баллистика.
- Диапазоны повторений по умолчанию (если в записи не указано иное):
  - базовые многосуставные со штангой: S 3–6, H 6–12, E 12–20;
  - тренажёры и изоляция: S 6–10, H 8–15, E 15–25;
  - кор: H 8–15 / 20–60 с, E 15–30 / 45–90 с.
- Флаги безопасности (enum): `knee_pain`, `patellofemoral_sensitive`, `deep_knee_flexion`, `lumbar_flexion_load`, `lumbar_extension_load`, `axial_spinal_load`, `hip_impingement_deep_flexion`, `ankle_mobility_required`, `balance_demand`, `grip_limited`, `high_eccentric_doms`, `hernia_valsalva` (натуживание; внутрибрюшное давление), `pregnancy_supine_caution`, `neck_strain`, `shoulder_mobility_required`, `wrist_load`.
- Обозначения в записях: P — primary, S — secondary, Eq — equipment, Inc — шаг, Reg/Prog — регрессия/прогрессия, Sub — замены: noBB — нет штанги, DB — дома только гантели, BW — без инвентаря, KNEE — проблемы с коленом, LB — проблемы с поясницей.

---

#### 1. SQUAT (присед, коленно-доминантный двусторонний)

**back_squat_high_bar** — Приседания со штангой на спине (высокий гриф) | Barbell Back Squat (high-bar) | aliases: «Присед», «Классические приседания», «Приседания со штангой на плечах»
- squat | compound | bilateral | intermediate (новичку — после goblet_squat) | Eq: barbell, rack
- P: квадрицепс, большая ягодичная, приводящие (большая приводящая) | S: разгибатели спины, камбаловидная, кор
- barbell, Inc 2.5 кг (новичок 5 кг) | S 3–6, H 6–12, E 12–15 | e1RM: **yes**
- Cues: гриф на трапециях; вдох и «распор» корпуса перед спуском; колени идут по линии носков; глубина — минимум параллель, если позволяет мобильность.
- Errors: колени заваливаются внутрь на подъёме; «подкрутка» таза внизу с потерей нейтрали; таз поднимается быстрее плеч.
- Reg: goblet_squat → box_squat. Prog: pause_back_squat, front_squat.
- Sub: noBB → goblet_squat / hack_squat / leg_press_45; DB → db_goblet_squat, heel_elevated_db_squat; BW → bodyweight_squat → pistol_squat; KNEE → box_squat (ограниченная глубина), belt_squat, spanish_squat; LB → belt_squat, leg_press_45, hack_squat.
- Flags: axial_spinal_load, lumbar_flexion_load (при потере нейтрали внизу), deep_knee_flexion, ankle_mobility_required, hernia_valsalva.

**back_squat_low_bar** — Приседания со штангой на спине (низкий гриф, «пауэрлифтерский присед») | Low-bar Back Squat | aliases: «Присед с низким грифом»
- squat (ближе к hinge) | compound | bilateral | intermediate–advanced | barbell, rack
- P: ягодичные, приводящие, квадрицепс | S: разгибатели спины, хамстринги
- Inc 2.5 кг | S 1–6, H 5–10 | e1RM: yes — **отдельно от high-bar**, обычно на 5–10% больше (оценка практиков, не проверено в источниках).
- Cues: гриф под остью лопатки; больший наклон корпуса; таз назад; запястья прямые.
- Errors: штанга «уезжает» на шею; гудморнинг на подъёме; боль в локтях и запястьях.
- Sub: как у back_squat_high_bar.
- Flags: axial_spinal_load, shoulder_mobility_required, lumbar_flexion_load.

**pause_back_squat** — Приседания с паузой | Paused Squat — `variant_of: back_squat_high_bar`, advanced. Inc 2.5 кг, S 2–5. e1RM: отдельный трекинг (нагрузка на ~10–15% ниже — эвристика).

**box_squat** — Приседания на ящик / к скамье (со штангой) | Box Squat | aliases: «Присед на бокс», «Присед на тумбу»
- squat | compound | bilateral | beginner–intermediate | barbell + box/bench
- P: квадрицепс, ягодичные | S: разгибатели спины
- Inc 2.5 кг | S 3–5, H 6–10 | e1RM: yes (при фиксированной высоте ящика)
- Cues: садиться под контролем, не «плюхаться»; короткая пауза без расслабления корпуса; голени ближе к вертикали.
- Errors: падение на ящик; раскачка с ящика.
- Sub: KNEE → тот же ящик повыше; BW → sit_to_stand.
- Flags: axial_spinal_load, lumbar_flexion_load (при ударе о ящик).

**front_squat** — Фронтальные приседания / Приседания со штангой на груди | Front Squat | aliases: «Фронтальный присед»
- squat | compound | bilateral | intermediate–advanced | barbell, rack
- P: квадрицепс | S: ягодичные, приводящие, верх спины, кор
- Inc 2.5 кг | S 2–5, H 5–10 | e1RM: yes (отдельно; обычно ~80–85% от back squat — эвристика практиков, без цитаты)
- Cues: локти высоко; корпус вертикально; гриф лежит на дельтах, а не в ладонях.
- Errors: локти падают и штанга катится вперёд; округление верха спины.
- Reg: goblet_squat. Sub: noBB → goblet_squat, hack_squat; KNEE → box_squat; LB → belt_squat.
- Flags: wrist_load (клин-хват), shoulder_mobility_required, axial_spinal_load, deep_knee_flexion.

**safety_bar_squat** — Приседания с безопасным грифом (SSB) | Safety Squat Bar Squat — intermediate, barbell (special bar), Inc 2.5 кг, e1RM yes (отдельно). Полезен при ограниченной мобильности плеч. Flags: axial_spinal_load. *Русское название неустоявшееся (SSB, «сейфти-бар»).*

**zercher_squat** — Приседания Зерчера (штанга в локтевых сгибах) | Zercher Squat — advanced, barbell, Inc 2.5 кг, e1RM partial. Flags: lumbar_flexion_load, боль в локтях. В приложении — только для продвинутых.

**smith_squat** — Приседания в Смите (в тренажёре Смита) | Smith Machine Squat | aliases: «Присед в машине Смита»
- squat | compound | bilateral | beginner–intermediate | smith machine
- P: квадрицепс, ягодичные | S: приводящие
- Inc 2.5 кг (вес грифа Смита зависит от зала: ~6–25 кг, есть противовесы — фиксировать у пользователя) | H 6–12 | e1RM: partial (внутри зала)
- Cues: стопы чуть впереди корпуса; спина прижата к линии движения; контролируемая глубина.
- Errors: стопы прямо под грифом (лишний сдвиг коленей вперёд); отрыв пяток.
- Flags: axial_spinal_load, knee_pain (при стопах под грифом).

**goblet_squat** — Гоблет-присед / Кубковые приседания (с гантелью или гирей у груди) | Goblet Squat | aliases: «Приседания с гантелью у груди», «Присед с гирей»
- squat | compound | bilateral | **beginner** | dumbbell или kettlebell
- P: квадрицепс, ягодичные | S: приводящие, верх спины, кор
- DB Inc 2–2.5 кг / KB 4 кг | H 8–15, E 15–20 (ограничение — вес снаряда) | e1RM: partial (полезно до ~30–40 кг)
- Cues: снаряд прижат к груди; локти между коленей внизу; грудь вверх.
- Errors: снаряд отходит от тела; пятки отрываются.
- Reg: bodyweight_squat, box_squat_bw. Prog: front_squat, back_squat_high_bar, heel_elevated_goblet_squat.
- Sub: BW → bodyweight_squat, tempo-присед; KNEE → box_squat_bw к высокой опоре; LB → goblet_squat обычно переносится (малая осевая нагрузка).
- Flags: deep_knee_flexion (опционально), hip_impingement_deep_flexion.

**db_squat** — Приседания с гантелями (в опущенных руках) | Dumbbell Squat — beginner, Inc 1–2.5 кг/рука, H 8–15, e1RM partial. Flags: grip_limited.

**heel_elevated_squat** — Приседания с поднятыми пятками («велосипедистский присед») | Heel-Elevated / Cyclist Squat — beginner–intermediate, DB/KB/barbell, P: квадрицепс (акцент). H 8–15. Хорошо при ограниченной мобильности голеностопа. Flags: patellofemoral_sensitive, deep_knee_flexion. *Название в RU неустоявшееся.*

**sumo_squat_db** — Приседания «плие» / Сумо-приседания с гантелью или гирей | Sumo/Plié Squat — beginner, DB/KB, P: приводящие, ягодичные, квадрицепс. Inc 2–4 кг. H 10–15. Cues: широкая стойка, носки развёрнуты; колени по линии стоп. Flags: hip_impingement_deep_flexion. Sub: noBB/DB — нативно.

**landmine_squat** — Приседания с лендмайном (свободный конец штанги в углу) | Landmine Squat — beginner–intermediate, barbell + landmine, Inc 2.5 кг (на конце рычаг: фактическая нагрузка меньше веса). e1RM partial. Удобен при болях в плечах.

**belt_squat** — Приседания с поясом (белт-сквот) | Belt Squat — intermediate, тренажёр или платформа с поясом, Inc 5 кг, H 8–15. P: квадрицепс, ягодичные. Без осевой нагрузки на позвоночник → основная замена при LB. e1RM partial.

**hack_squat** — Гакк-приседания (в тренажёре) | Hack Squat (machine) | aliases: «Хакк-приседания», «Гак-присед», «Присед в гакк-машине»
- squat | compound | bilateral | beginner–intermediate | hack machine (plate-loaded)
- P: квадрицепс | S: ягодичные, приводящие
- plate_loaded, Inc 5–10 кг суммарно | H 6–12, E 15–20 | e1RM: partial (тренажёры разные)
- Cues: спина и таз прижаты к спинке; полная стопа на платформе; плавный разворот внизу.
- Errors: подкрутка таза; отрыв пяток; жёсткий замок коленей; рывок вверх.
- Sub: noBB → нативно; DB → heel_elevated_squat с гантелями; BW → sissy_squat, bodyweight_squat; KNEE → leg_press_45 с ограниченной амплитудой; LB → нативно (опора спины).
- Flags: deep_knee_flexion, patellofemoral_sensitive.
- (Источник ошибок: [Спорт Mail.ru](https://sportmail.ru/article/others/69654998/))

**reverse_hack_squat** — Обратные гакк-приседания (лицом к тренажёру) | Reverse Hack Squat — `variant_of: hack_squat`, больший акцент на ягодичные и хамстринги; e1RM отдельно.

**pendulum_squat** — Маятниковый присед / Присед в маятниковом тренажёре | Pendulum Squat — intermediate, plate-loaded, P: квадрицепс; H 8–15. Сюда же как alias: V-squat machine. e1RM partial.

**leg_press_45** — Жим ногами (в тренажёре 45°) | 45° Leg Press | aliases: «Жим платформы ногами», «Жим ногами лёжа»
- squat (machine) | compound | bilateral | **beginner** | leg press (plate-loaded)
- P: квадрицепс, ягодичные | S: приводящие
- Inc 5–10 кг суммарно | S 6–10, H 8–15, E 15–25 | e1RM: partial (сильно зависит от тренажёра и амплитуды; не сравнивать с приседом)
- Cues: таз и поясница прижаты; опускать, пока таз не начал отрываться; колени по линии носков.
- Errors: отрыв таза и округление поясницы внизу; замок коленей; слишком короткая амплитуда.
- Variants (поле `variant`): постановка стоп high/low, wide/narrow.
- Sub: noBB → нативно; DB → goblet_squat, bulgarian_split_squat; BW → split_squat; KNEE → высокая постановка стоп, ограниченная амплитуда; LB → ограниченная амплитуда (без отрыва таза) или belt_squat.
- Flags: lumbar_flexion_load (отрыв таза), knee_pain (замок коленей).

**horizontal_leg_press** — Жим ногами сидя (горизонтальный, блочный) | Seated/Horizontal Leg Press — beginner, machine_stack, Inc 5 кг, H 10–15. e1RM partial.

**single_leg_press** — Жим ногами одной ногой | Single-Leg Press — `unilateral: yes`, beginner–intermediate. Inc 2.5–5 кг. Удобен при асимметрии.

**spanish_squat** — «Испанский присед» (с лентой за коленями) | Spanish Squat — beginner, band + стойка, изометрия 30–45 с или 10–15 повторений. P: квадрицепс. Используется в реабилитационном контексте при болях в сухожилии надколенника (практика физиотерапевтов, без цитаты). e1RM: no. *RU-название — калька, редкое.*

**wall_sit** — Стульчик у стены / «Стульчик» | Wall Sit — beginner, bodyweight, isometric_time, Inc +10 с. e1RM: no. Flags: patellofemoral_sensitive (при угле 90°).

**bodyweight_squat** — Приседания без веса / с собственным весом / «аир-сквот» | Bodyweight (Air) Squat — beginner, BW; прогрессия: повторения → темп 3-1-1 → пауза → goblet. E 15–30. e1RM: no.

**sit_to_stand** — Приседания на стул (вставание со стула / бокс-присед без веса) | Box Squat to Bench (Sit-to-Stand) — beginner/returner, BW. Регрессия для всех приседаний. e1RM: no.

**sissy_squat** — Сисси-присед (сисси-приседания) | Sissy Squat — intermediate–advanced, BW или тренажёр, P: квадрицепс (прямая головка). H 8–15. Flags: **patellofemoral_sensitive**, deep_knee_flexion, knee_pain. e1RM: no.

**pistol_squat** — Пистолетик (приседания на одной ноге) | Pistol Squat — `unilateral: yes`, advanced, BW. Reg: приседания на одной ноге на скамью (box pistol), с опорой TRX. Flags: balance_demand, deep_knee_flexion, ankle_mobility_required. e1RM: no.

**skater_squat** — Конькобежный присед / «Креветка» | Skater / Shrimp Squat — unilateral, intermediate–advanced, BW (+ гантели). Flags: balance_demand. *Названия в RU разнятся: «креветка» = shrimp squat.*

**cossack_squat** — Казачий присед / «Казачьи приседания» | Cossack Squat — unilateral (поочерёдно), intermediate, BW/KB. P: приводящие, квадрицепс, ягодичные. Flags: hip_impingement_deep_flexion, knee_pain.

---

#### 2. HINGE (наклон в тазобедренном суставе)

**deadlift_conventional** — Становая тяга (классическая) | Conventional Deadlift | aliases: «Становая», «Тяга с пола»
- hinge | compound | bilateral | intermediate (новичку — после rdl/kb_deadlift/trap_bar) | barbell
- P: ягодичные, хамстринги, разгибатели спины, приводящие | S: квадрицепс, трапеции, широчайшие, предплечья (хват)
- Inc 2.5–5 кг | S 1–5, H 5–8 (высокие повторения не рекомендуются из-за технической усталости) | e1RM: **yes**
- Cues: гриф над серединой стопы; «натянуть» штангу (убрать люфт) до отрыва; толкать пол ногами; гриф скользит по ногам.
- Errors: округление поясницы; таз взлетает первым; гриф уходит от ног; переразгибание наверху.
- Reg: rdl_db → kb_deadlift → trap_bar_deadlift. Prog: deficit_deadlift, pause.
- Sub: noBB → trap_bar_deadlift / kb_deadlift / rdl_db; DB → rdl_db, single_leg_rdl; BW → single_leg_rdl_bw, hip_thrust_bw, back_extension; KNEE → rdl_db (малое сгибание колена); LB → hip_thrust, cable_pull_through, back_extension (облегчённо) — по самочувствию.
- Flags: **lumbar_flexion_load**, axial_spinal_load, grip_limited, hernia_valsalva.

**sumo_deadlift** — Становая тяга сумо / в стиле сумо | Sumo Deadlift — intermediate–advanced, barbell, Inc 2.5–5 кг, S 1–5, e1RM yes (отдельно). P: ягодичные, приводящие, квадрицепс. Flags: hip_impingement_deep_flexion, lumbar_flexion_load.

**trap_bar_deadlift** — Тяга с трэп-грифом / с шестигранным (гекс) грифом | Trap/Hex Bar Deadlift — beginner–intermediate, trap bar, Inc 2.5–5 кг, S 3–6, H 6–10, e1RM yes (отдельно). Более вертикальный корпус и больше работы квадрицепса — дружелюбнее к пояснице. Flags: lumbar_flexion_load (меньше, чем в классике), grip_limited.

**deficit_deadlift** — Становая тяга с дефицита (стоя на платформе) | Deficit Deadlift — `variant_of: deadlift_conventional`, advanced.

**rack_pull** — Тяга с плинтов / Тяга из стоек (с блоков) | Rack/Block Pull — intermediate, частичная амплитуда, e1RM yes (отдельно, высоту фиксировать). Flags: axial_spinal_load.

**romanian_deadlift_bb** — Румынская тяга (со штангой) | Barbell Romanian Deadlift (RDL) | aliases: «Румынская становая тяга», «РДЛ»; **внимание**: часть источников называет её «становая тяга на прямых ногах», хотя классически это разные упражнения.
- hinge | compound | bilateral | beginner–intermediate | barbell
- P: хамстринги, большая ягодичная | S: разгибатели спины, приводящие, предплечья
- Inc 2.5 кг | S 4–6, H 6–12 | e1RM: yes
- Cues: колени чуть согнуты и зафиксированы; таз уходит назад; гриф по бёдрам; опускать до натяжения задней поверхности бедра без потери нейтрали.
- Errors: приседание вместо наклона; округление спины ради глубины; гриф далеко от ног.
- Reg: hip_hinge_drill → rdl_db. Prog: single_leg_rdl, deficit RDL.
- Sub: noBB → rdl_db, kb_deadlift; DB → rdl_db, single_leg_rdl_db; BW → single_leg_rdl_bw, nordic/slider_leg_curl, hip_thrust_bw; KNEE → нативно (малая нагрузка на колено); LB → seated_leg_curl + hip_thrust, cable_pull_through.
- Flags: lumbar_flexion_load, high_eccentric_doms.

**romanian_deadlift_db** — Румынская тяга с гантелями | Dumbbell RDL — beginner, DB Inc 1–2.5 кг/рука, H 8–15, e1RM partial. Flags: grip_limited, lumbar_flexion_load.

**stiff_leg_deadlift** — Становая тяга на прямых ногах (с пола) | Stiff-Legged Deadlift (SLDL) — intermediate, barbell. Отличие от RDL: каждое повторение начинается с пола, ноги почти прямые. *Названия в RU смешиваются с RDL — хранить как отдельные id с alias-предупреждением.* Flags: lumbar_flexion_load.

**single_leg_rdl** — Румынская тяга на одной ноге (с гантелью/гирей) | Single-Leg RDL — unilateral, intermediate, DB/KB/BW. P: хамстринги, ягодичные (+ средняя ягодичная как стабилизатор). H 8–12 на ногу. Flags: balance_demand. e1RM: no (вариабельность из-за баланса). Reg: b_stance_rdl.

**b_stance_rdl** — Румынская тяга в B-стойке (опора на носок второй ноги, «kickstand») | B-Stance / Kickstand RDL — unilateral-biased, beginner–intermediate, DB/BB. e1RM partial. *RU-название неустоявшееся.*

**kb_deadlift** — Тяга гири (становая с гирей) | Kettlebell Deadlift — beginner, KB Inc 4 кг, H 8–15. Лучший учебный hinge для новичка.

**hip_hinge_drill** — Наклоны с палкой вдоль спины (обучение «шарниру») | Dowel Hip Hinge — beginner, BW, технический дрилл. e1RM: no. Не силовое — `is_drill: true`.

**kettlebell_swing** — Махи гирей (двумя руками) | Kettlebell Swing (Russian) | aliases: «Свинг гири»
- hinge (баллистика) | compound | bilateral | intermediate | KB
- P: ягодичные, хамстринги | S: разгибатели спины, кор, хват
- Inc 4 кг | E 10–20 повторений / по времени | e1RM: **no**
- Cues: движение тазом, а не приседанием; гиря «летит» от толчка бёдер; наверху — напряжённые ягодицы и пресс.
- Errors: приседание; подъём гири руками; переразгибание поясницы наверху.
- Flags: lumbar_flexion_load, lumbar_extension_load.

**good_morning** — Гуд-морнинг / Наклоны со штангой на плечах («Доброе утро») | Good Morning — intermediate–advanced, barbell, Inc 2.5 кг, H 6–12, e1RM partial. Flags: **lumbar_flexion_load**, axial_spinal_load. Новичкам не предлагать по умолчанию.

**cable_pull_through** — Протяжка каната между ног (пулл-тру на нижнем блоке) | Cable Pull-Through — beginner, cable, Inc 5 кг (стек), H 12–20. Низкая осевая нагрузка → замена при LB. e1RM: no/partial.

**back_extension_45** — Гиперэкстензия (на тренажёре 45° / горизонтальном) | 45° Back Extension / Hyperextension | aliases: «Гипер», «Разгибание спины»
- hinge / hip_extension | compound | bilateral | beginner | бенч для гиперэкстензии (+ блин/гантель)
- P: разгибатели спины, ягодичные, хамстринги (зависит от варианта) | S: —
- bodyweight_plus: повторения → блин 5–10–20 кг у груди | H 10–20 | e1RM: no
- Variants: `glute_bias` (округлённый верх спины, движение тазом, носки в стороны), `erector_bias` (сгибание и разгибание позвоночника).
- Cues: опора у паха, не на животе; не переразгибаться наверху; контроль спуска.
- Errors: рывки; переразгибание поясницы; слишком высокая подушка, мешающая наклону.
- Sub: BW → bird_dog, glute_bridge; DB → rdl_db.
- Flags: lumbar_extension_load (переразгибание), lumbar_flexion_load (erector-вариант).
- Source (RU-наименования и вариант на ягодицы): [Mentoday — гиперэкстензия с округлённой спиной](https://www.mentoday.ru/fitness/training/giperekstenziya-so-skruglennoy-spinoy-dlya-yagodic-tehnika-i-chastye-oshibki/), [Т—Ж](https://t-j.ru/what-is-hyperextension/)

**reverse_hyperextension** — Обратная гиперэкстензия | Reverse Hyperextension — intermediate, специальный тренажёр или скамья (BW / ремень с весом), H 10–20. P: ягодичные, хамстринги. Flags: lumbar_extension_load. Источник названия: [Mentoday](https://mentoday.ru/fitness/training/obratnaya-giperekstenziya-6-variantov-vypolneniya-i-chastye-oshibki).

---

#### 3. LUNGE / SINGLE-LEG (выпады, на одной ноге)

**bulgarian_split_squat** — Болгарские выпады / Болгарский сплит-присед (с гантелями) | Bulgarian Split Squat (DB) | aliases: «Болгарские приседания», «Болгарский присед», «Выпады с ногой на скамье»
- lunge | compound | **unilateral** | intermediate | dumbbells + bench
- P: квадрицепс, большая ягодичная, приводящие | S: средняя ягодичная (стабилизация), хамстринги
- DB Inc 1–2.5 кг/рука | H 6–12, E 12–20 на ногу | e1RM: partial (баланс и хват ограничивают)
- Variants: `torso_upright` (квадрицепс) / `torso_lean` (ягодичные) — поле variant, а не отдельный id.
- Cues: передняя стопа достаточно далеко; вес на передней ноге; задняя нога — только опора; опускаться вертикально.
- Errors: слишком короткая стойка (колено уходит далеко вперёд, отрыв пятки); толчок задней ногой; заваливание колена внутрь.
- Reg: split_squat → поддержка рукой. Prog: штанга, дефицит под передней ногой.
- Sub: noBB/DB → нативно; BW → BSS без веса, медленный темп; KNEE → reverse_lunge, step_up (низкая тумба); LB → нативно с гантелями (осевая нагрузка низкая) или smith_split_squat.
- Flags: balance_demand, grip_limited, deep_knee_flexion, hip flexor stretch задней ноги.
- RU-название и происхождение — [Mentoday](https://www.mentoday.ru/fitness/fitness-faq/rumynskaya-tyaga-bolgarskiy-prised-francuzskiy-zhim-otkuda-u-uprazhneniy-nacionalnye-nazvaniya/); вариант «Болгарский сплит-присед» — [Лайфхакер](https://lifehacker.ru/kak-nakachat-nogi/).

**bulgarian_split_squat_bb** — Болгарские выпады со штангой | Barbell BSS — `variant_of: bulgarian_split_squat`, advanced, Inc 2.5 кг, e1RM yes. Flags: balance_demand, axial_spinal_load.

**smith_split_squat** — Выпады/сплит-присед в Смите | Smith Split Squat — beginner–intermediate, Inc 2.5 кг, e1RM partial. Меньше требований к балансу.

**split_squat** — Сплит-присед / Статические выпады (выпады на месте) | Split Squat — beginner, BW/DB, H 8–15 на ногу. Регрессия для всех выпадов.

**front_foot_elevated_split_squat** — Сплит-присед с передней ногой на платформе | FFE Split Squat — `variant_of: split_squat`, увеличенная амплитуда.

**forward_lunge** — Выпады вперёд (с гантелями) | Forward Lunge — intermediate (торможение сложнее), DB, Inc 1–2.5 кг/рука. Flags: knee_pain (ударное торможение), balance_demand.

**reverse_lunge** — Выпады назад / Обратные выпады | Reverse Lunge — beginner–intermediate, DB/BW/BB. **Дружелюбнее к колену**, чем выпад вперёд (практическая эвристика; без цитаты). H 8–12. Prog: deficit_reverse_lunge.

**deficit_reverse_lunge** — Выпады назад с платформы | Deficit Reverse Lunge — `variant_of: reverse_lunge`, больший акцент на ягодичные.

**walking_lunge** — Выпады в ходьбе / шагающие выпады | Walking Lunge — intermediate, DB/BB/BW. H 10–20 шагов на ногу. e1RM: no. Flags: balance_demand, grip_limited.

**barbell_lunge** — Выпады со штангой (на спине) | Barbell Lunge — intermediate–advanced, Inc 2.5 кг, e1RM partial. Flags: axial_spinal_load, balance_demand.

**lateral_lunge** — Боковые выпады / Выпады в сторону | Lateral Lunge — beginner–intermediate, BW/DB/KB, P: приводящие, ягодичные, квадрицепс. Flags: knee_pain (при валгусе), hip_impingement_deep_flexion.

**curtsy_lunge** — Перекрёстные выпады / «Реверанс» | Curtsy Lunge — beginner–intermediate, BW/DB, P: ягодичные (+ средняя). Flags: knee_pain (скручивающий момент) — не предлагать при KNEE.

**step_up** — Зашагивания на тумбу/скамью (с гантелями) | Step-Up | aliases: «Подъёмы на платформу», «Шаги на скамью»
- lunge | compound | unilateral | beginner | box/bench, DB
- P: квадрицепс, ягодичные | Inc 1–2.5 кг/рука | H 8–12 на ногу | e1RM partial
- Cues: работает верхняя нога, нижняя не отталкивается; полная стопа на тумбе; высота — бедро не выше параллели на старте.
- Errors: толчок нижней ногой; слишком высокая тумба (округление таза).
- Sub: KNEE → низкая тумба (15–20 см); BW → без веса.
- Flags: balance_demand.

**lunge_bodyweight** — Выпады без веса | Bodyweight Lunge — beginner, BW, `variant_of: reverse_lunge/forward_lunge` (поле `load: bodyweight`). e1RM: no.

---

#### 4. HIP EXTENSION / GLUTE (ягодичные)

**hip_thrust_bb** — Ягодичный мост со штангой / Хип-траст (лопатки на скамье) | Barbell Hip Thrust | aliases: «Хип-траст», «Ягодичный мостик со штангой», «Тазовый подъём»
- hip_extension | compound | bilateral | beginner–intermediate | barbell + bench (+ накладка на гриф)
- P: большая ягодичная | S: хамстринги, квадрицепс, приводящие
- Inc 2.5–5 кг | S 5–8, H 8–15, E 15–25 | e1RM: yes (если опора и амплитуда стандартны)
- Cues: нижний край лопаток на скамье; голени вертикальны в верхней точке; подбородок к груди, рёбра вниз; пауза 1 с наверху.
- Errors: подъём за счёт переразгибания поясницы; стопы слишком далеко (уходит в хамстринги) или близко (уходит в квадрицепс); неполное разгибание.
- Reg: glute_bridge_bw → hip_thrust_bw. Prog: пауза, single_leg_hip_thrust.
- Sub: noBB → hip_thrust_db / hip_thrust_machine / smith_hip_thrust; DB → hip_thrust_db; BW → single_leg_hip_thrust; KNEE → нативно (малое движение колена); LB → нативно при контроле рёбер (осевой нагрузки нет).
- Flags: lumbar_extension_load (переразгибание), давление грифа на таз (нужна накладка), pregnancy_supine_caution.
- EMG и гипертрофия: см. Cited Findings ([Contreras 2015](https://pubmed.ncbi.nlm.nih.gov/26214739/); [Plotkin 2023](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1279170/full)).
- RU-именование (fitwill использует «Ягодичный мост со штангой» для хип-траста) — [fitwill](https://fitwill.app/ru/exercise/0058/barbell-lying-lifting-on-hip/), [«Ягодичный мост в Смите»](https://fitwill.app/ru/exercise/3110/smith-hip-thrust/).

**smith_hip_thrust** — Ягодичный мост в Смите | Smith Hip Thrust — `variant_of: hip_thrust_bb`, beginner, Inc 2.5 кг, e1RM partial.

**hip_thrust_machine** — Ягодичный мост в тренажёре / Тренажёр для ягодичного моста | Machine Hip Thrust (Glute Drive) — beginner, plate/stack, Inc 5 кг, H 8–15, e1RM partial.

**hip_thrust_db** — Ягодичный мост с гантелью (лопатки на скамье) | Dumbbell Hip Thrust — beginner, DB/KB, Inc 2.5 кг. Ограничение по весу гантели → быстрее переходить на одну ногу.

**glute_bridge_bb** — Ягодичный мостик со штангой лёжа на полу | Barbell Glute Bridge — beginner–intermediate, Inc 2.5–5 кг, меньшая амплитуда, e1RM yes (отдельно от hip thrust). [fitwill/lyfta](https://www.lyfta.app/ru/exercise/barbell-glute-bridge-83v)

**glute_bridge_bw** — Ягодичный мостик (без веса, лёжа на полу) | Glute Bridge — beginner, BW, H 12–25. Регрессия для всего паттерна. Flags: pregnancy_supine_caution.

**single_leg_hip_thrust** — Ягодичный мост на одной ноге (лопатки на скамье) | Single-Leg Hip Thrust / Bridge — unilateral, intermediate, BW/DB. Основная BW-замена хип-траста.

**hip_thrust_bw** — Ягодичный мост от скамьи без веса | Bodyweight Hip Thrust — beginner, `variant_of: hip_thrust_bb` (load: bodyweight).

**frog_pump** — «Лягушка» / Ягодичный мостик стопы вместе, колени врозь | Frog Pump — beginner, BW/DB, E 20–50. e1RM: no. *RU-название неустоявшееся.*

**cable_kickback** — Отведение ноги назад на нижнем блоке (кикбэк) | Cable Glute Kickback | aliases: «Махи ногой назад в кроссовере»
- hip_extension | isolation | unilateral | beginner | cable + манжета
- P: большая ягодичная | S: хамстринги | Inc 2.5–5 кг (стек) | H 10–20 | e1RM: no
- Cues: корпус наклонён и неподвижен; движение в тазобедренном суставе, не в пояснице.
- Errors: переразгибание поясницы; раскачка корпусом.
- Sub: BW → quadruped_kickback; DB → hip_thrust_db.
- Flags: lumbar_extension_load.

**glute_kickback_machine** — Отведение ноги назад в тренажёре (ягодичный тренажёр) | Machine Glute Kickback — beginner, stack, Inc 5 кг, H 10–15, e1RM partial.

**quadruped_kickback** — Махи ногой назад на четвереньках (с лентой/утяжелителем) | Donkey Kick / Quadruped Hip Extension — beginner, BW/band, E 15–25. e1RM: no.

---

#### 5. KNEE EXTENSION (разгибание колена)

**leg_extension** — Разгибание ног (сидя) в тренажёре | Leg Extension | aliases: «Разгибания ног сидя», «Экстензия»
- knee_extension | isolation | bilateral (можно по одной) | beginner | leg extension machine
- P: квадрицепс (прямая мышца бедра включена, так как бедро согнуто сидя) | S: —
- Inc 5 кг (стек), на одну ногу 2.5 | S 8–12, H 10–15, E 15–25 | e1RM: partial
- Cues: ось тренажёра на уровне коленного сустава; валик над голеностопом; пауза наверху; медленно вниз.
- Errors: забрасывание веса рывком; таз отрывается от сиденья; неправильная настройка оси.
- Sub: noBB → нативно; DB → heel_elevated_squat, sissy_squat (assisted); BW → reverse_nordic, sissy_squat; KNEE → ограниченная амплитуда (часто 90°→45° переносится лучше; индивидуально), spanish_squat, изометрия; LB → нативно.
- Flags: patellofemoral_sensitive (концевая амплитуда под нагрузкой), knee_pain; после операций на ПКС — только по указанию специалиста.

**single_leg_extension** — Разгибание одной ноги в тренажёре | Single-Leg Extension — `variant_of: leg_extension`, unilateral.

**reverse_nordic** — Обратные скандинавские сгибания / «Обратный нордик» | Reverse Nordic Curl — intermediate, BW (+ band assist), H 6–12. P: квадрицепс (прямая мышца). Flags: patellofemoral_sensitive, knee_pain, deep_knee_flexion. e1RM: no. *RU-название — калька.*

---

#### 6. KNEE FLEXION (сгибание ног, хамстринги)

**lying_leg_curl** — Сгибание ног лёжа (в тренажёре) | Lying (Prone) Leg Curl | aliases: «Сгибания ног в тренажёре лёжа»
- knee_flexion | isolation | bilateral | beginner | lying leg curl machine
- P: хамстринги (короткая и длинная головка двуглавой, полусухожильная, полуперепончатая) | S: икроножная
- Inc 2.5–5 кг | S 6–10, H 8–15, E 15–20 | e1RM: partial
- Cues: таз прижат к скамье; ось сустава совпадает с осью тренажёра; контролируемый негатив.
- Errors: таз поднимается (поясница прогибается); рывки; неполная амплитуда.
- Sub: noBB → нативно; DB → db_leg_curl (гантель между стоп, лёжа) или rdl_db; BW → slider_leg_curl, nordic_curl (продвинутые); KNEE → обычно переносится (подбирать амплитуду); LB → seated_leg_curl.
- Flags: lumbar_extension_load (при отрыве таза), судороги икроножной.

**seated_leg_curl** — Сгибание ног сидя (в тренажёре) | Seated Leg Curl
- то же, beginner, stack Inc 5 кг; H 8–15; e1RM partial.
- Рекомендовать по умолчанию для гипертрофии хамстрингов: [Maeo 2021](https://sci-sport.com/en/hypertrophy-and-hamstring-protection-seated-prone-leg-curl/) (большой прирост на удлинённых мышцах).
- Flags: — (поясница нагружена минимально).

**standing_leg_curl** — Сгибание ноги стоя (в тренажёре или на нижнем блоке) | Standing Single-Leg Curl — unilateral, beginner, Inc 2.5–5 кг, H 10–15.

**db_leg_curl** — Сгибание ног с гантелью лёжа | Dumbbell Lying Leg Curl — beginner–intermediate, DB, Inc 1–2.5 кг. Неудобная фиксация → `e1rm: no`. Домашняя замена.

**nordic_curl** — Скандинавские сгибания / Нордические сгибания («скандинавские скручивания» у Лайфхакера) | Nordic Hamstring Curl
- knee_flexion (эксцентрика) | isolation | bilateral | advanced (эксцентрическая версия — intermediate) | BW, фиксация стоп (партнёр, лавка, ремень)
- P: хамстринги (особенно полусухожильная) | H 3–8 (эксцентрика), прогресс — амплитудой (угол падения) и замедлением
- e1RM: no | Reg: с лентой-ассистом, амплитуда до упора руками.
- Cues: тело прямое от колен до головы; сопротивляться падению как можно дольше; ловить себя руками.
- Errors: сгиб в тазобедренном суставе (таз назад); слишком большой объём с нуля → сильная крепатура.
- Flags: **high_eccentric_doms**, knee_pain (давление на колени — подложить мат).
- Evidence: [van Dyk 2019](https://bjsm.bmj.com/content/53/21/1362.abstract) (оспорено: [Physio Network](https://www.physio-network.com/research-reviews/thigh/why-methods-matter-in-a-meta-analysis-a-reappraisal-showed-inconclusive-injury-preventive-effect-of-nordic-hamstring-exercise/)); RU-название — [Лайфхакер](https://lifehacker.ru/kak-nakachat-nogi/).

**glute_ham_raise** — Подъёмы на GHD (глют-хэм рейз) / Сгибание на GHD | Glute-Ham Raise — advanced, GHD, BW+, H 5–10. e1RM: no. «Подъёмы корпуса на GHD» — [Лайфхакер](https://lifehacker.ru/kak-nakachat-nogi/).

**slider_leg_curl** — Сгибание ног в мостике со скольжением (слайдеры, полотенце или фитбол) | Slider / Swiss Ball Leg Curl | aliases: «Скольжение ногами по полу в мостике» ([Лайфхакер](https://lifehacker.ru/kak-nakachat-nogi/)), «Сгибание ног на фитболе»
- knee_flexion + hip_extension | beginner–intermediate | BW | H 8–15, затем на одной ноге. e1RM: no.
- Основная домашняя замена сгибаний в тренажёре.

---

#### 7. CALF (икры)

**standing_calf_raise** — Подъём на носки стоя (в тренажёре) | Standing Calf Raise (machine) | aliases: «Подъёмы на икры стоя»
- calf | isolation | bilateral | beginner | machine / smith / BB
- P: икроножная | S: камбаловидная
- Inc 5 кг | H 8–15, E 15–25 | e1RM: partial
- Cues: полная амплитуда с растяжением внизу; пауза 1–2 с внизу (убирает пружинящий эффект); колени прямые, но не в замке.
- Errors: пружинящие короткие повторения; сгибание коленей для «помощи».
- Sub: noBB → нативно; DB → single_leg_calf_raise_db; BW → single_leg_calf_raise на ступеньке; KNEE → seated_calf_raise; LB → seated_calf_raise или подъёмы на носки в жиме ногами (без осевой нагрузки).
- Flags: axial_spinal_load (тренажёр с плечевыми упорами), ахиллово сухожилие.

**seated_calf_raise** — Подъём на носки сидя | Seated Calf Raise — beginner, plate/stack, P: **камбаловидная** (при согнутом колене икроножная укорочена). Inc 5 кг, H 10–20. Подъёмы на носки сидя — [Лайфхакер](https://lifehacker.ru/kak-nakachat-nogi/).

**leg_press_calf_raise** — Подъём на носки в тренажёре для жима ногами | Leg Press Calf Raise — beginner, Inc 5–10 кг. Flags: следить, чтобы стопа не соскользнула с платформы (флаг `safety_slip`).

**smith_calf_raise** — Подъём на носки в Смите | Smith Calf Raise — `variant_of: standing_calf_raise`.

**single_leg_calf_raise** — Подъём на носок на одной ноге (с гантелью, на ступеньке) | Single-Leg Calf Raise — unilateral, beginner, BW/DB, Inc 1–2.5 кг. Основная домашняя версия. Источник названия: [Лайфхакер](https://lifehacker.ru/kak-nakachat-nogi/).

**donkey_calf_raise** — «Ослик» / Подъём на носки в наклоне | Donkey Calf Raise — intermediate, тренажёр или партнёр, Inc 5 кг.

**tibialis_raise** — Подъём носков (на переднюю большеберцовую), стоя у стены | Tibialis Raise — beginner, BW/тренажёр/гиря, E 15–25. `movement_pattern: ankle_dorsiflexion` (предлагаю добавить в enum). e1RM: no.

---

#### 8. HIP ADDUCTION (приводящие)

**hip_adduction_machine** — Сведение ног в тренажёре (сидя) | Hip Adduction Machine | aliases: «Приведение ног в тренажёре», «Сведения на тренажёре»
- hip_adduction | isolation | bilateral | beginner | adductor machine
- P: приводящие (длинная, короткая, большая, тонкая) | Inc 5 кг | H 10–20 | e1RM partial
- Cues: таз прижат к спинке; контроль разведения (растяжение); без рывков.
- Errors: рывки; слишком широкая стартовая амплитуда (риск растяжения у новичка).
- Sub: DB → sumo_squat_db, lateral_lunge; BW → copenhagen_plank (короткий рычаг), сжатие мяча коленями; KNEE → нативно (подушки выше колена) или cable_hip_adduction; LB → нативно.
- Flags: паховая боль/грыжа (hernia_valsalva), растяжение приводящих.
- Названия «Приведение ног», «Сведения на тренажёре», «Сжатие мяча ногами» — [Лайфхакер](https://lifehacker.ru/kak-nakachat-nogi/).

**cable_hip_adduction** — Приведение ноги на нижнем блоке стоя | Cable Hip Adduction — unilateral, beginner, Inc 2.5–5 кг.

**copenhagen_plank** — Копенгагенская планка / Копенгагенские приведения | Copenhagen Adduction / Plank — intermediate (длинный рычаг — advanced), BW, isometric 10–30 с или 5–12 повторений. Reg: опора коленом (короткий рычаг). Evidence: [Harøy 2019](https://bjsm.bmj.com/content/53/3/150.abstract). Flags: knee_pain (при опоре стопой длинным рычагом нагружается медиальная связка), wrist/shoulder (опора на предплечье). e1RM: no.

**ball_squeeze** — Сжатие мяча (подушки) коленями лёжа | Adductor Ball Squeeze — beginner/returner, изометрия. e1RM: no.

---

#### 9. HIP ABDUCTION (отводящие)

**hip_abduction_machine** — Разведение ног в тренажёре (сидя) | Hip Abduction Machine | aliases: «Отведение бедра в тренажёре», «Разведения ног сидя»
- hip_abduction | isolation | bilateral | beginner | abductor machine
- P: средняя и малая ягодичные, напрягатель широкой фасции | S: верхняя порция большой ягодичной (при наклоне корпуса вперёд — практическая эвристика)
- Inc 5 кг | H 12–20, E 20–30 | e1RM partial
- Variants: `torso_lean_forward` / `upright`.
- Sub: BW/DB → side_lying_hip_abduction, banded_lateral_walk; cable → cable_hip_abduction.

**cable_hip_abduction** — Отведение ноги в сторону на нижнем блоке | Cable Hip Abduction — unilateral, beginner, Inc 2.5–5 кг.

**side_lying_hip_abduction** — Отведение ноги лёжа на боку | Side-Lying Hip Abduction — beginner, BW/утяжелители/лента, E 15–30. e1RM: no.

**banded_lateral_walk** — Ходьба в сторону с резинкой («монстр-шаги») | Banded Lateral Walk / Monster Walk — beginner, band, E 10–20 шагов. Прогресс — жёсткость ленты (enum: light/medium/heavy; не кг). e1RM: no.

**clamshell** — «Ракушка» (отведение колена лёжа на боку с резинкой) | Clamshell — beginner, band, E 15–25. e1RM: no.

---

#### 10. CORE — ANTI-EXTENSION (антиразгибание)

**plank** — Планка (на предплечьях) | Front Plank | aliases: «Классическая планка»
- core_anti_extension | bilateral | beginner | BW | isometric_time Inc +5–10 с → затем вариации (блин на спину, RKC-планка с максимальным напряжением, long-lever) | 20–60 с | e1RM: no
- Cues: прямая линия от головы до пяток; рёбра вниз, ягодицы напряжены; дышать.
- Errors: провис поясницы; таз задран; задержка дыхания.
- Reg: планка с колен, планка у стены/скамьи. Prog: rkc_plank, body_saw, ab_wheel_rollout.
- Flags: lumbar_extension_load (при провисе), wrist_load (на прямых руках), hernia_valsalva, pregnancy (поздние сроки — индивидуально).

**rkc_plank** — Планка RKC (с максимальным напряжением) | RKC Plank — `variant_of: plank`, intermediate, 10–20 с.

**ab_wheel_rollout** — Раскатка ролика для пресса / Пресс-ролик | Ab Wheel Rollout | aliases: «Ролик для пресса», «Колесо для пресса»
- core_anti_extension | intermediate (с колен) / advanced (стоя) | ab wheel | H 6–15 | e1RM: no
- Cues: таз подкручен (задний наклон); раскатывать только до точки, где спина ещё не прогибается.
- Errors: прогиб поясницы в дальней точке; движение тазом вместо плеч.
- Reg: раскатка к стене (ограничить амплитуду), stability_ball_rollout. Prog: стоя.
- Flags: **lumbar_extension_load**, shoulder.

**stability_ball_rollout** — Раскатка на фитболе / «Пила» на фитболе | Stability Ball Rollout / Body Saw — beginner–intermediate. e1RM: no.

**dead_bug** — «Мёртвый жук» | Dead Bug — beginner, BW (+ лента/гантель), H 6–12 на сторону. Отличная базовая регрессия для анти-экстензии. Flags: — (низкий риск).

**hollow_body_hold** — «Лодочка» на спине / Холлоу-холд (полое тело) | Hollow Body Hold — intermediate, isometric 15–45 с. Flags: lumbar_extension_load (если поясница отрывается от пола). *Название «лодочка» в RU используют и для упражнения на животе (супермен) — неоднозначность, хранить alias с пометкой.*

**mcgill_curl_up** — Модифицированные скручивания Макгилла (curl-up) | McGill Curl-Up — beginner, BW, 5-3-1 удержания по 8–10 с. Источник: [Harvard Health](https://www.health.harvard.edu/staying-healthy/three-moves-for-better-spine-health). Паттерн: core_anti_extension / flexion-light. Подходит при LB. *RU-название неустоявшееся.*

---

#### 11. CORE — ANTI-ROTATION / ANTI-LATERAL FLEXION

**pallof_press** — Жим Паллофа / Паллоф-пресс | Pallof Press
- core_anti_rotation | beginner | cable или band | Inc 2.5–5 кг (стек) / жёсткость ленты | H 8–12 на сторону, или изометрия 10–30 с | e1RM: no
- Cues: стоять боком к блоку; выжать рукоять перед грудью и не дать корпусу повернуться; таз и плечи — квадратом.
- Errors: поворот корпуса; стоять слишком близко к блоку (нет нагрузки).
- Reg: на коленях → half-kneeling. Prog: в стойке выпада, с шагом.
- Sub: BW → bird_dog, side_plank; DB → suitcase_carry.

**side_plank** — Боковая планка | Side Plank — beginner–intermediate, BW, 15–45 с на сторону. Reg: на коленях. Prog: с отведением ноги, Copenhagen. Source: [Harvard Health](https://www.health.harvard.edu/staying-healthy/three-moves-for-better-spine-health). Flags: плечо (опора).

**bird_dog** — «Птица-собака» / Bird-dog (на четвереньках, подъём противоположных руки и ноги) | Bird Dog — beginner, BW, 6–10 на сторону с удержанием. [Harvard Health](https://www.health.harvard.edu/staying-healthy/three-moves-for-better-spine-health). Подходит при LB. *RU-названия разнятся: «Птица-собака», «Охотничья собака», «Bird-dog».*

**cable_woodchop** — Дровосек на блоке (рубка дров) | Cable Woodchop (high-to-low / low-to-high) — intermediate, cable, Inc 2.5–5 кг. Паттерн: core_rotation (предлагаю отдельный enum). Flags: lumbar rotation under load.

**landmine_rotation** — Повороты с лендмайном («радуга») | Landmine Rotation / Rainbow — intermediate–advanced, core_rotation. Flags: lumbar rotation.

**russian_twist** — Русские скручивания / Русский твист | Russian Twist — beginner–intermediate, BW/блин/медбол. Паттерн: core_rotation + flexion. Flags: **lumbar_flexion_load** + rotation (не предлагать при LB). Происхождение названия неясно — [Mentoday](https://www.mentoday.ru/fitness/fitness-faq/rumynskaya-tyaga-bolgarskiy-prised-francuzskiy-zhim-otkuda-u-uprazhneniy-nacionalnye-nazvaniya/).

---

#### 12. CORE — FLEXION (сгибание туловища)

**crunch** — Скручивания (на полу) | Crunch | aliases: «Кранчи», «Классические скручивания»
- core_flexion | isolation | beginner | BW (+ блин) | H 12–25 | e1RM: no
- Cues: поднимать верх спины, скручивая рёбра к тазу; не тянуть голову руками; выдох наверху.
- Errors: рывки за шею; подъём всего корпуса за счёт сгибателей бедра.
- Flags: lumbar_flexion_load (повторяющаяся флексия — осторожно при грыже диска), neck_strain.
- Sub: LB → mcgill_curl_up, dead_bug.

**cable_crunch** — Скручивания на верхнем блоке стоя на коленях («Молитва») | Kneeling Cable Crunch | aliases: «Молитва», «Скручивания с канатом» — beginner–intermediate, cable, Inc 5 кг, H 10–15. e1RM: partial. Flags: lumbar_flexion_load. *Alias «Молитва» — разговорный, широко используемый.*

**machine_crunch** — Скручивания в тренажёре | Ab Crunch Machine — beginner, stack, Inc 5 кг. e1RM partial.

**decline_situp** — Подъёмы корпуса на наклонной скамье | Decline Sit-Up — intermediate, BW/блин, H 10–20. Flags: lumbar_flexion_load, hip flexor dominance.

**reverse_crunch** — Обратные скручивания | Reverse Crunch — beginner–intermediate, BW, H 10–20. Cue: подкручивать таз, а не махать ногами.

**lying_leg_raise** — Подъём ног лёжа | Lying Leg Raise — beginner–intermediate, BW. Flags: lumbar_extension_load (поясница отрывается от пола), hip flexor dominance.

**hanging_knee_raise** — Подъём коленей в висе (на турнике или в упоре на брусьях — «капитанский стул») | Hanging Knee Raise / Captain's Chair — beginner–intermediate, H 8–15. Flags: grip_limited, плечо.

**hanging_leg_raise** — Подъём прямых ног в висе | Hanging Leg Raise — advanced, H 6–12. Flags: grip_limited, lumbar_extension_load (раскачка).

---

#### 13. CARRY (переноски)

**farmers_walk** — Прогулка фермера / Фермерская прогулка | Farmer's Walk / Carry
- carry | compound | bilateral | beginner–intermediate | DB/KB/farmer handles/trap bar
- P: хват (предплечья), трапеции, кор | S: ягодичные, икры
- Inc 2–4 кг на руку / по дистанции (м) или по времени (с) | 20–40 м × 2–4 | e1RM: no (трекинг: кг × метры)
- Cues: высокая грудь, плечи вниз; короткие быстрые шаги; не раскачиваться.
- Errors: сутулость; спешка с перекосом.
- Flags: grip_limited, axial_spinal_load (тяжёлые веса).

**suitcase_carry** — Переноска чемодана (с одной гантелью/гирей) | Suitcase Carry — beginner, unilateral load, P: косые мышцы живота, квадратная мышца поясницы (anti-lateral flexion). Подходит как замена pallof_press дома.

**front_rack_carry** — Переноска гирь в фронтальной позиции / Гоблет-переноска | Front Rack / Goblet Carry — intermediate, KB/DB, core_anti_extension-доминанта.

**overhead_carry** — Переноска над головой | Overhead Carry (Waiter's walk — одной рукой) — intermediate–advanced. Flags: shoulder_mobility_required.

Итого: 121 запись (включая ~15 записей-вариантов с `variant_of`).

#### Правило «отдельный id или поле variant»
Отдельный id, если выполняется **хотя бы одно** из условий:
1. Меняется тип снаряда (BB против DB против машины) — меняется шаг веса и округление.
2. Вес в рабочих подходах систематически отличается больше чем на ~10% (high-bar и low-bar, front и back, conventional и sumo, hip thrust и glute bridge) — иначе ломается e1RM и двойная прогрессия.
3. Меняется паттерн или профиль флагов (RDL против SLDL; выпад вперёд против выпада назад — разный риск для колена).

Поле `variant` (без отдельной истории e1RM или с общей), если меняется только постановка стоп или ширина (жим ногами high/low/wide), наклон корпуса (BSS upright/lean), угол (гиперэкстензия glute/erector) или темп/пауза (лучше отдельное поле `tempo`).

Для пауз и дефицитов — `variant_of` с отдельным трекингом, но общей заменой.

#### Важное для движка замен
- Замена ищется сначала по `movement_pattern`, затем по пересечению `primary_muscles`, затем фильтруется по `equipment_available` и `flags`, не пересекающимся с жалобами пользователя.
- Фиксированные пять сценариев (noBB, DB, BW, KNEE, LB) хранятся в каждой записи как явные ссылки на id — это детерминированно и проверяемо (подходит для rule-based движка).

### Gaps
- Не удалось загрузить ExRx, sportwiki.to и wger API (robots/403). Подсказки и ошибки — авторский синтез, их стоит проверить методистом.
- Нет прямых источников для численных эвристик: low-bar на 5–10% тяжелее high-bar, front ≈ 80–85% от back, «выпад назад дружелюбнее к колену», «акцент абдукции на большую ягодичную при наклоне». Это практические эвристики.
- Не найдено устоявшихся русских названий для: B-stance RDL, Spanish squat, Frog pump, Reverse Nordic, McGill curl-up, Safety bar squat, Pendulum squat — отмечены как неустоявшиеся.
- Конкретный вес грифа тренажёра Смита и шаг стека в конкретных залах — переменные. Их нужно хранить в профиле инвентаря пользователя.

---

## Вопрос 2. Стандартные русские названия и расхождения

### Takeaway
Ядро русских названий устойчиво: «Приседания со штангой на спине/груди», «Жим ногами», «Гакк-приседания», «Румынская тяга», «Становая тяга», «Болгарские выпады», «Сгибание ног лёжа/сидя», «Разгибание ног», «Подъём на носки стоя/сидя», «Гиперэкстензия», «Ягодичный мост». Расхождения есть в трёх местах: (1) «ягодичный мост» используют и для хип-траста, и для мостика с пола; (2) «тяга на прямых ногах» путают с румынской; (3) у ряда англоязычных калек нет устоявшегося перевода.

### Cited Findings
- «Румынская тяга» названа по румынскому тяжелоатлету Нику Владу. «Болгарский сплит-присед» — по болгарской сборной по тяжёлой атлетике 1970-х (атрибуция по популярной статье, историческая достоверность не подтверждена). Происхождение «русского твиста» не подтверждено — [Mentoday](https://www.mentoday.ru/fitness/fitness-faq/rumynskaya-tyaga-bolgarskiy-prised-francuzskiy-zhim-otkuda-u-uprazhneniy-nacionalnye-nazvaniya/)
- Список имён в обзоре Лайфхакера: «Приседания со штангой на спине», «Приседания со штангой на груди», «Выпады», «Жим ногами в тренажёре», «Разгибание ног в тренажёре», «Гакк-приседания», «Болгарский сплит-присед», «Сгибание ног в тренажёре», «Становая тяга», «Подъёмы корпуса на GHD», «Румынская становая», «Скандинавские скручивания», «Скольжение ногами по полу в мостике», «Приведение ног», «Копенгагенские приведения», «Сведения на тренажёре», «Сжатие мяча ногами», «Подъёмы на носок на одной ноге», «Подъёмы на носки стоя/сидя» — [Лайфхакер](https://lifehacker.ru/kak-nakachat-nogi/)
- «Гакк-приседания», «гакк-машина», «гакк тренажёр» — [Спорт Mail.ru](https://sportmail.ru/article/others/69654998/)
- Названия в локализованных приложениях: «Ягодичный Мост Со Штангой» (barbell hip thrust), «Ягодичный Мост В Смите», «Ягодичный Мостик КАС С Гантелью», «Ягодичный Мост Со Штангой В Разножке» — [fitwill.app](https://fitwill.app/ru/exercise/0058/barbell-lying-lifting-on-hip/); «Ягодичный мостик со штангой» для glute bridge — [lyfta.app](https://www.lyfta.app/ru/exercise/barbell-glute-bridge-83v). Fitwill относит гиперэкстензию к категории «Спина», оборудование — «Собственный вес» — [fitwill.app](https://fitwill.app/ru/exercise/0489/hyperextension/)
- «Гиперэкстензия», «обратная гиперэкстензия», «гиперэкстензия с округлённой спиной для ягодиц» — [Т—Ж](https://t-j.ru/what-is-hyperextension/), [Mentoday](https://mentoday.ru/fitness/training/obratnaya-giperekstenziya-6-variantov-vypolneniya-i-chastye-oshibki)

### Inferences
Таблица расхождений и рекомендуемый `name_ru` (канон в приложении) с alias:

| id | Канон `name_ru` | Альтернативы / конфликт |
|---|---|---|
| bulgarian_split_squat | Болгарские выпады | «Болгарский сплит-присед», «Болгарские приседания», «Болгарский присед» — все синонимы, хранить в aliases |
| romanian_deadlift_bb | Румынская тяга | «Румынская становая (тяга)», «РДЛ»; **не** «Тяга на прямых ногах» (это SLDL) — часть сайтов смешивает |
| stiff_leg_deadlift | Становая тяга на прямых ногах | смешивается с румынской; «Мёртвая тяга» — используется неоднозначно (иногда = SLDL, иногда = RDL) → не использовать как канон |
| hip_thrust_bb | Ягодичный мост со штангой (хип-траст) | в RU «ягодичный мост» = и hip thrust (лопатки на скамье), и glute bridge (на полу) → в UI показывать уточнение «от скамьи» / «с пола» |
| hack_squat | Гакк-приседания | «Хакк-приседания», «Гак-присед» (написание варьируется) |
| nordic_curl | Скандинавские сгибания | «Нордические сгибания», «Скандинавские скручивания» (Лайфхакер) |
| copenhagen_plank | Копенгагенская планка | «Копенгагенские приведения» |
| lying_leg_curl | Сгибание ног лёжа | «Сгибание ног в тренажёре» (неоднозначно лёжа/сидя) |
| back_extension_45 | Гиперэкстензия | в англоязычных базах back extension; в RU «гиперэкстензия» — общее бытовое название |
| farmers_walk | Прогулка фермера | «Фермерская прогулка» |
| cable_crunch | Скручивания на блоке стоя на коленях | разговорное «Молитва» |
| ab_wheel_rollout | Раскатка ролика для пресса | «Колесо для пресса», «Пресс-ролик» |
| pallof_press | Жим Паллофа | «Паллоф-пресс» |
| hollow_body_hold | Холлоу-холд («лодочка» на спине) | «лодочка» используют и для супермена → неоднозначно |
| trap_bar_deadlift | Тяга с трэп-грифом | «Тяга с шестигранным грифом», «Тяга с гекс-грифом» |

- Для поиска в приложении обязательно хранить `aliases` (включая латиницу: «RDL», «хип-траст», «hip thrust»), так как аудитория 20–40 лет смешивает языки.

### Gaps
- Не удалось проверить словарь «Энциклопедии упражнений» (sportwiki.to — ошибка загрузки), atletiq и ironman.ru. Канон строился по Лайфхакеру, Mentoday, Mail.ru Спорт, Т—Ж и локализациям fitwill и lyfta.
- Частотность вариантов (например, «болгарские выпады» против «болгарского сплит-приседа») не измерялась. Можно проверить через Яндекс Вордстат.

---

## Вопрос 3. Какие варианты делать отдельными записями, а какие полем variant

### Takeaway
Отдельная запись нужна, когда меняются снаряд, профиль нагрузки (>~10% по весу) или флаги безопасности. Когда меняется только постановка, наклон или темп — достаточно поля `variant`. High-bar и low-bar — отдельные id с общей группой (`family: back_squat`), потому что их веса несопоставимы для e1RM.

### Cited Findings
- Разные упражнения одного паттерна дают разное распределение гипертрофии. Присед сильнее растит квадрицепс и приводящие, хип-траст при сходном росте ягодиц почти не растит квадрицепс — [Plotkin 2023](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1279170/full). Значит, «Заменить» внутри одного `movement_pattern` не всегда эквивалентен по мышцам.
- Одно и то же упражнение с разным положением бедра (сгибание сидя против лёжа) даёт разный прирост: +14.1% против +9.3% — [Maeo 2021](https://sci-sport.com/en/hypertrophy-and-hamstring-protection-seated-prone-leg-curl/). Это аргумент хранить seated и lying как отдельные id.
- Глубина приседа влияет на рост приводящих и ягодичных (полный присед лучше), а сила специфична к тренируемой амплитуде — [Kubo 2019 via SBS](https://www.strongerbyscience.com/squats-adductors/). Поэтому box squat с фиксированной высотой и rack pull требуют своего трекинга.

### Inferences
- Рекомендуемая модель: `exercise` (id) → `family` (back_squat, deadlift, hip_thrust, leg_curl…) → `variant` (enum внутри id). e1RM хранить на уровне id. Замена сначала идёт внутри family, затем внутри pattern.
- Отдельные id: high-bar/low-bar, front, box, pause (variant_of), conventional/sumo/trap-bar, RDL/SLDL, hip thrust/glute bridge, seated/lying leg curl, standing/seated calf raise, forward/reverse lunge.
- Поле variant: стойка (узкая/широкая/сумо в жиме ногами), наклон корпуса в BSS, угол гиперэкстензии, хват, тип гантель/гиря в goblet (влияет только на шаг веса — можно вычислять из equipment).
- Тренажёрам ставить `e1rm_trackable: partial` и привязывать историю к `gym_id` пользователя, чтобы при смене зала не сравнивать несопоставимое.

### Gaps
- Нет исследований, которые количественно задают порог «≥10% разницы в весах» для разделения записей. Это проектное решение.

---

## Вопрос 4. Как открытые базы (wger, free-exercise-db, ExerciseDB, MuscleWiki) категоризируют этот регион

### Takeaway
Ни одна открытая база не размечает упражнения по паттерну движения (squat/hinge/lunge). Все размечают по мышцам, оборудованию и грубой категории (части тела). free-exercise-db (~800+ упражнений, Unlicense) — лучший кандидат для импорта: у него есть `force`, `level`, `mechanic`, `equipment`, `primaryMuscles`. Паттерны и флаги придётся добавлять самостоятельно.

### Cited Findings
- **free-exercise-db (yuhonas)**: 800+ упражнений, лицензия Unlicense (public domain). Поля: id, name, force, level, mechanic, equipment, primaryMuscles, secondaryMuscles, instructions, category, images — [GitHub README](https://github.com/yuhonas/free-exercise-db). Перечисления из schema.json — [schema.json](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/schema.json):
  - force: static/pull/push/null;
  - level: beginner/intermediate/expert;
  - mechanic: isolation/compound/null;
  - equipment: body only, dumbbell, barbell, kettlebells, cable, machine, bands, medicine ball, exercise ball, e-z curl bar, foam roll, other, null;
  - мышцы нижней части и кора: abdominals, abductors, adductors, calves, glutes, hamstrings, quadriceps, lower back;
  - category: strength, powerlifting, olympic weightlifting, strongman, plyometrics, stretching, cardio.
  - force, mechanic и equipment заполнены не везде (допускают null).
- **wger**: в фикстурах 16 мышц. Для низа тела и кора: Rectus abdominis (Abs), Obliquus externus abdominis, Gastrocnemius (Calves), Soleus, Gluteus maximus (Glutes), Quadriceps femoris (Quads), Biceps femoris (Hamstrings), Erector spinae (Lower back). **Нет приводящих, отводящих и средней ягодичной** — [wger muscles.json](https://github.com/wger-project/wger/blob/master/wger/exercises/fixtures/muscles.json)
  - Оборудование (12): Barbell, SZ-Bar, Dumbbell, Gym mat, Swiss Ball, Pull-up bar, none (bodyweight), Bench, Incline bench, Kettlebell, Resistance band, Cable machine — **нет «machine»/тренажёров и нет стойки** — [equipment.json](https://github.com/wger-project/wger/blob/master/wger/exercises/fixtures/equipment.json)
  - Категории (8): Arms, Legs, Abs, Chest, Back, Shoulders, Calves, Cardio — [categories.json](https://github.com/wger-project/wger/blob/master/wger/exercises/fixtures/categories.json)
  - wger API напрямую недоступен для роботов (robots_disallowed при попытке загрузки).
- **ExerciseDB (V2)**: 11 000+ упражнений, 15 000+ видео, 5 000+ GIF. Поля: exerciseId, name, imageUrl, videoUrl, exerciseType, bodyParts, equipments (например «LEVERAGE MACHINE»), targetMuscles (анатомически детально, например «Pectoralis Major Clavicular Head»), secondaryMuscles, keywords, overview, instructions, exerciseTips, variations, relatedExerciseIds. Репозиторий под AGPL-3.0, отдельные Terms of Use, платные тарифы через сайт/RapidAPI, Playground «не рекомендован для production» — [GitHub exercisedb-api](https://github.com/exercisedb/exercisedb-api)
- **MuscleWiki**: страница каталога не загрузилась (client_error) — [musclewiki.com/exercises](https://musclewiki.com/exercises).

### Inferences
- Маппинг в нашу схему:
  - free-exercise-db `force: push` (присед, жим ногами) / `pull` (тяги, сгибания) → наш `movement_pattern` требует ручной разметки. Автоматически можно ставить только `calf`, `hip_adduction`, `hip_abduction` (по primaryMuscles: calves/adductors/abductors).
  - `level: expert` → наш `advanced`.
  - Для кора в free-exercise-db одна мышца `abdominals` → разделение на anti-extension/anti-rotation/flexion — только ручное.
- wger не годится как источник мышечной разметки для ягодичных и приводящих (нет средней ягодичной и приводящих) и тренажёров. Годится лишь для переводов и изображений (проверить лицензии изображений отдельно, CC-BY-SA у части медиа — не проверено).
- ExerciseDB даёт видео и GIF, но лицензия AGPL и коммерческие условия рискованны для закрытого коммерческого Mini App. Нужна юридическая проверка Terms; использовать скорее как референс, а не как источник данных.
- Рекомендуемая собственная мышечная таксономия для низа: quadriceps (+ rectus_femoris), glute_max, glute_med_min, adductors, hamstrings, gastrocnemius, soleus, tibialis_anterior, erector_spinae, rectus_abdominis, obliques, transverse_abdominis (stabilizer), hip_flexors, quadratus_lumborum, grip. Это надмножество wger и free-exercise-db, которое на них маппится.

### Gaps
- MuscleWiki: фильтры (equipment/difficulty) и количество упражнений не получены. Сайт не загрузился, нужна ручная проверка в браузере.
- ExRx.net Directory не загрузился (robots). Его иерархия «регион → мышца → снаряд» в заметках не подтверждена источником.
- Полный список bodyParts и equipments ExerciseDB V2 не опубликован на странице GitHub. Тарифы и лицензия на медиа не проверены.
- Лицензии изображений free-exercise-db (часть происходит из старых открытых наборов) отдельно не проверялись.
