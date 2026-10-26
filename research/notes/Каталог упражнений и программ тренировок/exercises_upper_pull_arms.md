# Каталог упражнений: тяги верхней части тела (вертикальные/горизонтальные тяги, задняя дельта и верх спины, бицепс и предплечья, хват)

> Собрано 2026-10-25 для Telegram Mini App (силовой дневник + rule-based decision engine). Всего записей в каталоге: **90**.
> Метод: веб-поиск + выборочная загрузка страниц (часть первоисточников — PubMed/PMC, wger API, ExerciseDB API, MuscleWiki EN, reddit r/bodyweightfitness — была недоступна из среды: капча/403/блокировка; это отмечено в Gaps).
> Текст подсказок (cues) и ошибок написан своими словами на основе общепринятой тренерской практики, а не скопирован. Где источника нет — помечено как «вывод/практика», а не как факт.
> Пометка `[?]` у названия = русское название неустоявшееся / есть разночтения.

---

## 1. Каталог записей (структура для seed-базы) и общие словари

### Takeaway
Сформирован каталог из 90 записей в 6 паттернах (vertical_pull 24, horizontal_pull 25, scapular 7, rear_delt 7, elbow_flexion 19, grip_forearm 8). Для экономии места повторяющиеся поля (диапазоны повторений, шаги отягощения, профили замен) вынесены в словари-пресеты, на которые записи ссылаются кодом.

### Cited Findings
- free-exercise-db (yuhonas) использует поля `force` (static/pull/push), `level` (beginner/intermediate/expert), `mechanic` (isolation/compound), `equipment` (medicine ball, dumbbell, body only, bands, kettlebells, foam roll, cable, machine, barbell, exercise ball, e-z curl bar, other), `primaryMuscles`/`secondaryMuscles` из 17 значений (abdominals, abductors, adductors, biceps, calves, chest, forearms, glutes, hamstrings, lats, lower back, middle back, neck, quadriceps, shoulders, traps, triceps), `category` (powerlifting, strength, stretching, cardio, olympic weightlifting, strongman, plyometrics); `force`/`mechanic`/`equipment` могут быть null — [free-exercise-db schema.json](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/schema.json); [README](https://github.com/yuhonas/free-exercise-db)
- В free-exercise-db пример: «Alternate Incline Dumbbell Curl» → force pull, level beginner, mechanic isolation, equipment dumbbell, primary biceps, secondary forearms, category strength — [free-exercise-db README](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/README.md)
- Мышцы в wger (fixture muscles.json): 16 записей с латинским и англ. именем и флагом is_front; для зоны тяг релевантны: 1 Biceps brachii (Biceps), 2 Anterior deltoid (Shoulders), 9 Trapezius, 12 Latissimus dorsi (Lats), 13 Brachialis, 16 Erector spinae (Lower back). Отдельных rhomboids, задней дельты, предплечий/брахиорадиалиса нет — [wger muscles.json](https://github.com/wger-project/wger/blob/master/wger/exercises/fixtures/muscles.json)
- ExerciseDB v2: поля exerciseId, name, imageUrl, videoUrl, equipments, bodyParts, targetMuscles, secondaryMuscles, gender, exerciseType, keywords, overview, instructions, exerciseTips, variations, relatedExerciseIds; лицензия репозитория AGPL-3.0; значения в верхнем регистре (пример bodyParts: CHEST, equipments: LEVERAGE MACHINE, targetMuscles: «Pectoralis Major Clavicular Head») — [exercisedb-api GitHub](https://github.com/exercisedb/exercisedb-api)
- MuscleWiki (RU-интерфейс): фильтры оборудования «Штанга, Гантели, Собственный вес, Тренажёр, Медбол, Гири, Блочные тренажёры, Резинка, Блин, TRX, BOSU мяч, тренажёр Смита»; уровни «Новичок»/«Расширенный»; детальные мышцы (напр. Lower Trapezius, posterior-deltoid, rear-shoulders), русские названия «Тяга верхнего блока», «…обратным хватом», «…узким хватом», «…(нейтральный хват)» — [MuscleWiki RU lower trapezius](https://musclewiki.com/ru-ru/exercises/lower-trapezius); URL-структура мышц: [posterior-deltoid/dumbbells](https://musclewiki.com/exercises/posterior-deltoid/dumbbells), [rear-shoulders](https://musclewiki.com/de-de/exercises/rear-shoulders/dumbbells)

### Inferences

#### 1.1 Словари (enum) для записи

- **movement_pattern**: `vertical_pull` | `horizontal_pull` | `scapular` | `rear_delt` | `elbow_flexion` | `grip_forearm`
- **muscles** (собственный, детальнее wger/free-exercise-db; маппинг ниже в разделе 4): `lats, teres_major, traps_upper, traps_mid, traps_lower, rhomboids, rear_delt, rotator_cuff_ext (infraspinatus/teres minor), biceps, brachialis, brachioradialis, forearm_flexors, forearm_extensors, erectors, core, pec_major_sternal, serratus`
- **equipment**: `pullup_bar, rings, trx, barbell, ez_bar, dumbbell, kettlebell, cable, lat_pulldown_station, low_row_station, machine_selectorized, machine_plate_loaded, assisted_pullup_machine, smith, t_bar_landmine, trap_bar, bench_adjustable, preacher_bench, band, dip_belt, weight_vest, table_or_sturdy_bar, door_towel, plate, wrist_roller, gripper`
- **level**: `beginner | intermediate | advanced` (+ поле `prereq` — напр. «≥1 строгое подтягивание»)
- **load_type** (ключевое для decision engine, см. раздел 3): `external` | `bodyweight` | `bodyweight_added` | `bodyweight_assisted_machine` | `bodyweight_assisted_band` | `band_resistance` | `isometric_time` | `carry_time_distance`

#### 1.2 Пресеты шагов отягощения (INC)
- `INC_BB` — штанга: шаг 2.5 кг (2×1.25) базово; 5 кг для тяжёлых тяг на старте; микроблины 0.5–1 кг если есть.
- `INC_DB` — гантели (за 1 руку): шаг 1–2.5 кг (зал: обычно 2–2.5 кг; дом наборные: 0.5–1.25 кг).
- `INC_CABLE` — блок: шаг стека 2.5–7 кг (зависит от тренажёра; хранить у пользователя `stack_step`), доп. «полушаг» магнитной накладкой если есть.
- `INC_MACH` — тренажёр с плитами/рычажный: 5 кг (2×2.5) или шаг стека.
- `INC_BWADD` — пояс/жилет: 1.25–2.5 кг (минимальный блин), гантель между ног 2 кг шаг.
- `INC_ASSIST_MACH` — гравитрон: уменьшение противовеса на 1 шаг стека (обычно 5–7 кг).
- `INC_BAND` — резинки: дискретные уровни (ordinal), переход на следующую более тонкую; кг-эквивалент — приблизительный (Gaps).
- `INC_REPS` — только повторы/темп/пауза/ROM (свой вес без пояса).
- `INC_TIME` — секунды (вис, удержание) +5–10 с.

#### 1.3 Пресеты диапазонов повторений по целям (R)
- `R_HEAVY_COMP` (базовые тяги/подтягивания с весом): сила 3–6, гипертрофия 6–12, выносливость 12–20.
- `R_COMP` (тяги на блоке/тренажёре/гантели): сила 5–8, гипертрофия 8–15, выносливость 15–25.
- `R_BW` (свой вес без отягощения): сила — перейти к варианту с весом при >12 повт.; гипертрофия 5–15; выносливость 15+/лесенки.
- `R_ISO` (бицепс, задняя дельта, шраги): сила 6–10 (условно), гипертрофия 8–15, выносливость 15–30.
- `R_SMALL_ISO` (задняя дельта, фейс-пул, кисти): гипертрофия 12–20, выносливость 20–30.
- `R_TIME` (вис, удержание, прогулка): 20–60 с / 20–40 м.
- Обоснование широкого коридора гипертрофии (≈6–30 повт. при близости к отказу) — мета-анализ Schoenfeld et al. 2017 (PubMed 28834797) — страница была недоступна (капча), поэтому факт помещён в Gaps как непроверенный в этой сессии.

#### 1.4 Профили замен (SUB) — что предлагать по кнопке «Заменить»
- `SUB_NO_BAR` (нет турника): тяга верхнего блока → тяга резинки сверху (дверной якорь) → тяга гантели в наклоне/с упором → пуловер с гантелью.
- `SUB_DB_HOME` (только гантели): тяга гантели одной рукой с упором; тяга двух гантелей с упором грудью в скамью/наклонную спинку; пуловер с гантелью; разведения в наклоне; шраги/сгибания с гантелями.
- `SUB_BW` (только свой вес: двери/стол/кольца): австралийские подтягивания под столом/перекладиной, тяга полотенцем на двери, кольца/TRX-тяга, подтягивания на кольцах; для бицепса — сгибания в TRX/кольцах, «полотенце-сгибания» изометрией.
- `SUB_SHOULDER` (дискомфорт в плече): нейтральный хват, хват не шире плеч, избегать «за голову» и тяги к подбородку; тренажёры с упором грудью; укороченная амплитуда сверху; фейс-пул лёгкий.
- `SUB_ELBOW` (локоть: «локоть гольфиста/теннисиста»): нейтральный хват (молот), EZ-гриф вместо прямого, канатная рукоять, лямки (straps) для тяг, меньше висовых и строгих супинированных сгибаний; разгрузка на предплечья.
- `SUB_LOWBACK` (поясница — для тяг в наклоне): тяга с упором грудью (гантели/Т-гриф/seal row), тяга одной рукой с опорой о скамью, тяга нижнего блока сидя с вертикальным корпусом, тренажёрная тяга, австралийские подтягивания.

#### 1.5 Флаги осторожности (информационные, не медицинские)
`F_SHOULDER_END_RANGE` (крайние позиции плеча над головой/за головой), `F_ELBOW_TENDON` (нагрузка на сухожилия локтя/предплечья), `F_LOWBACK_HINGE` (поясница держит наклон), `F_GRIP_LIMIT` (хват может лимитировать раньше целевых мышц — предложить лямки), `F_DOOR_EQUIPMENT` (самодельные опоры: двери/столы — проверить прочность), `F_BAND_SNAP` (резинка может порваться/соскочить), `F_IMPINGEMENT_POSITION` (внутренняя ротация + отведение, напр. тяга к подбородку), `F_SWING_CHEAT` (склонность к читингу инерцией), `F_FALL_RISK` (падение с перекладины/колец, прыжки), `F_NECK_TENSION` (шраги, тяга к подбородку).

#### 1.6 Формат записи (поля)
```
id | name_ru | name_en | aliases
pattern | primary | secondary
equipment | level (prereq) | mechanic | unilateral
load_type | increment | reps
cues (2–4) | errors (2–3)
regress → | progress →
subs: no_bar / db_home / bw / shoulder / elbow / lowback (если не указано — см. профиль SUB_*)
flags | e1rm (yes/no + как)
```

---

### 1.7 VERTICAL_PULL (24)

**vp01 `pull_up`** — Подтягивания прямым хватом | Pull-up | aliases: классические подтягивания, подтягивания средним хватом, «подтягивания на турнике» [разночтение «прямой» vs «широкий» — см. раздел 2]
- prim: lats, teres_major | sec: biceps, brachialis, brachioradialis, traps_lower, rhomboids, rear_delt, core
- equip: pullup_bar | level: intermediate (prereq ≥1 строгое повт.) | compound | uni: no
- load_type: bodyweight (→ bodyweight_added при >12 повт.) | inc: INC_REPS → INC_BWADD | reps: R_BW
- cues: начни с «опускания лопаток вниз»; тяни локти к карманам/рёбрам; грудь к перекладине, подбородок выше грифа; полный вис внизу без «падения» в плечи
- errors: кипинг/раскачка ногами; половинная амплитуда (не до виса или не до подбородка); вытягивание шеи вперёд вместо подъёма корпуса
- regress → vp08 гравитрон / vp07 с резинкой / vp09 негативы / vp10 с опорой ногами / vp11 лопаточные подтягивания | progress → vp05 с весом, vp15 «лучник», паузы, медленный эксцентрик
- subs: no_bar → vp16 тяга верхнего блока / vp21 резинка сверху; db_home → hp04 тяга гантели одной рукой + vp23 пуловер; bw → vp14 на кольцах / hp17 австралийские; shoulder → vp04 нейтральный хват; elbow → vp04 нейтральный хват, лямки
- flags: F_SHOULDER_END_RANGE, F_ELBOW_TENDON, F_FALL_RISK | e1rm: yes — на системной массе (BW×k + доп.вес), см. раздел 3

**vp02 `wide_grip_pull_up`** — Подтягивания широким хватом | Wide-grip pull-up | aliases: «широкие подтягивания»
- prim: lats, teres_major | sec: traps_lower, rhomboids, rear_delt, biceps, brachialis
- equip: pullup_bar | level: intermediate | compound | uni: no
- load_type: bodyweight / bodyweight_added | inc: INC_REPS → INC_BWADD | reps: R_BW
- cues: хват ~1.5 ширины плеч, не шире; локти вниз-назад; тянуться грудью к перекладине
- errors: слишком широкий хват → короткая амплитуда и плечевой дискомфорт; «подбородок вперёд»
- regress → vp01, vp16 | progress → vp05 с весом
- subs: shoulder → vp04 / vp17; прочее как vp01
- flags: F_SHOULDER_END_RANGE | e1rm: yes (системная масса)

**vp03 `chin_up`** — Подтягивания обратным хватом | Chin-up | aliases: подтягивания обратным узким хватом, «чин-апы» [?]
- prim: lats, biceps | sec: brachialis, teres_major, traps_lower, rhomboids
- equip: pullup_bar | level: beginner-intermediate (обычно легче прямого) | compound | uni: no
- load_type: bodyweight / bodyweight_added | inc: INC_REPS → INC_BWADD | reps: R_BW
- cues: хват на ширине плеч, ладони к себе; локти вниз вдоль корпуса; грудь к грифу
- errors: перегиб в пояснице; сброс вниз без контроля; хват слишком узкий с вывернутыми кистями
- regress → vp07/vp08/vp09 обратным хватом, vp18 тяга верхнего блока обратным хватом | progress → vp06 с весом
- subs: elbow → vp04 нейтральный (супинация под нагрузкой может раздражать локоть); прочее как vp01
- flags: F_ELBOW_TENDON (супинированный хват), F_FALL_RISK | e1rm: yes

**vp04 `neutral_grip_pull_up`** — Подтягивания параллельным хватом | Neutral-grip pull-up | aliases: подтягивания нейтральным хватом, «на параллельных рукоятях» [? «параллельный» и «нейтральный» используются как синонимы]
- prim: lats | sec: brachialis, brachioradialis, biceps, teres_major, rhomboids
- equip: pullup_bar с параллельными рукоятями / V-рукоять на турнике | level: beginner-intermediate | compound | uni: no
- load_type: bodyweight / bodyweight_added | inc: INC_REPS → INC_BWADD | reps: R_BW
- cues: ладони друг к другу; локти вперёд-вниз; тянуть грудь к рукоятям
- errors: раскачка; неполный вис
- regress → vp07/vp08 нейтральным | progress → +вес
- subs: no_bar → vp17 тяга верхнего блока V-рукоятью; прочее как vp01
- flags: обычно наиболее «дружелюбный» к плечу/локтю вариант (практика) | e1rm: yes

**vp05 `weighted_pull_up`** — Подтягивания с отягощением | Weighted pull-up | aliases: подтягивания с весом, с поясом
- prim: lats, teres_major | sec: biceps, brachialis, rhomboids, traps_lower, core
- equip: pullup_bar + dip_belt / weight_vest / гантель между стоп | level: advanced (prereq ≥10–12 строгих повт.) | compound | uni: no
- load_type: bodyweight_added | inc: INC_BWADD (1.25–2.5 кг) | reps: R_HEAVY_COMP
- cues: вес висит неподвижно, корпус «полым»; тот же стандарт амплитуды, что без веса; контролируемый негатив
- errors: укороченная амплитуда ради веса; раскачка груза
- regress → vp01 | progress → +вес, паузы
- subs: no_bar → vp16 с большим весом; прочее как vp01
- flags: F_SHOULDER_END_RANGE, F_ELBOW_TENDON | e1rm: yes — e1RM(system) по Epley на BW+добавка, показывать «добавочный 1ПМ» = e1RM(system) − BW

**vp06 `weighted_chin_up`** — Подтягивания обратным хватом с отягощением | Weighted chin-up
- как vp05 (обратный хват); prim: lats, biceps | flags: F_ELBOW_TENDON | e1rm: yes

**vp07 `band_assisted_pull_up`** — Подтягивания с резиной (с резиновой петлёй) | Band-assisted pull-up | aliases: подтягивания с резинкой, с эспандером
- prim: lats | sec: biceps, brachialis, teres_major, rhomboids
- equip: pullup_bar + band (петля) | level: beginner | compound | uni: no
- load_type: bodyweight_assisted_band | inc: INC_BAND (переход на более тонкую резинку) + INC_REPS | reps: 5–12
- cues: петля под колено или стопу, надёжно закреплена; внизу резинка помогает сильнее всего — внимание на верхнюю часть; не «выстреливать» из нижней точки
- errors: резинка соскальзывает; использование отскока резинки; слишком толстая резинка «вечно»
- regress → vp08 гравитрон / hp17 австралийские | progress → тоньше резинка → vp09 негативы → vp01
- subs: no_bar → vp21 тяга резинки сверху / vp16; bw → hp17
- flags: F_BAND_SNAP, F_FALL_RISK | e1rm: условно (нет точного кг-эквивалента резинки); трекать повторы × уровень резинки

**vp08 `machine_assisted_pull_up`** — Подтягивания в гравитроне | Assisted pull-up machine | aliases: гравитрон, подтягивания с противовесом
- prim: lats | sec: biceps, brachialis, teres_major
- equip: assisted_pullup_machine | level: beginner | compound | uni: no
- load_type: bodyweight_assisted_machine | inc: INC_ASSIST_MACH (−1 шаг противовеса) | reps: R_COMP (6–12)
- cues: колени на платформе, корпус вертикально; полный вис сверху вниз; тянуть локти вниз к бокам
- errors: «помощь» ногами/толчок платформой; укороченная амплитуда
- regress → vp16 | progress → меньший противовес → vp09 / vp01
- subs: no_bar → vp16; bw → vp07, hp17
- flags: — | e1rm: yes, через эффективную нагрузку = BW − противовес (линейно, приемлемо)

**vp09 `negative_pull_up`** — Негативные подтягивания | Negative (eccentric) pull-up | aliases: эксцентрические подтягивания, «опускания с перекладины»
- prim: lats | sec: biceps, brachialis, teres_major
- equip: pullup_bar + опора (лавка/стул) | level: beginner | compound | uni: no
- load_type: bodyweight (эксцентрика) | inc: длительность опускания 3→5→8 с, повторы | reps: 3–6 × 3–5 с
- cues: запрыгни/встань в верхнюю позицию; опускайся равномерно, считая секунды; в конце — активный вис
- errors: «провал» в середине; прыжок без контроля; слишком много повторов → сильная крепатура
- regress → vp08, vp07 | progress → vp01
- subs: как vp01
- flags: F_FALL_RISK, выраженная крепатура/DOMS для новичков | e1rm: no (трекать время эксцентрика и повторы)

**vp10 `feet_assisted_pull_up`** — Подтягивания с опорой ногами [?] | Foot-assisted pull-up | aliases: подтягивания с помощью ног, «с табуретки»
- prim: lats | sec: biceps, brachialis
- equip: низкая перекладина/турник + опора | level: beginner | compound | uni: no
- load_type: bodyweight (помощь неколичественная) | inc: INC_REPS, меньше помощи ногами | reps: 6–12
- cues: ноги помогают ровно настолько, чтобы закончить повтор; держи темп
- errors: ноги делают всю работу
- regress → hp17 | progress → vp07/vp09
- flags: F_FALL_RISK | e1rm: no

**vp11 `scapular_pull_up`** — Лопаточные подтягивания | Scapular pull-up | aliases: «подтягивания лопатками», scap pull-up
- prim: traps_lower, lats | sec: rhomboids, serratus
- equip: pullup_bar | level: beginner | isolation (лопаточная) | uni: no
- load_type: bodyweight | inc: INC_REPS, пауза сверху | reps: 8–15
- cues: руки прямые; опусти и слегка сведи лопатки — тело приподнимается на несколько см; пауза 1–2 с
- errors: сгибание рук в локтях; рывок
- regress → vp12 вис | progress → vp09/vp01
- flags: F_FALL_RISK (низкий) | e1rm: no
- примечание: pattern допустимо как `scapular`; используется в 4-нед. прогрессии к 1-му подтягиванию (см. раздел 3)

**vp12 → см. gf05 `dead_hang`** (вис) — вынесен в grip_forearm.

**vp13 `towel_pull_up`** — Подтягивания на полотенцах | Towel pull-up
- prim: lats, forearm_flexors | sec: biceps, brachialis, brachioradialis
- equip: pullup_bar + 2 полотенца | level: advanced | compound | uni: no
- load_type: bodyweight | inc: INC_REPS | reps: 3–10
- cues: полотенца перекинуты, хват нейтральный в кулак; тяни как обычное подтягивание
- errors: срыв хвата без контроля
- regress → vp04, gf05 вис на полотенцах | progress → +вес
- flags: F_GRIP_LIMIT, F_FALL_RISK | e1rm: no (хват — лимитирующий фактор)

**vp14 `ring_pull_up`** — Подтягивания на кольцах | Ring pull-up (+ TRX)
- prim: lats | sec: biceps, brachialis, teres_major, rhomboids
- equip: rings | level: intermediate | compound | uni: no
- load_type: bodyweight / bodyweight_added | inc: INC_REPS | reps: R_BW
- cues: внизу ладони вперёд, вверху кольца разворачиваются в нейтраль; кольца у груди
- errors: раскачивание колец; неполная амплитуда
- regress → hp18 тяга на кольцах | progress → +вес
- flags: F_DOOR_EQUIPMENT (крепление), F_FALL_RISK | e1rm: yes (системная масса)

**vp15 `archer_pull_up`** — Подтягивания «лучник» [?] | Archer pull-up | aliases: «лучник», подтягивания с переносом веса
- prim: lats (акцент на одну сторону) | sec: biceps, brachialis, core
- equip: pullup_bar/rings | level: advanced | compound | uni: частично (yes, ассиметричная нагрузка)
- load_type: bodyweight | inc: INC_REPS | reps: 3–8/сторона
- cues: широкий хват, тянуться к одной руке, вторая почти прямая
- errors: вращение корпуса; неполная амплитуда
- regress → vp02 | progress → подтягивание на одной руке с помощью
- flags: F_ELBOW_TENDON, F_SHOULDER_END_RANGE | e1rm: no

**vp16 `lat_pulldown_wide`** — Тяга верхнего блока широким хватом | Wide-grip lat pulldown | aliases: тяга верхнего блока к груди, вертикальная тяга, «тяга блока к груди»
- prim: lats, teres_major | sec: biceps, brachialis, rhomboids, traps_lower, rear_delt
- equip: lat_pulldown_station (cable) | level: beginner | compound | uni: no
- load_type: external | inc: INC_CABLE | reps: R_COMP
- cues: бёдра зафиксированы валиками; хват чуть шире плеч, ладони от себя; рукоять к верху груди, лёгкий отклон корпуса; вверху — полное растяжение без потери контроля
- errors: тяга за счёт отклона назад и раскачки; рукоять к животу/за голову; локти уходят назад вместо вниз
- regress → меньший вес | progress → вес; переход vp08→vp01
- subs: no_bar n/a (это и есть замена); db_home → vp23 пуловер + hp04; bw → hp17/vp07; shoulder → vp17 V-рукоять; elbow → vp17
- flags: — | e1rm: yes (вес стека; сравним только в пределах одного тренажёра — хранить machine_id)
- data: pronated grip даёт большую активность широчайших, чем supinated, при широком и узком хвате (12 мужчин, 70% 1ПМ, EMG) — [Lusk et al., 2010, J Strength Cond Res via PSU](https://pure.psu.edu/en/publications/grip-width-and-forearm-orientation-effects-on-muscle-activity-dur/)

**vp17 `lat_pulldown_close_neutral`** — Тяга верхнего блока узким (параллельным) хватом | Close-grip / neutral lat pulldown | aliases: тяга верхнего блока V-рукоятью, нейтральным хватом
- prim: lats | sec: biceps, brachialis, brachioradialis, rhomboids
- equip: lat_pulldown_station + V-handle | level: beginner | compound | uni: no
- load_type: external | inc: INC_CABLE | reps: R_COMP
- cues: рукоять к верху груди; локти вниз вдоль корпуса; не наклоняться сильно назад
- errors: тяга бицепсом (короткая амплитуда); перекат корпусом
- regress/progress: вес | subs: как vp16
- flags: — | e1rm: yes (machine-specific)

**vp18 `lat_pulldown_reverse`** — Тяга верхнего блока обратным хватом | Reverse-grip (supinated) lat pulldown
- prim: lats, biceps | sec: brachialis, teres_major
- equip: lat_pulldown_station | level: beginner | compound | uni: no
- load_type: external | inc: INC_CABLE | reps: R_COMP
- cues: хват на ширине плеч, ладони к себе; локти вниз к рёбрам; рукоять к верху груди
- errors: раскачка корпусом
- subs: elbow → vp17 | flags: F_ELBOW_TENDON | e1rm: yes
- data: в Lusk et al. 2010 супинированный хват — меньше активность широчайших, разницы для бицепса не найдено — [PSU](https://pure.psu.edu/en/publications/grip-width-and-forearm-orientation-effects-on-muscle-activity-dur/)

**vp19 `lat_pulldown_behind_neck`** — Тяга верхнего блока за голову | Behind-the-neck pulldown
- prim: lats | sec: rhomboids, traps_mid, rear_delt
- equip: lat_pulldown_station | level: intermediate | compound | uni: no
- load_type: external | inc: INC_CABLE | reps: R_COMP
- cues: (если выполнять) — лёгкий вес, только при хорошей подвижности плеча; голова чуть вперёд, без удара грифом по шее
- errors: выведение плеч в крайнюю наружную ротацию под весом; тяга до шеи с подбородком в грудь
- default: **не рекомендовать по умолчанию**; замена → vp16
- flags: F_SHOULDER_END_RANGE (сильный) | e1rm: yes
- data: русскоязычная статья: вариант «за голову» выводит плечевые суставы в неестественное положение и не даёт преимуществ — [Т—Ж](https://t-j.ru/lat-pulldown/)

**vp20 `single_arm_lat_pulldown`** — Тяга верхнего блока одной рукой | Single-arm (kneeling) cable pulldown | aliases: тяга в кроссовере одной рукой стоя на коленях
- prim: lats | sec: teres_major, biceps
- equip: cable (кроссовер/верхний блок) + D-рукоять | level: beginner | compound | uni: yes
- load_type: external | inc: INC_CABLE | reps: 10–20
- cues: локоть вниз к бедру; лёгкий наклон к рабочей стороне; полное растяжение вверху
- errors: вращение корпуса; тяга бицепсом
- flags: — | e1rm: yes (по стороне)
- data: используется 15–20 повторений перед основными упражнениями для «чувства» широчайших — [Лайфхакер](https://lifehacker.ru/varianty-tyagi-dlya-spiny/)

**vp21 `band_lat_pulldown`** — Тяга резинки сверху (вертикальная тяга с эспандером) [?] | Band lat pulldown
- prim: lats | sec: biceps, teres_major
- equip: band + дверной якорь/перекладина | level: beginner | compound | uni: no/yes
- load_type: band_resistance | inc: INC_BAND, повторы | reps: 12–25
- cues: якорь выше головы; сидя/на коленях; тяни локти вниз к рёбрам
- errors: резинка проскальзывает; слишком короткая амплитуда
- flags: F_BAND_SNAP, F_DOOR_EQUIPMENT | e1rm: no

**vp22 `straight_arm_pulldown`** — Пуловер на верхнем блоке (тяга прямыми руками) | Straight-arm pulldown | aliases: «пуловер на блоке», тяга верхнего блока прямыми руками
- prim: lats, teres_major | sec: triceps (длинная головка), core, pec_major_sternal
- equip: cable + прямая рукоять/канат | level: beginner | isolation | uni: no
- load_type: external | inc: INC_CABLE | reps: R_ISO (10–15)
- cues: руки почти прямые; движение только в плече — дуга от уровня головы к бёдрам; корпус наклонён, спина ровная
- errors: сгибание локтей (превращается в тягу/жим вниз); раскачка
- subs: db_home → vp23; bw → n/a (резинка: band straight-arm pulldown)
- flags: F_SHOULDER_END_RANGE (верх) | e1rm: no (изоляция; трекать вес×повторы)

**vp23 `dumbbell_pullover`** — Пуловер с гантелью | Dumbbell pullover
- prim: lats, pec_major_sternal | sec: triceps, serratus, teres_major
- equip: dumbbell + bench | level: beginner-intermediate | isolation | uni: no
- load_type: external | inc: INC_DB | reps: R_ISO
- cues: лёжа поперёк/вдоль скамьи, локти слегка согнуты и фиксированы; опускать за голову до комфортного растяжения; тянуть гантель над грудь
- errors: сгибание-разгибание локтей; чрезмерная амплитуда; прогиб поясницы
- flags: F_SHOULDER_END_RANGE | e1rm: no
- примечание: спорная классификация (спина vs грудь) — в каталоге pattern=vertical_pull (разгибание плеча) [?]

**vp24 `machine_pulldown`** — Тяга сверху в рычажном тренажёре | Machine (lever) pulldown | aliases: «Хаммер-тяга сверху», вертикальная тяга в тренажёре
- prim: lats | sec: biceps, brachialis, teres_major
- equip: machine_plate_loaded / selectorized | level: beginner | compound | uni: часто опция (iso-lateral)
- load_type: external | inc: INC_MACH | reps: R_COMP
- cues: сиденье так, чтобы рукояти были в вытянутых руках; локти вниз к бокам; пауза внизу
- errors: подъём таза; рывки
- flags: — | e1rm: yes (machine-specific)
- MuscleWiki слаг: «machine-pulldown» — [MuscleWiki](https://musclewiki.com/fr-fr/exercise/machine-pulldown?model=m)

---

### 1.8 HORIZONTAL_PULL (25)

**hp01 `barbell_bent_over_row`** — Тяга штанги в наклоне | Barbell bent-over row | aliases: тяга штанги к поясу, тяга штанги в наклоне к поясу [?«к поясу» vs «к животу»]
- prim: lats, rhomboids, traps_mid | sec: rear_delt, teres_major, biceps, brachialis, erectors, hamstrings (изометрия)
- equip: barbell | level: intermediate | compound | uni: no
- load_type: external | inc: INC_BB | reps: R_HEAVY_COMP
- cues: наклон 30–45° от горизонта (или ближе к параллели), спина нейтральная; хват чуть шире плеч; тянуть гриф к низу живота/поясу локтями назад; опускать до прямых рук без потери положения спины
- errors: «подъём корпуса» с каждым повтором (превращается в шраг/становую); округление поясницы; тяга бицепсом без сведения лопаток
- regress → hp08 с упором грудью, hp12 нижний блок | progress → вес, пауза у живота, hp02 Пендлей
- subs: lowback → hp06/hp08/hp12/hp14; db_home → hp04/hp05; bw → hp17; shoulder → нейтральный хват (hp05 гантели); elbow → лямки, нейтральный хват
- flags: F_LOWBACK_HINGE, F_SWING_CHEAT, F_GRIP_LIMIT | e1rm: yes
- data: тяга в наклоне сильнее нагружает поясницу и кор и даёт больше читинга, но позволяет больший вес; тяга с упором грудью — для новичков и возвращающихся после проблем со спиной — [Breaking Muscle](https://breakingmuscle.com/chest-supported-row-vs-bent-over-row/)
- data (RU): для гипертрофии рекомендуют 10–16 повторов при ~75% 1ПМ, строгость важнее веса, тянуть к животу для меньшего участия бицепса — [Хорошенко, ironman.ru (PDF)](https://ironman.ru/pdf_articles/khoroshenko-nagruzite-seredinu-spiny.pdf)

**hp02 `pendlay_row`** — Тяга Пендлея | Pendlay row | aliases: тяга Пэндли, тяга штанги от пола в наклоне [? транслитерация: Пендлей/Пэндли]
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps, erectors
- equip: barbell | level: intermediate | compound | uni: no
- load_type: external | inc: INC_BB | reps: R_HEAVY_COMP (3–8)
- cues: корпус ~параллельно полу; каждый повтор с пола (мёртвая точка); взрывной подъём к нижней части груди; опустить на пол контролируемо
- errors: подъём корпуса; отбив штанги от пола
- flags: F_LOWBACK_HINGE | e1rm: yes
- data: штанга опускается на пол каждый повтор; вариант с трэп-грифом даёт нейтральный хват и помогает держать спину; 3×8–12 — [Лайфхакер](https://lifehacker.ru/varianty-tyagi-dlya-spiny/)

**hp03 `reverse_grip_barbell_row`** — Тяга штанги обратным хватом в наклоне | Reverse-grip barbell row | aliases: тяга Ятса [?]
- prim: lats | sec: biceps, rhomboids, traps_mid, erectors
- equip: barbell/ez_bar | level: intermediate | compound | uni: no
- load_type: external | inc: INC_BB | reps: R_COMP
- cues: корпус более вертикальный (≈45°); локти близко к бокам; гриф к животу
- errors: перегрузка бицепса/локтя; избыточный читинг
- flags: F_ELBOW_TENDON, F_LOWBACK_HINGE | e1rm: yes

**hp04 `one_arm_dumbbell_row`** — Тяга гантели одной рукой в наклоне | One-arm dumbbell row | aliases: тяга гантели одной рукой к поясу, «тяга гантели с упором в скамью»
- prim: lats, rhomboids | sec: teres_major, rear_delt, biceps, brachialis, traps_mid
- equip: dumbbell + bench | level: beginner | compound | uni: yes
- load_type: external | inc: INC_DB | reps: R_COMP
- cues: колено и ладонь на скамье, спина параллельно полу; тяни гантель к тазу по дуге (локоть к бедру); внизу — дать лопатке выйти вперёд
- errors: вращение корпуса для подъёма; тяга к груди с локтем в сторону (уходит в заднюю дельту — если не цель); подъём плеча к уху
- regress → hp06 с упором грудью | progress → вес, hp10 Кроу-тяга
- subs: lowback → уже щадящий вариант (опора); bw → hp17; elbow → лямки
- flags: F_GRIP_LIMIT | e1rm: yes (на сторону)
- RU-термин: «тяги гантели одной рукой к поясу» — [ironman.ru](https://ironman.ru/pdf_articles/khoroshenko-nagruzite-seredinu-spiny.pdf)

**hp05 `two_arm_dumbbell_row`** — Тяга гантелей в наклоне | Bent-over dumbbell row (two arms) | aliases: тяга двух гантелей к поясу
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps, erectors
- equip: dumbbell | level: beginner-intermediate | compound | uni: no
- load_type: external | inc: INC_DB | reps: R_COMP
- cues: наклон, нейтральная спина; нейтральный или прямой хват; локти назад к поясу
- errors: подъём корпуса; округление спины
- subs: lowback → hp06 | flags: F_LOWBACK_HINGE | e1rm: yes
- RU-название: «Тяга Гантелей В Наклоне» — [Fitwill RU](https://fitwill.app/ru/exercise/2482/dumbbell-bent-over-row/)

**hp06 `chest_supported_dumbbell_row`** — Тяга гантелей лёжа на наклонной скамье | Chest-supported (incline) dumbbell row | aliases: тяга гантелей с упором грудью, «тяга лёжа на наклонной»
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps
- equip: dumbbell + bench_adjustable (30–45°) | level: beginner | compound | uni: no
- load_type: external | inc: INC_DB | reps: R_COMP
- cues: грудь прижата к спинке; гантели тянуть к нижним рёбрам; не отрывать грудь
- errors: подъём груди со скамьи; «шраг» вместо тяги
- subs: — (это главная замена для lowback) | flags: — | e1rm: yes
- RU-вариант с хватом «молот»: [Fitwill RU](https://fitwill.app/ru/exercise/3901/dumbbell-hammer-grip-incline-bench-two-arm-row/)

**hp07 `seal_row`** — Тяга лёжа на высокой скамье («тюленья тяга») [?] | Seal row | aliases: тяга штанги лёжа на скамье
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps
- equip: barbell/dumbbell + высокая горизонтальная скамья | level: intermediate | compound | uni: no
- load_type: external | inc: INC_BB/INC_DB | reps: R_COMP
- cues: лёжа на животе, руки висят; гриф к низу груди; без помощи ногами
- errors: подъём головы/корпуса; рывок
- flags: — (оборудование редкое) | e1rm: yes

**hp08 `t_bar_row`** — Тяга Т-грифа в наклоне | T-bar row | aliases: Т-тяга, тяга Т-образной штанги, тяга «landmine» [?]
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps, erectors
- equip: t_bar_landmine + V-рукоять | level: intermediate | compound | uni: no
- load_type: external (плиты) | inc: INC_MACH (2×1.25/2×2.5) | reps: R_HEAVY_COMP
- cues: ноги по сторонам грифа, наклон с нейтральной спиной; рукоять к животу/низу груди; сведение лопаток вверху
- errors: подъём корпуса; короткая амплитуда
- subs: lowback → hp09 | flags: F_LOWBACK_HINGE | e1rm: yes (вес блинов; гриф — отдельная константа)
- RU-термин «тяги Т-грифа в наклоне» — [ironman.ru](https://ironman.ru/pdf_articles/khoroshenko-nagruzite-seredinu-spiny.pdf)

**hp09 `chest_supported_t_bar_row`** — Тяга Т-грифа с упором грудью | Chest-supported T-bar row
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps
- equip: machine_plate_loaded (Т-тяга с упором) | level: beginner | compound | uni: no
- load_type: external | inc: INC_MACH | reps: R_COMP
- cues: грудь на подушке; прямой хват — акцент верх спины, нейтральный — широчайшие
- errors: отрыв груди; рывки
- flags: — | e1rm: yes
- data: снижает нагрузку на поясницу; 3–4×6–10; прямой хват → верх спины, нейтральный → больше широчайших — [Лайфхакер](https://lifehacker.ru/varianty-tyagi-dlya-spiny/)

**hp10 `kroc_row`** — Тяга Кроу [?] (тяжёлая тяга гантели одной рукой на много повторов) | Kroc row
- prim: lats, traps, rhomboids | sec: biceps, forearm_flexors
- equip: dumbbell | level: advanced | compound | uni: yes
- load_type: external | inc: INC_DB | reps: 15–30
- cues: допускается умеренный «телесный» импульс; лямки
- errors: читинг превращается в рывок корпуса
- flags: F_SWING_CHEAT, F_GRIP_LIMIT | e1rm: no (много повторов — e1RM неточен)

**hp11 `meadows_row`** — Тяга Медоуза [?] | Meadows row
- prim: lats, rhomboids | sec: rear_delt, biceps, forearm
- equip: t_bar_landmine (конец грифа) | level: intermediate | compound | uni: yes
- load_type: external | inc: INC_MACH | reps: R_COMP
- cues: встать перпендикулярно грифу, хват прямой за толстый конец; локоть вверх-назад
- errors: вращение корпуса
- flags: F_LOWBACK_HINGE (умеренный) | e1rm: yes

**hp12 `seated_cable_row`** — Тяга нижнего блока сидя (к поясу) | Seated cable row | aliases: горизонтальная тяга, тяга блока к животу, тяга к поясу на блоке
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps, brachialis, erectors (изометрия)
- equip: low_row_station + V-рукоять | level: beginner | compound | uni: no
- load_type: external | inc: INC_CABLE | reps: R_COMP
- cues: колени слегка согнуты, корпус вертикально; рукоять к животу, плечи вниз-назад; вперёд — дать лопаткам разойтись без округления поясницы
- errors: раскачка корпусом вперёд-назад; подъём плеч к ушам; округление спины в растяжении
- subs: lowback → hp15 тренажёр с упором; db_home → hp06; bw → hp17
- flags: F_SWING_CHEAT | e1rm: yes (machine-specific)
- RU-термин «тяги к поясу на блоке» — [ironman.ru](https://ironman.ru/pdf_articles/khoroshenko-nagruzite-seredinu-spiny.pdf)

**hp13 `wide_grip_cable_row`** — Тяга нижнего блока широким хватом | Wide-grip seated cable row
- prim: rhomboids, traps_mid, rear_delt | sec: lats, biceps
- equip: low_row_station + длинная рукоять | level: beginner | compound | uni: no
- load_type: external | inc: INC_CABLE | reps: R_COMP
- cues: рукоять к нижней части груди, локти ~45–60° от корпуса
- errors: как hp12 | e1rm: yes

**hp14 `single_arm_cable_row`** — Тяга нижнего блока одной рукой | Single-arm cable row
- prim: lats | sec: rhomboids, biceps, core (антиротация)
- equip: cable + D-рукоять | level: beginner | compound | uni: yes
- load_type: external | inc: INC_CABLE | reps: R_COMP (8–12/сторона)
- cues: нейтральный хват, локоть вдоль рёбер; корпус не разворачивается за рукой
- errors: вращение корпуса
- flags: — | e1rm: yes
- data: 3×8–12 на сторону, локоть прижат, корпус не вращается — [Лайфхакер](https://lifehacker.ru/varianty-tyagi-dlya-spiny/)

**hp15 `machine_row`** — Тяга в тренажёре сидя (с упором грудью) | Seated machine row | aliases: горизонтальная тяга в тренажёре, тяги к поясу на тренажёре
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps
- equip: machine_selectorized | level: beginner | compound | uni: часто
- load_type: external | inc: INC_MACH/стек | reps: R_COMP
- cues: грудь на упоре, рукояти в вытянутых руках; локти назад; пауза
- errors: отрыв груди; неполная амплитуда | flags: — | e1rm: yes (machine-specific)

**hp16 `iso_lateral_row`** — Рычажная тяга (Хаммер) [?] | Plate-loaded iso-lateral row | aliases: тяга в тренажёре Хаммер
- prim: lats, rhomboids | sec: rear_delt, biceps
- equip: machine_plate_loaded | level: beginner | compound | uni: yes/no
- load_type: external | inc: INC_MACH | reps: R_COMP
- cues/errors: как hp15 | e1rm: yes
- примечание: «Хаммер» — бренд Hammer Strength; в названии для UI лучше «рычажная тяга» (бренд-нейтрально)

**hp17 `inverted_row`** — Австралийские подтягивания | Inverted row | aliases: горизонтальные подтягивания, обратные подтягивания, тяга в висе лёжа [? три равноправных названия]
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps, core, glutes (изометрия)
- equip: перекладина на уровне пояса / Смит / силовая рама | level: beginner | compound | uni: no
- load_type: bodyweight (доля BW зависит от угла) | inc: INC_REPS + угол корпуса (выше/ниже перекладина, ноги согнуты→прямые→на скамье) | reps: 8–15
- cues: тело прямое как доска; тяни грудь к перекладине; лопатки сводятся вверху
- errors: провисание таза; тянуться подбородком; короткая амплитуда
- regress → выше перекладина/ноги согнуты | progress → ноги прямо → hp19 ноги на возвышении → жилет/пауза → vp01
- flags: F_FALL_RISK (низкий) | e1rm: no (угол меняет нагрузку — трекать угол/высоту как параметр «уровень»)
- data: положение стоп меняет акцент; облегчить — согнуть ноги, усложнить — ноги на скамье, медленный негатив, утяжеление — [Лайфхакер](https://lifehacker.ru/varianty-tyagi-dlya-spiny/)
- data: входит в 4-нед. прогрессию к 1-му подтягиванию (3×10 + висы) — [Garage Gym Reviews](https://www.garagegymreviews.com/pull-up-progression)

**hp18 `ring_row`** — Тяга на кольцах / в петлях TRX | Ring row / suspension row | aliases: TRX-тяга
- prim: lats, rhomboids, traps_mid | sec: rear_delt, biceps, core
- equip: rings / trx | level: beginner | compound | uni: no (one-arm вариант — advanced)
- load_type: bodyweight (угол) | inc: угол корпуса, INC_REPS | reps: 8–20
- cues: как hp17; внизу ладони вниз, вверху нейтраль
- errors: провисание таза
- flags: F_DOOR_EQUIPMENT (крепление ремней) | e1rm: no

**hp19 `feet_elevated_inverted_row`** — Австралийские подтягивания с ногами на возвышении | Feet-elevated inverted row
- как hp17, level intermediate; прогресс → жилет | e1rm: no / bodyweight_added при жилете

**hp20 `table_row`** — Тяга под столом [?] | Table (under-table) row
- prim: lats, rhomboids | sec: biceps, rear_delt
- equip: table_or_sturdy_bar | level: beginner | compound | uni: no
- load_type: bodyweight | inc: угол/повторы | reps: 8–15
- cues: лёжа под прочным столом, хват за край; тянуть грудь к краю
- errors: тяга рывком; стол смещается
- flags: F_DOOR_EQUIPMENT (проверить что стол не опрокинется) | e1rm: no

**hp21 `door_towel_row`** — Тяга полотенцем за дверь [?] | Door towel row
- prim: lats, rhomboids | sec: biceps, forearm_flexors
- equip: door_towel (полотенце вокруг ручек двери) | level: beginner | compound | uni: no/yes
- load_type: bodyweight (угол) | inc: угол/повторы | reps: 10–20
- cues: дверь закрыта и ты тянешь в сторону, в которую она закрывается (не открывается!); стопы у двери, отклон назад
- errors: тяга в сторону открывания; соскальзывание стоп
- flags: F_DOOR_EQUIPMENT (высокий) | e1rm: no

**hp22 `band_row`** — Тяга резинки к поясу | Band row (seated/standing)
- prim: lats, rhomboids | sec: biceps, rear_delt
- equip: band | level: beginner | compound | uni: no/yes
- load_type: band_resistance | inc: INC_BAND, повторы | reps: 12–25
- cues: якорь на уровне пояса/вокруг стоп; локти назад; пауза
- errors: слишком слабое натяжение; рывок
- flags: F_BAND_SNAP | e1rm: no

**hp23 `smith_machine_row`** — Тяга в Смите в наклоне | Smith machine bent-over row
- prim: lats, rhomboids, traps_mid | sec: biceps, erectors
- equip: smith | level: beginner-intermediate | compound | uni: no
- load_type: external | inc: INC_BB (вес грифа Смита разный — хранить константу тренажёра) | reps: R_COMP
- cues/errors: как hp01 | flags: F_LOWBACK_HINGE | e1rm: yes (machine-specific)

**hp24 `kettlebell_row`** — Тяга гири в наклоне | Kettlebell row (one-arm / gorilla row [?])
- prim: lats, rhomboids | sec: biceps, rear_delt
- equip: kettlebell | level: beginner | compound | uni: yes
- load_type: external | inc: шаг гирь 4 кг (дискретно 8/12/16/20/24…) | reps: R_COMP
- cues: как hp04
- flags: F_LOWBACK_HINGE (без опоры) | e1rm: yes (грубый шаг — двойная прогрессия через повторы)

**hp25 `rear_delt_row`** — Тяга гантелей на заднюю дельту (локти в стороны) | Rear-delt row | aliases: «Тяга гантелей лёжа на скамье на заднюю дельту»
- prim: rear_delt, traps_mid, rhomboids | sec: biceps, rotator_cuff_ext
- equip: dumbbell (+ bench) / cable / barbell | level: beginner | compound | uni: no
- load_type: external | inc: INC_DB | reps: 10–20
- cues: локти разведены ~70–90°, тянуть к уровню груди; пауза
- errors: шраг; тяга бицепсом
- flags: — | e1rm: no (вспомогательное)
- RU-название — [Fitwill RU](https://fitwill.app/ru/exercise/2618/dumbbell-lying-rear-delt-row/); сидя в наклоне — [Lyfta RU](https://www.lyfta.app/ru/exercise/dumbbell-seated-bent-over-rear-delt-row-922)

---

### 1.9 SCAPULAR / UPPER BACK (7)

**sc01 `barbell_shrug`** — Шраги со штангой | Barbell shrug | aliases: шраги, «пожимание плечами» [?]
- prim: traps_upper | sec: forearm_flexors, levator scapulae, traps_mid
- equip: barbell | level: beginner | isolation | uni: no
- load_type: external | inc: INC_BB | reps: R_ISO (8–15)
- cues: плечи вверх к ушам, вертикально; пауза 1 с; руки как «крюки»
- errors: вращение плечами по кругу; сгибание локтей; кивки головой
- subs: db_home → sc02; elbow/grip → лямки; bw → нет полноценной (вис-шраг на турнике vp11 частично)
- flags: F_NECK_TENSION, F_GRIP_LIMIT | e1rm: possible (но не ключевая метрика)

**sc02 `dumbbell_shrug`** — Шраги с гантелями | Dumbbell shrug
- как sc01, equip dumbbell, inc INC_DB | e1rm: no/possible

**sc03 `trap_bar_shrug`** — Шраги с трэп-грифом | Trap-bar shrug
- как sc01, нейтральный хват, equip trap_bar | e1rm: possible

**sc04 `smith_or_machine_shrug`** — Шраги в Смите / в тренажёре | Smith / machine shrug
- как sc01; inc INC_MACH | e1rm: machine-specific

**sc05 `prone_ytw_raise`** — Подъёмы «Y-T-W» лёжа на наклонной скамье [?] | Prone Y-T-W raise | aliases: «YTW», разведения Y/T
- prim: traps_lower, traps_mid, rear_delt | sec: rhomboids, rotator_cuff_ext
- equip: bench_adjustable + лёгкие dumbbell / без веса | level: beginner | isolation | uni: no
- load_type: external (1–5 кг) / bodyweight | inc: 0.5–1 кг, повторы | reps: R_SMALL_ISO
- cues: грудь на скамье; большой палец вверх; движение от лопаток; медленно
- errors: тяжёлый вес → подъём за счёт поясницы/шрага
- flags: — | e1rm: no

**sc06 `upright_row`** — Тяга штанги к подбородку | Upright row | aliases: протяжка [?]
- prim: traps_upper, delts (лат./перед.) | sec: biceps, forearms
- equip: barbell/ez_bar/dumbbell/cable | level: intermediate | compound | uni: no
- load_type: external | inc: INC_BB/INC_DB | reps: R_ISO
- cues: хват шире плеч; локти до уровня плеч (не выше); гриф близко к телу
- errors: узкий хват + высокий подъём локтей; рывок
- subs: shoulder → тяга к груди широким хватом с канатом / подъём гантелей в стороны / sc01
- flags: **F_IMPINGEMENT_POSITION** (сильный), F_NECK_TENSION | e1rm: no
- примечание: традиционно в программах «на плечи»; включено как scapular-pull для полноты [?]

**sc07 `scapular_retraction_cable`** — Сведение лопаток на нижнем блоке [?] | Scapular retraction (cable / band)
- prim: rhomboids, traps_mid | sec: rear_delt
- equip: cable/band | level: beginner | isolation | uni: no
- load_type: external / band | inc: INC_CABLE | reps: 12–20
- cues: руки прямые; движение только лопатками; пауза 2 с
- errors: сгибание рук | flags: — | e1rm: no
- (vp11 лопаточные подтягивания тоже относятся к scapular)

---

### 1.10 REAR_DELT (7)

**rd01 `face_pull`** — Тяга каната к лицу | Face pull | aliases: фейс-пул, тяга верхнего блока к лицу [?]
- prim: rear_delt, traps_mid, rotator_cuff_ext | sec: rhomboids, traps_lower
- equip: cable + канатная рукоять | level: beginner | isolation (многосуставное по сути) | uni: no
- load_type: external | inc: INC_CABLE | reps: R_SMALL_ISO (12–20)
- cues: блок на уровне лица/выше; тяни концы каната к ушам, разводя их; в конце — «двойной бицепс» (наружная ротация)
- errors: слишком большой вес → отклон корпуса; тяга к шее/груди; локти ниже кистей
- subs: no_cable/home → rd02 резинка; db_home → rd03; bw → hp18 высокая тяга на кольцах к лицу
- flags: — (часто используется как «плечевое здоровье», но это профилактика по практике, не медицинское утверждение) | e1rm: no

**rd02 `band_face_pull`** — Тяга резинки к лицу | Band face pull
- как rd01, load_type band_resistance, INC_BAND, reps 15–25, flags F_BAND_SNAP

**rd03 `bent_over_reverse_fly`** — Разведение гантелей в наклоне | Bent-over dumbbell reverse fly | aliases: махи гантелями в наклоне, обратные разведения, «на заднюю дельту»
- prim: rear_delt | sec: traps_mid, rhomboids, rotator_cuff_ext
- equip: dumbbell | level: beginner | isolation | uni: no
- load_type: external | inc: INC_DB (часто 1 кг шаг — изоляция) | reps: R_SMALL_ISO
- cues: наклон почти параллельно полу; локти слегка согнуты и фиксированы; развести в стороны мизинцами вверх; без инерции
- errors: подъём корпуса/раскачка; сведение лопаток вместо работы дельты (зависит от цели); слишком тяжёлый вес
- subs: lowback → rd04 с упором грудью / rd05 тренажёр
- flags: F_LOWBACK_HINGE (лёгкий), F_SWING_CHEAT | e1rm: no

**rd04 `chest_supported_reverse_fly`** — Разведение гантелей лёжа на наклонной скамье | Incline chest-supported reverse fly
- как rd03, опора грудью; flags: — | e1rm: no

**rd05 `reverse_pec_deck`** — Обратные разведения в тренажёре («обратная бабочка») | Reverse pec deck / rear delt machine
- prim: rear_delt | sec: traps_mid, rhomboids
- equip: machine_selectorized (бабочка) | level: beginner | isolation | uni: no/yes
- load_type: external | inc: стек | reps: R_SMALL_ISO
- cues: грудь к спинке, рукояти на уровне плеч; разводи руки широкой дугой
- errors: сгибание локтей/шраг | e1rm: no

**rd06 `cable_reverse_fly`** — Обратные разведения в кроссовере | Cable reverse fly (crossover)
- как rd05, equip cable, uni опционально (одной рукой) | e1rm: no

**rd07 `band_pull_apart`** — Разведение резинки перед собой [?] | Band pull-apart
- prim: rear_delt, traps_mid, rhomboids | sec: rotator_cuff_ext
- equip: band | level: beginner | isolation | uni: no
- load_type: band_resistance | inc: INC_BAND, повторы | reps: 15–30
- cues: руки прямые на уровне плеч; разведи до касания резинкой груди; медленно назад
- errors: прогиб поясницы; сгибание рук
- flags: F_BAND_SNAP | e1rm: no

---

### 1.11 ELBOW_FLEXION (19)

**ef01 `barbell_curl`** — Подъём штанги на бицепс | Barbell curl | aliases: сгибание рук со штангой стоя, «подъём на бицепс»
- prim: biceps | sec: brachialis, brachioradialis, forearm_flexors
- equip: barbell | level: beginner | isolation | uni: no
- load_type: external | inc: INC_BB (на бицепсе 2.5 кг — большой относительный шаг; микроблины желательны) | reps: R_ISO
- cues: локти у боков и почти неподвижны; поднимай без отклона корпуса; опускай до почти прямых рук
- errors: читинг корпусом; вынос локтей вперёд; неполное опускание
- regress → ef02 EZ, ef03 гантели | progress → вес, медленный негатив
- subs: db_home → ef03; bw → ef18 сгибания в TRX; elbow → ef05 молот / ef02 EZ; shoulder → ef08 Скотт
- flags: F_ELBOW_TENDON (прямой гриф — запястья в супинации), F_SWING_CHEAT | e1rm: yes (опционально — изоляция; разумно трекать «лучший подход»)
- RU: «сгибания рук со штангой» — [ironman.ru](https://ironman.ru/pdf_articles/khoroshenko-nagruzite-seredinu-spiny.pdf)

**ef02 `ez_bar_curl`** — Подъём EZ-штанги на бицепс | EZ-bar curl | aliases: сгибания с изогнутым грифом
- как ef01; equip ez_bar; flags: мягче для запястий/локтей (практика) | e1rm: yes

**ef03 `dumbbell_curl`** — Сгибание рук с гантелями (с супинацией) | Dumbbell curl | aliases: подъём гантелей на бицепс, попеременные сгибания
- prim: biceps | sec: brachialis, brachioradialis
- equip: dumbbell | level: beginner | isolation | uni: yes (попеременно) / no
- load_type: external | inc: INC_DB | reps: R_ISO
- cues: начинать с нейтрали и разворачивать мизинец вверх по ходу подъёма; локоть неподвижен
- errors: размах; плечо выходит вперёд
- flags: — | e1rm: yes (на руку)

**ef04 `incline_dumbbell_curl`** — Сгибание рук с гантелями сидя на наклонной скамье | Incline dumbbell curl
- prim: biceps (длинная головка, растянутое положение) | sec: brachialis
- equip: dumbbell + bench_adjustable (45–60°) | level: intermediate | isolation | uni: no/yes
- load_type: external | inc: INC_DB | reps: R_ISO
- cues: руки висят вертикально позади корпуса; не выносить локти вперёд
- errors: слишком тяжело → подъём плеча
- flags: F_SHOULDER_END_RANGE (передняя поверхность плеча в растяжении) | e1rm: no
- free-exercise-db пример «Alternate Incline Dumbbell Curl» (beginner/isolation/dumbbell/biceps+forearms) — [README](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/README.md)

**ef05 `hammer_curl`** — Молотковые сгибания | Hammer curl | aliases: «молоты», сгибания хватом «молот», сгибания с нейтральным хватом [?]
- prim: brachialis, brachioradialis | sec: biceps, forearm_flexors
- equip: dumbbell | level: beginner | isolation | uni: yes/no
- load_type: external | inc: INC_DB | reps: R_ISO
- cues: ладони друг к другу на всём ходе; локти у корпуса; контролируемое опускание
- errors: размах; разворот кисти
- subs: elbow → обычно лучшая переносимость (практика); bw → ef18 нейтральным хватом
- flags: — | e1rm: yes
- RU-формы: «Молотковый сгиб рук с гантелями на наклонной скамье» — [Fitwill RU](https://fitwill.app/ru/exercise/2494/dumbbell-incline-hammer-curl/); «Сгибание рук с гантелями-молотом» (машинный перевод, неудачное) — [Lyfta RU](https://www.lyfta.app/ru/exercise/dumbbell-hammer-curl-6i5)

**ef06 `cross_body_hammer_curl`** — Молотковые сгибания к противоположному плечу | Cross-body hammer curl
- как ef05, uni yes | e1rm: no

**ef07 `rope_hammer_curl`** — Сгибания с канатом на нижнем блоке («молот» на блоке) | Cable rope hammer curl
- как ef05; equip cable + rope; inc INC_CABLE | e1rm: no

**ef08 `preacher_curl`** — Сгибания на скамье Скотта | Preacher curl (EZ) | aliases: «Скотт», подъём на бицепс на скамье Скотта
- prim: biceps | sec: brachialis
- equip: preacher_bench + ez_bar/dumbbell | level: beginner | isolation | uni: no/yes
- load_type: external | inc: INC_BB/INC_DB | reps: R_ISO
- cues: подмышки плотно на подушке; опускай до почти прямой руки медленно; не отрывать локти
- errors: «бросок» в нижней точке; отрыв плеч от подушки
- flags: F_ELBOW_TENDON (нижняя точка под нагрузкой) | e1rm: yes
- RU: «сгибания рук на скамье Скотта» — [ironman.ru](https://ironman.ru/pdf_articles/khoroshenko-nagruzite-seredinu-spiny.pdf)

**ef09 `machine_biceps_curl`** — Сгибание рук в тренажёре | Machine biceps curl
- как ef08; equip machine_selectorized; inc стек | e1rm: machine-specific

**ef10 `concentration_curl`** — Концентрированные сгибания | Concentration curl
- prim: biceps | sec: brachialis
- equip: dumbbell | level: beginner | isolation | uni: yes
- load_type: external | inc: INC_DB | reps: R_ISO
- cues: сидя, локоть упирается во внутреннюю часть бедра; пауза вверху
- errors: помогать корпусом/бедром | e1rm: no

**ef11 `spider_curl`** — «Паучьи» сгибания [?] | Spider curl
- prim: biceps | sec: brachialis
- equip: dumbbell/ez_bar + bench_adjustable (лёжа грудью) | level: intermediate | isolation | uni: no
- load_type: external | inc: INC_DB | reps: R_ISO
- cues: руки висят вертикально перед скамьёй; подъём без движения плеч
- errors: раскачка | e1rm: no

**ef12 `cable_curl`** — Сгибание рук на нижнем блоке | Cable curl (straight/EZ bar) | aliases: сгибания на блоке
- prim: biceps | sec: brachialis, brachioradialis
- equip: cable | level: beginner | isolation | uni: no
- load_type: external | inc: INC_CABLE | reps: R_ISO
- cues/errors: как ef01 | e1rm: machine-specific
- RU: «сгибания рук на блоке» — [ironman.ru](https://ironman.ru/pdf_articles/khoroshenko-nagruzite-seredinu-spiny.pdf)

**ef13 `bayesian_cable_curl`** — Сгибания «Байесиан» на блоке [? нет устоявшегося русского имени; варианты: «байесовские сгибания», «сгибание спиной к блоку»] | Bayesian cable curl
- prim: biceps (растянутое положение) | sec: brachialis
- equip: cable (нижний блок, стоя спиной) | level: intermediate | isolation | uni: yes
- load_type: external | inc: INC_CABLE | reps: R_ISO
- cues: шаг вперёд от блока, рука отведена назад; сгибание без выноса локтя вперёд
- errors: локоть уходит вперёд; корпус вращается
- flags: F_SHOULDER_END_RANGE (лёгкий) | e1rm: no

**ef14 `reverse_curl`** — Сгибания рук обратным хватом | Reverse curl (barbell/EZ) | aliases: подъём штанги обратным хватом
- prim: brachioradialis, brachialis | sec: forearm_extensors, biceps
- equip: ez_bar/barbell/dumbbell/cable | level: beginner | isolation | uni: no
- load_type: external | inc: INC_BB/INC_DB | reps: R_ISO (10–15)
- cues: хват сверху, запястья прямые; локти у корпуса
- errors: провисание запястий; читинг
- flags: F_ELBOW_TENDON (разгибатели — «теннисный локоть») | e1rm: no

**ef15 `zottman_curl`** — Сгибания Зоттмана | Zottman curl
- prim: biceps (подъём), brachioradialis (опускание) | sec: brachialis, forearm_extensors
- equip: dumbbell | level: intermediate | isolation | uni: no/yes
- load_type: external | inc: INC_DB (вес лимитирован эксцентрикой обратным хватом) | reps: 8–12
- cues: поднять в супинации, вверху развернуть ладони вниз, медленно опустить, внизу вернуть хват
- errors: быстрый негатив | flags: F_ELBOW_TENDON | e1rm: no

**ef16 `drag_curl`** — Сгибания «драг» (протяжка штанги вдоль корпуса) [?] | Drag curl
- prim: biceps | sec: brachialis
- equip: barbell/ez_bar | level: intermediate | isolation | uni: no
- load_type: external | inc: INC_BB | reps: R_ISO
- cues: локти уводятся назад, гриф скользит вдоль корпуса
- errors: подъём плеч | e1rm: no

**ef17 `band_curl`** — Сгибания рук с резинкой | Band curl
- prim: biceps | sec: brachialis
- equip: band | level: beginner | isolation | uni: no
- load_type: band_resistance | inc: INC_BAND, повторы | reps: 12–25
- cues: резинка под стопами; полная амплитуда; медленный негатив
- flags: F_BAND_SNAP | e1rm: no

**ef18 `bodyweight_curl`** — Сгибания рук в петлях TRX / на кольцах | Suspension / ring biceps curl | aliases: «бицепс с собственным весом»
- prim: biceps | sec: brachialis, core
- equip: trx / rings / низкая перекладина (вариант: «бицепс-подтягивание» под перекладиной) | level: beginner-intermediate | isolation | uni: no
- load_type: bodyweight (угол) | inc: угол корпуса, повторы | reps: 8–20
- cues: тело прямое; локти направлены вперёд и остаются на уровне плеч; кисти к лбу
- errors: локти опускаются (превращается в тягу) | flags: F_DOOR_EQUIPMENT | e1rm: no

**ef19 `chin_up_isometric_hold`** — Удержание в верхней точке подтягивания обратным хватом [?] | Flexed-arm hang
- prim: biceps, brachialis, lats | sec: forearm_flexors
- equip: pullup_bar | level: beginner | isolation (изометрия) | uni: no
- load_type: isometric_time | inc: INC_TIME | reps: R_TIME (10–40 с)
- cues: подбородок над грифом, лопатки вниз
- flags: F_FALL_RISK | e1rm: no (трекать секунды); полезно как ступень к первому подтягиванию

---

### 1.12 GRIP_FOREARM (8)

**gf01 `wrist_curl`** — Сгибания кистей со штангой (гантелями) сидя | Wrist curl
- prim: forearm_flexors | sec: —
- equip: barbell/dumbbell + bench | level: beginner | isolation | uni: no/yes
- load_type: external | inc: 1–2.5 кг | reps: 12–25
- cues: предплечья на бёдрах/скамье, кисти свисают; сгибание только в запястье; опустить, позволив грифу скатиться к пальцам (опционально)
- errors: подключение локтей/плеч; слишком большой вес и рывки
- flags: F_ELBOW_TENDON (сгибатели — «локоть гольфиста») | e1rm: no

**gf02 `reverse_wrist_curl`** — Разгибания кистей (обратные сгибания запястий) | Reverse wrist curl
- prim: forearm_extensors | equip: barbell/dumbbell | reps: 15–25 | inc: малые шаги (0.5–1 кг) | flags: F_ELBOW_TENDON | e1rm: no

**gf03 `farmers_walk`** — Прогулка фермера | Farmer's walk / carry
- prim: forearm_flexors, traps_upper | sec: core, glutes, всё тело
- equip: dumbbell / kettlebell / trap_bar / специальные рукояти | level: beginner | compound | uni: no (suitcase carry — yes)
- load_type: carry_time_distance | inc: вес INC_DB + расстояние/время | reps: R_TIME (20–40 м / 30–60 с)
- cues: стоя ровно, плечи вниз-назад; короткие быстрые шаги; дыхание
- errors: сутулость; вес бьёт по ногам
- flags: F_GRIP_LIMIT | e1rm: no (трекать кг × м)

**gf04 `plate_pinch`** — Удержание блинов щипковым хватом [?] | Plate pinch
- prim: forearm_flexors (большой палец) | equip: plate | load_type: isometric_time | inc: INC_TIME, блин больше | reps: 15–45 с | e1rm: no

**gf05 `dead_hang`** — Вис на перекладине | Dead hang | aliases: вис, пассивный вис
- prim: forearm_flexors | sec: lats (растяжение), shoulder
- equip: pullup_bar | level: beginner | isometric | uni: no (вис на одной руке — advanced)
- load_type: isometric_time (→ +вес на поясе) | inc: INC_TIME | reps: R_TIME (20–60 с)
- cues: полный хват большим пальцем; активный вариант — лопатки слегка вниз
- errors: «спрыгивание» без контроля
- flags: F_FALL_RISK, F_SHOULDER_END_RANGE (пассивный вис при чувствительном плече) | e1rm: no
- data: 3×20 с → 3×30 с в 1–2 нед. прогрессии к первому подтягиванию — [Garage Gym Reviews](https://www.garagegymreviews.com/pull-up-progression)

**gf06 `towel_hang`** — Вис на полотенцах | Towel hang
- как gf05; flags F_GRIP_LIMIT; прогресс → vp13

**gf07 `wrist_roller`** — Накручивание груза на роллер [?] | Wrist roller
- prim: forearm_flexors, forearm_extensors | equip: wrist_roller | load_type: external | inc: 1.25–2.5 кг | reps: 2–4 подъёма | e1rm: no

**gf08 `hand_gripper`** — Кистевой эспандер | Hand gripper
- prim: forearm_flexors | equip: gripper (уровни жёсткости) | load_type: band_resistance-подобная (ordinal уровни) | inc: следующий уровень | reps: 8–20 / удержание | e1rm: no

---

### 1.13 Сводная таблица (90 записей)

| # | id | pattern | load_type | e1RM |
|---|---|---|---|---|
| vp01 | pull_up | vertical_pull | bodyweight→bw_added | yes(system) |
| vp02 | wide_grip_pull_up | vertical_pull | bodyweight→bw_added | yes |
| vp03 | chin_up | vertical_pull | bodyweight→bw_added | yes |
| vp04 | neutral_grip_pull_up | vertical_pull | bodyweight→bw_added | yes |
| vp05 | weighted_pull_up | vertical_pull | bw_added | yes |
| vp06 | weighted_chin_up | vertical_pull | bw_added | yes |
| vp07 | band_assisted_pull_up | vertical_pull | bw_assisted_band | approx |
| vp08 | machine_assisted_pull_up | vertical_pull | bw_assisted_machine | yes |
| vp09 | negative_pull_up | vertical_pull | bodyweight (ecc) | no |
| vp10 | feet_assisted_pull_up | vertical_pull | bodyweight | no |
| vp11 | scapular_pull_up | vertical_pull/scapular | bodyweight | no |
| vp13 | towel_pull_up | vertical_pull | bodyweight | no |
| vp14 | ring_pull_up | vertical_pull | bodyweight | yes |
| vp15 | archer_pull_up | vertical_pull | bodyweight | no |
| vp16 | lat_pulldown_wide | vertical_pull | external | yes |
| vp17 | lat_pulldown_close_neutral | vertical_pull | external | yes |
| vp18 | lat_pulldown_reverse | vertical_pull | external | yes |
| vp19 | lat_pulldown_behind_neck | vertical_pull | external | yes |
| vp20 | single_arm_lat_pulldown | vertical_pull | external | yes |
| vp21 | band_lat_pulldown | vertical_pull | band | no |
| vp22 | straight_arm_pulldown | vertical_pull | external | no |
| vp23 | dumbbell_pullover | vertical_pull | external | no |
| vp24 | machine_pulldown | vertical_pull | external | yes |
| hp01–hp25 | (см. выше) | horizontal_pull | external / bodyweight / band | barbell/db/cable/machine — yes; bodyweight/band — no |
| sc01–sc07 | шраги, YTW, тяга к подбородку, сведения лопаток | scapular | external/band | в основном no |
| rd01–rd07 | фейс-пул, разведения, бабочка, резинка | rear_delt | external/band | no |
| ef01–ef19 | сгибания | elbow_flexion | external/band/bodyweight/time | основные (ef01–03, ef05, ef08) — yes |
| gf01–gf08 | кисти, хват | grip_forearm | external/time/carry | no |

(vp12 зарезервирован/переадресован в gf05; итого уникальных записей: 23 vp + 25 hp + 7 sc + 7 rd + 19 ef + 8 gf = **89** + vp11 двойная классификация; при желании добавить `trap_bar_pendlay_row` как отдельную запись (упомянута в [Лайфхакер](https://lifehacker.ru/varianty-tyagi-dlya-spiny/)) → 90.)

### Gaps
- Не удалось получить полный список оборудования/категорий wger через API (robots/403) — известен только fixture мышц.
- ExerciseDB: полные списки bodyParts/equipments/targetMuscles не получены (API 403); из памяти (не проверено): v1 bodyPart включал «back», «upper arms», «lower arms», «shoulders», «neck» — требует проверки.
- MuscleWiki EN страница недоступна; использована RU-локализация.
- Не найдены первичные данные (EMG) по заднему дельту/фейс-пулу, сгибаниям Байесиан/Зоттмана — cues основаны на общей практике.
- Мета-анализ Schoenfeld et al. 2017 по диапазонам повторов (PubMed 28834797) не загрузился (капча) — диапазоны в пресетах R_* являются практическими, а не цитатой.

---

## 2. Стандартные русские названия и разночтения

### Takeaway
Базовые названия устойчивы («Тяга верхнего блока», «Тяга штанги в наклоне», «Молотковые сгибания», «Шраги», «Сгибания на скамье Скотта»), но систематически путаются ось «тип хвата» (прямой/обратный/нейтральный=параллельный) и ось «ширина» (широкий/средний/узкий), а также «к поясу» vs «к животу» vs «к груди». Для БД нужно хранить canonical name_ru + aliases и строить название из атрибутов (снаряд + хват + ширина + положение).

### Cited Findings
- «Тяга верхнего блока» — основное название; варианты хвата: прямой (=широкий в тексте статьи), «узким и нейтральным хватом» (V-рукоять), «обратным хватом», «за голову»; термина «параллельный хват» в статье нет — [Т—Ж](https://t-j.ru/lat-pulldown/)
- Синоним «вертикальная тяга» используется в заголовке статьи «Тяга верхнего блока или вертикальная тяга» — [Спорт Mail](https://sportmail.ru/article/weight-lifting/65783785/)
- MuscleWiki RU: «Тяга верхнего блока», «Тяга верхнего блока обратным хватом», «…узким хватом», «…(нейтральный хват)» — [MuscleWiki RU](https://musclewiki.com/ru-ru/exercises/lower-trapezius)
- Журнальная терминология (ironman.ru): «тяги к поясу», «тяги штанги в наклоне», «тяги гантели одной рукой к поясу», «тяги Т-грифа в наклоне», «тяги к поясу на блоке», «тяги к поясу на тренажёре», «сгибания рук со штангой», «сгибания рук на блоке», «сгибания рук на скамье Скотта» — [Хорошенко, ironman.ru](https://ironman.ru/pdf_articles/khoroshenko-nagruzite-seredinu-spiny.pdf)
- Лайфхакер: «Тяга к животу на блочном тренажёре одной рукой», «Тяга в кроссовере одной рукой», «Т-образная тяга с упором на грудь», «Обратные подтягивания» (= inverted row), «Тяга Пэндли с трэп-грифом» (транслитерация «Пэндли») — [Лайфхакер](https://lifehacker.ru/varianty-tyagi-dlya-spiny/)
- Fitwill RU (переводная база): «Тяга Штанги В Наклоне Широким Хватом», «Тяга Гантелей В Наклоне», «Тяга Верхнего Блока Резинкой Обратным Хватом», «Тяга Гантелей Лёжа На Скамье На Заднюю Дельту», «Молотковый Сгиб Рук С Гантелями На Наклонной Скамье» — [Fitwill bent-over wide](https://fitwill.app/ru/exercise/3721/barbell-bent-over-wide-grip-row/), [band underhand pulldown](https://fitwill.app/ru/exercise/1013/band-underhand-pulldown/), [rear delt row](https://fitwill.app/ru/exercise/2618/dumbbell-lying-rear-delt-row/)
- Lyfta RU (машинный перевод) даёт неудачные формы: «Сгибание рук с гантелями-молотом», «Сгибание молотка с гантелью…», «Тяга Т-образной штанги…», «Изогнутая перекладина лежа» (=cambered bar lying row) — [Lyfta](https://www.lyfta.app/ru/exercise/dumbbell-hammer-curl-6i5), [Lyfta T-bar](https://www.lyfta.app/ru/exercise/lever-lying-t-bar-row-3h)

### Inferences
Рекомендованные canonical-названия и разночтения:

| Канон (name_ru) | Разночтения / алиасы | Комментарий |
|---|---|---|
| Подтягивания прямым хватом | подтягивания широким хватом, классические | «прямой» = пронация (ладони от себя), «широкий» = ширина; в быту смешивают. В БД: grip=pronated, width=medium/wide — две записи (vp01, vp02) |
| Подтягивания обратным хватом | чин-апы, подтягивания узким обратным | «обратный» в RU = супинация; в EN chin-up |
| Подтягивания параллельным хватом | нейтральным хватом | синонимы; выбрать «параллельным» как более частое в залах [?] |
| Австралийские подтягивания | горизонтальные / обратные подтягивания, тяга в висе лёжа | «обратные подтягивания» конфликтует с «подтягивания обратным хватом» → не использовать как канон |
| Тяга верхнего блока (к груди) | вертикальная тяга, тяга блока к груди | «за голову» — отдельная запись с флагом |
| Тяга штанги в наклоне | тяга штанги к поясу | цель тяги (пояс/живот/низ груди) — cue, а не имя |
| Тяга нижнего блока сидя | горизонтальная тяга, тяга блока к поясу/животу | «горизонтальная тяга» также обозначает весь паттерн → неоднозначно |
| Тяга гантели одной рукой в наклоне | тяга гантели к поясу, с упором в скамью | |
| Тяга Т-грифа | Т-тяга, тяга Т-образной штанги, landmine row | |
| Тяга Пендлея | тяга Пэндли | транслитерация не устоялась |
| Тяга каната к лицу | фейс-пул, тяга к лицу | англицизм «фейс-пул» распространён у аудитории 20–40 [?] |
| Разведение гантелей в наклоне | махи в наклоне, обратные разведения, «на заднюю дельту» | |
| Обратная бабочка | разведения в тренажёре на заднюю дельту, reverse pec deck | |
| Шраги со штангой / гантелями | «пожимания плечами» (редко) | англицизм «шраги» — фактический стандарт |
| Тяга штанги к подбородку | протяжка | «протяжка» — жаргон [?] |
| Подъём штанги на бицепс | сгибания рук со штангой | оба нормальные; «сгибания» — более «книжное» |
| Молотковые сгибания | молоты, сгибания хватом «молот» | машинные переводы «молотка» — избегать |
| Сгибания на скамье Скотта | «Скотт», preacher curl | |
| Концентрированные сгибания | концентрированный подъём на бицепс | |
| Сгибания Зоттмана | — | |
| Сгибания «Байесиан» | — | нет устоявшегося RU [?] |
| Прогулка фермера | фермерская прогулка, переноска | |

### Gaps
- sportwiki.to (основной RU-справочник) поиском не выдавался и не загружен — сверка с его названиями не проведена.
- Нет количественных данных, какое название чаще используют пользователи (можно проверить по поисковой статистике Яндекс Wordstat — недоступно в этой сессии).

---

## 3. Как представлять assisted-варианты и вес тела в БД, чтобы работала прогрессия

### Takeaway
Хранить в каждом подходе знаковую «внешнюю» нагрузку (+добавка / −помощь), снимок веса тела и тип нагрузки; эффективную нагрузку считать как `BW × bw_fraction + external`. e1RM считать на эффективной (системной) массе, а показывать пользователю в его терминах (добавка или помощь). Для резинок — ordinal-уровни без точного кг. Прогрессия: двойная прогрессия по повторам, затем «шаг» = +добавка или −помощь (уменьшение противовеса/более тонкая резинка).

### Cited Findings
- Hevy различает 3 типа: Bodyweight, Assisted bodyweight (помощь резинкой/тренажёром), Weighted bodyweight (жилет/блин); вес тела включается в объём только у библиотечных упражнений со 100% BW (подтягивания, чин-апы, отжимания на брусьях, отжимания в стойке); Assisted: эффективная нагрузка = BW − помощь (100−10 = 90 кг × 10 = 900 кг объёма); Weighted: BW + добавка (100+10 = 110 кг); пользовательские bodyweight-упражнения вес тела не учитывают; вес тела нужно вводить (можно обновить прямо в тренировке) — [Hevy Help Center](https://help.hevyapp.com/hc/en-us/articles/38386262243223-Bodyweight-Exercises-in-Hevy-Bodyweight-vs-Assisted-vs-Weighted)
- Hevy не описывает расчёт 1ПМ для bodyweight-упражнений; PR-ы: Bodyweight — лучшие подходы и макс. повторов за сессию; Assisted — макс. повторов в подходе и лучшая сумма повторов; Weighted — лучший объём подхода и максимальный вес — [Hevy Help Center](https://help.hevyapp.com/hc/en-us/articles/38386262243223)
- Калькулятор 1ПМ для подтягиваний с весом (arvo.guru) выдаёт только «добавочный» вес и советует прибавить вес тела для «общей» силы; формулы Epley (точнее 1–6 повт.), Brzycki (консервативнее, 6–12), Lander — [arvo.guru](https://arvo.guru/tools/one-rep-max-calculator/weighted-pull-up)
- Прогрессия к первому подтягиванию (4 нед.): нед.1 австралийские 3×10 + вис 3×20 с; нед.2 вис 3×30 с + лопаточные 3×10; нед.3 лопаточные 3×10, с резинкой 2×6, негативы 2×2; нед.4 лопаточные 3×10, с резинкой 3×6, негативы 3×3; явных порогов перехода нет, неделю можно повторить; успех не гарантирован — [Garage Gym Reviews](https://www.garagegymreviews.com/pull-up-progression)
- Для inverted row сложность регулируется положением ног/высотой (согнутые ноги → прямые → на скамье, медленный негатив, утяжеление) — [Лайфхакер](https://lifehacker.ru/varianty-tyagi-dlya-spiny/)

### Inferences
**Модель данных (предложение):**
```
exercise:
  load_type: external | bodyweight | bodyweight_added | bodyweight_assisted_machine
             | bodyweight_assisted_band | band_resistance | isometric_time | carry_time_distance
  bw_fraction: 1.0 для подтягиваний/чин-апов (как в Hevy); null для тяг с external;
               для inverted/ring row — null (не считать кг, т.к. зависит от угла) [доля BW неизвестна → Gaps]
  progression_family: "vertical_pull_bw"  # связывает vp08 → vp07 → vp09 → vp01 → vp05
  difficulty_rank: int в семействе (лесенка регрессий/прогрессий)

set_log:
  reps, rir|rpe, tempo?, rom_flag?
  external_kg: signed  # +12.5 (пояс), −25 (гравитрон), 0 (чистый вес тела)
  band_level: ordinal|null  # 1=самая толстая (максимум помощи) … N=самая тонкая
  bodyweight_kg_snapshot: float  # взять последний замер; если нет — спросить 1 раз
  angle_level: ordinal|null  # для australian/ring row: высота перекладины/ноги
  duration_s / distance_m  # для висов/переносок

derived:
  effective_load = bw_snapshot*bw_fraction + external_kg      (если bw_fraction задан)
  e1rm_system   = Epley(effective_load, reps) при reps ≤ 10–12
  e1rm_added    = e1rm_system − bw_snapshot*bw_fraction       (показывать для weighted)
```
**Логика прогрессии (rule-based):**
1. Двойная прогрессия: держим нагрузку, пока все рабочие подходы не дошли до верхней границы диапазона (напр. 3×8 → 3×12).
2. Затем «шаг нагрузки» по load_type: external → +INC (округлить до доступного оборудования); bodyweight_added → +1.25–2.5 кг; bodyweight_assisted_machine → противовес −1 шаг стека; bodyweight_assisted_band → band_level+1; bodyweight (без пояса) → перейти на bodyweight_added, когда ≥12 строгих повт. ×3 подхода, или усложнить вариант (difficulty_rank+1); band_resistance/isometric → повторы/время, затем уровень.
3. Переход между вариантами семейства: assisted → свой вес, когда противовес ≤ ~10–15% BW (или самая тонкая резинка) и 3×8 выполнено [порог — практика, не цитата].
4. Изменение веса тела: e1RM считается по снимку BW на дату подхода; при похудении «падение» абсолютной добавки при росте повторов не считается регрессом — сравнивать effective_load.
5. Для тренажёров: e1RM/веса сопоставимы только внутри одного `machine_id` (разные стеки/рычаги) — при смене зала сбрасывать «шаг» и калибровать.

**UI-подсказки:** вводить «помощь» в гравитроне как положительное число «Противовес, кг», а в БД писать отрицательный external_kg; для резинок — цветной выбор из набора пользователя.

### Gaps
- Нет надёжного кг-эквивалента помощи резинок (зависит от растяжения и длины) — трекать ordinal.
- Не найдено валидированной доли BW для inverted row / ring row по углам — не считать e1RM в кг.
- Hevy не публикует, как именно строится 1ПМ для weighted/assisted; формула «системной массы» — общепринятая практика (подтверждается подходом arvo.guru частично), но научной валидации Epley для подтягиваний в этой сессии не найдено.
- Доля веса тела, поднимаемая в подтягивании (<100%, т.к. предплечья/кисти не поднимаются) — источник не найден; Hevy использует 100%.

---

## 4. Как упражнения этой зоны размечены в открытых базах (wger, free-exercise-db, ExerciseDB, MuscleWiki)

### Takeaway
Все четыре базы используют разную гранулярность: free-exercise-db — грубые группы (lats, middle back, traps, biceps, forearms, shoulders) + force=pull; wger — 16 мышц (нет ромбовидных/задней дельты/брахиорадиалиса); ExerciseDB v2 — детальные анатомические названия в верхнем регистре + bodyParts; MuscleWiki — детальные мышцы (lower trapezius, posterior deltoid) и 12+ категорий оборудования. Нужна собственная детальная таксономия + таблица маппинга.

### Cited Findings
- free-exercise-db: force pull/push/static; level beginner/intermediate/expert; mechanic isolation/compound; 12 equipment; 17 мышц (в т.ч. lats, middle back, lower back, traps, biceps, forearms, shoulders); category strength/powerlifting/strongman и др. — [schema.json](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/schema.json)
- wger: muscles 1 Biceps brachii, 2 Anterior deltoid, 3 Serratus anterior, 4 Pectoralis major, 5 Triceps brachii, 6 Rectus abdominis, 7 Gastrocnemius, 8 Gluteus maximus, 9 Trapezius, 10 Quadriceps femoris, 11 Biceps femoris, 12 Latissimus dorsi, 13 Brachialis, 14 Obliquus externus, 15 Soleus, 16 Erector spinae; is_front флаг — [wger fixtures](https://github.com/wger-project/wger/blob/master/wger/exercises/fixtures/muscles.json)
- ExerciseDB v2: equipments, bodyParts, targetMuscles, secondaryMuscles, exerciseType, variations, relatedExerciseIds; AGPL-3.0 — [GitHub](https://github.com/exercisedb/exercisedb-api)
- MuscleWiki: оборудование (Штанга, Гантели, Собственный вес, Тренажёр, Медбол, Гири, Блочные тренажёры, Резинка, Блин, TRX, BOSU, Смит), сложность «Новичок/Расширенный», мышцы вплоть до lower trapezius, posterior deltoid — [MuscleWiki RU](https://musclewiki.com/ru-ru/exercises/lower-trapezius), [posterior-deltoid](https://musclewiki.com/exercises/posterior-deltoid/dumbbells)

### Inferences
**Маппинг собственной таксономии:**

| наша мышца | free-exercise-db | wger | MuscleWiki (вероятно) |
|---|---|---|---|
| lats, teres_major | lats | 12 Latissimus dorsi | lats |
| rhomboids, traps_mid | middle back | 9 Trapezius (нет ромбовидных) | traps-middle / upper back [?] |
| traps_upper | traps | 9 Trapezius | traps |
| traps_lower | middle back / traps [?] | 9 Trapezius | lower trapezius |
| rear_delt | shoulders | — (только anterior deltoid) → нет | posterior deltoid / rear shoulders |
| biceps | biceps | 1 Biceps brachii | biceps |
| brachialis | biceps [?] | 13 Brachialis | biceps/forearms [?] |
| brachioradialis, forearm_* | forearms | — | forearms |
| erectors | lower back | 16 Erector spinae | lower back |

- Лицензии: ExerciseDB — AGPL-3.0 (копилефт; использование кода/данных в закрытом сервисе требует юр. проверки); free-exercise-db — проверить лицензию (в этой сессии не уточнено); wger — AGPL для кода, данные упражнений обычно CC-BY-SA [не проверено].
- В free-exercise-db нет поля «assisted» — гравитрон кодируется как equipment=machine; резинка — bands. Для decision engine этого недостаточно → нужно поле load_type.

### Gaps
- Списки ExerciseDB (bodyParts/equipments/targetMuscles) и wger (equipment, categories) не получены из-за 403/robots.
- Не проверены лицензии данных wger и free-exercise-db (README не показал лицензию в выдержке).
- MuscleWiki EN-страница и API недоступны; точные slug-и групп мышц для middle traps/rhomboids не подтверждены.

---

## 5. Доп. данные EMG по хвату (для пояснений LLM, не для правил)

### Takeaway
Научные данные по «какой хват лучше» ограничены малыми выборками и показывают скорее небольшие различия; для приложения достаточно фиксировать, что пронированный хват в тяге верхнего блока даёт чуть больше активности широчайших, а варианты подтягиваний (обычные/полотенце/подвесные) сопоставимы по широчайшим и бицепсу.

### Cited Findings
- Lusk et al. 2010: 12 мужчин, 70% 1ПМ, 4 хвата (широкий/узкий × прон/супин) тяги верхнего блока к груди: пронированный > супинированного для широчайшей; на средние трапеции и бицепс тип хвата не влиял — [PSU Pure](https://pure.psu.edu/en/publications/grip-width-and-forearm-orientation-effects-on-muscle-activity-dur/)
- Snarr et al. 2017 (J Hum Kinet 58:5–13): 15 тренированных, обычные vs подвесные (TRX-типа) vs на полотенцах подтягивания: нет различий для широчайшей, бицепса, задней дельты; средняя трапеция ниже на полотенцах (~51 vs 61% MVC); в обзоре упомянуто, что Youdas et al. 2010 не нашли значимых различий главных мышц между pull-up и chin-up — [JHK PDF](https://johk.pl/wp-content/uploads/2023/03/10078-58-2017-v58-2017-01.pdf)

### Inferences
- Для «Заменить» вариации хвата можно считать взаимозаменяемыми без потери стимула для широчайших; выбор хвата — по комфорту плеча/локтя.

### Gaps
- Оригинал Youdas 2010 и PMC-статья (PMC449729) не загружены (капча) — данные о chin-up vs pull-up приведены по вторичному упоминанию.
