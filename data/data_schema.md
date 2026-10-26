## 2. Схема данных: пять полей, которых нет ни в одной открытой базе

### 2.1. Почему открытых схем недостаточно

Открытые базы различаются гранулярностью, но все описывают упражнение «для человека», а не «для движка». В free-exercise-db 17 упрощённых мышц, 12 видов оборудования, поля force/level/mechanic/category, причём force, mechanic и equipment могут быть null ([schema.json](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/schema.json)). В wger 16 мышц, и среди них **нет приводящих, средней ягодичной, ромбовидных, задней дельты и плечелучевой**. В оборудовании wger нет тренажёров и стойки, категорий всего 8 ([muscles.json](https://github.com/wger-project/wger/blob/master/wger/exercises/fixtures/muscles.json); [equipment.json](https://github.com/wger-project/wger/blob/master/wger/exercises/fixtures/equipment.json); [categories.json](https://github.com/wger-project/wger/blob/master/wger/exercises/fixtures/categories.json)). ExerciseDB v2 размечает мышцы анатомически подробно (например, «Pectoralis Major Clavicular Head») и хранит связанные упражнения и вариации ([exercisedb-api](https://github.com/exercisedb/exercisedb-api)). MuscleWiki на плане Professional различает primary, secondary и tertiary мышцы ([pricing](https://api.musclewiki.com/pricing.md)). Ни одна из этих схем не хранит паттерн движения, тип нагрузки, шаг и группу замен. Стандартной онтологии паттернов среди открытых баз тоже не нашлось, поэтому таксономия ниже — проектное решение исследователей.

### 2.2. Рекомендуемая схема (PostgreSQL)

| Таблица / поле | Тип и значения | Назначение для движка |
|---|---|---|
| **exercise.id, slug** | uuid, slug латиницей (`back_squat_high_bar`) | Стабильный ключ; slug совпадает с id в каталоге раздела 3 |
| name_ru, name_en, aliases_ru[] | text; aliases с транслитом и английским («RDL», «хип-траст», «румынка») | Поиск. Аудитория 20–40 лет смешивает языки |
| movement_pattern | enum (см. 2.3), одно значение; `pattern_secondary` — опционально | Главный ключ замен и слотов программы |
| family, parent_id, variant_attrs | `family: back_squat`; `variant_attrs: {grip, angle, stance, implement, tempo}` | Замена сначала ищется внутри семейства, потом внутри паттерна |
| mechanic, force, laterality | compound/isolation; push/pull/static; bilateral/unilateral/alternating | Порядок в сессии, учёт стороны |
| level, prereq | beginner/intermediate/advanced; текстовое или машинное условие («≥1 строгое подтягивание») | Фильтр по уровню |
| category | strength / plyometric / conditioning / warmup / mobility / kb_skill | Вид слота |
| **load_type** | barbell · ez_bar · dumbbell (вес одной гантели) · kettlebell · machine_stack · plate_loaded · smith · cable · bodyweight · bodyweight_added · bodyweight_assisted_machine · bodyweight_assisted_band · band_resistance · isometric_time · carry_distance · interval | Определяет, как растёт нагрузка |
| **load_increment_kg**, load_multiplier, bar_weight_kg | Шаг по умолчанию (2.4); множитель 2 для пары гантелей; вес грифа | Шаг округляется к `user_equipment.available_weights[]` |
| bw_fraction | 1,0 для подтягиваний и брусьев (как в Hevy); null для тяг с углом | Эффективная нагрузка для упражнений с весом тела |
| **trackable_for_e1rm** | yes / partial (сравнимо только внутри тренажёра или пользователя) / no | Можно ли считать e1RM и тренд силы |
| default_rep_range (S/H/E), default_rest_s, progression_scheme | Диапазоны по целям «сила / гипертрофия / выносливость»; linear / double / tm_wave / ladder / time | Значения по умолчанию для слота |
| **substitution_group_id, substitution_rank** | Группа = паттерн + пересечение primary-мышц; ранг по сходству | Ранжированные замены |
| subs_explicit | `{noBB:[], DB:[], BW:[], KNEE:[], LB:[], SH:[], EL:[]}` | Детерминированные сценарии замен |
| **progression_of / regression_of, ladder_id, ladder_step** | ссылки на id; номер ступени | Лестницы: отжимания от стены → … → на одной руке |
| **caution_flags[]** | enum (2.5) | Фильтр при жалобах и подсказки для LLM |
| technique_cues_ru[], common_mistakes_ru[] | 2–4 подсказки, 2–3 ошибки | Карточка упражнения и объяснения LLM |
| **source, source_id, license, attribution** | own / free-exercise-db / wger…; Unlicense / CC-BY-SA-4.0 / proprietary | Происхождение и соблюдение лицензий |
| is_active, created_at, updated_at, reviewed_by | — | Активный набор MVP, вычитка методистом |
| **exercise_muscle** | exercise_id, muscle_id, role (primary/secondary/stabilizer), **volume_weight** (1,0 / 0,5 / 0,25 / 0) | Дробный подсчёт объёма |
| muscle, muscle_group_ui | Анатомические мышцы (около 30) → UI-группы (около 14) | Объём считается по UI-группам |
| exercise_equipment, equipment | required bool; у оборудования свой load_type | Фильтр «что есть дома или в зале» |
| media | type (image/gif/mp4/webm), url, poster, width, height, **license, attribution, source** | Отдельная лицензия у каждого файла |
| exercise_translation | lang, name, cues | На будущее. На старте хватит колонок `_ru` и `_en` |

Так выглядит запись в seed-файле JSON (пример составлен по полям каталога):

```json
{
  "id": "romanian_deadlift_bb", "family": "romanian_deadlift",
  "name_ru": "Румынская тяга", "name_en": "Barbell Romanian Deadlift",
  "aliases_ru": ["румынская становая", "РДЛ", "RDL", "румынка"],
  "movement_pattern": "hinge", "mechanic": "compound", "laterality": "bilateral",
  "level": "beginner", "category": "strength",
  "muscles": [{"m":"hamstrings","role":"primary","w":1.0},{"m":"glute_max","role":"primary","w":1.0},
              {"m":"erector_spinae","role":"secondary","w":0.5},{"m":"adductors","role":"secondary","w":0.5},
              {"m":"forearms","role":"stabilizer","w":0.25}],
  "equipment": ["barbell"], "load_type": "barbell", "load_increment_kg": 2.5,
  "trackable_for_e1rm": "yes", "default_rep_range": {"S":[4,6],"H":[6,12]},
  "progression_scheme": "double", "regression_of": "romanian_deadlift_db",
  "subs_explicit": {"noBB":["romanian_deadlift_db","kb_deadlift"],"DB":["romanian_deadlift_db","single_leg_rdl"],
                    "BW":["single_leg_rdl","slider_leg_curl","hip_thrust_bw"],"LB":["seated_leg_curl","hip_thrust_bb","cable_pull_through"]},
  "caution_flags": ["lumbar_flexion_load","high_eccentric_doms"],
  "source": "own", "license": "proprietary", "reviewed_by": null
}
```

### 2.3. Паттерны движения (enum `movement_pattern`)

Список объединяет словари четырёх файлов с упражнениями. Расхождения между файлами разрешены так: в `scapular` входят шраги и сведения лопаток, в `rear_delt` — задняя дельта и ротаторы. Пуловер отнесён к `vertical_pull`, но у него есть второй паттерн `chest_isolation`. Тяга к подбородку отнесена к `scapular`, с паттерном `shoulder_isolation` как вторым.

| Код (в таблицах) | enum | Русское название | Примеры |
|---|---|---|---|
| SQ | squat | Присед (коленно-доминантный) | присед, жим ногами, гакк |
| HG | hinge | Наклон в тазобедренном | становая, румынская, махи гирей |
| LU | lunge | Выпад / одна нога | болгарские выпады, зашагивания |
| HE | hip_extension | Разгибание бедра (ягодичные) | хип-траст, кикбэк |
| KE | knee_extension | Разгибание колена | разгибание ног |
| KF | knee_flexion | Сгибание колена | сгибание ног, нордические сгибания |
| CA | calf_raise / ankle_dorsiflexion | Икры / передняя большеберцовая | подъёмы на носки |
| AD / AB | hip_adduction / hip_abduction | Приведение / отведение бедра | сведение и разведение ног |
| HPU / VPU | horizontal_push / vertical_push | Горизонтальный / вертикальный жим | жим лёжа, жим стоя |
| CHI | chest_isolation | Изоляция груди (сведения) | разводка, кроссовер |
| SHI | shoulder_isolation | Изоляция дельт (отведение, подъём вперёд) | махи в стороны |
| EE | elbow_extension | Разгибание локтя (трицепс) | французский жим |
| VPL / HPL | vertical_pull / horizontal_pull | Вертикальная / горизонтальная тяга | подтягивания, тяга в наклоне |
| SC | scapular | Лопатки и трапеции | шраги, Y-T-W |
| RD | rear_delt | Задняя дельта и ротаторы | фейс-пул, обратная бабочка |
| EF | elbow_flexion | Сгибание локтя (бицепс) | подъём штанги на бицепс |
| GR | grip_forearm | Хват и предплечья | вис, сгибания кистей |
| C-AE / C-AR / C-FL / C-RO / C-EX | core_anti_extension / core_anti_rotation (вкл. anti-lateral flexion) / core_flexion / core_rotation / core_extension | Кор | планка, Паллоф, скручивания, дровосек, супермен |
| CR | carry | Переноски | прогулка фермера |
| KB | kb_skill (баллистика и навык) | Гиревые навыки | взятие на грудь, рывок, турецкий подъём |
| PLY / COND / WU / MOB | plyometric / conditioning / warmup / mobility | Плиометрика, кондиция, разминка, мобильность | — |

### 2.4. Мышцы в два уровня и `volume_weight`

| UI-группа (около 14) | Анатомические мышцы (слой 1) | Маппинг free-exercise-db / wger |
|---|---|---|
| Грудь | pec_major_sternal (средняя и нижняя), pec_major_clavicular (верх) | chest / Pectoralis major |
| Спина: ширина | lats, teres_major | lats / Latissimus dorsi |
| Спина: толщина | rhomboids, traps_mid, traps_lower | middle back / Trapezius (ромбовидных нет) |
| Трапеции | traps_upper | traps / Trapezius |
| Передняя дельта | front_delt | shoulders / Anterior deltoid |
| Средняя дельта | side_delt | shoulders / — |
| Задняя дельта | rear_delt, rotator_cuff_ext | shoulders / — (нет в wger) |
| Бицепс | biceps, brachialis, brachioradialis | biceps, forearms / Biceps brachii, Brachialis |
| Трицепс | triceps (long, lateral, medial) | triceps / Triceps brachii |
| Предплечья | forearm_flexors, forearm_extensors | forearms / — |
| Квадрицепс | quadriceps (+ rectus_femoris) | quadriceps / Quadriceps femoris |
| Задняя поверхность бедра | hamstrings | hamstrings / Biceps femoris |
| Ягодичные | glute_max, glute_med_min | glutes / Gluteus maximus (средней нет) |
| Приводящие | adductors | adductors / — (нет в wger) |
| Икры | gastrocnemius, soleus, tibialis_anterior | calves / Gastrocnemius, Soleus |
| Пресс и кор | rectus_abdominis, obliques, transverse_abdominis, quadratus_lumborum, hip_flexors | abdominals / Rectus abdominis, Obliquus externus |
| Поясница | erector_spinae | lower back / Erector spinae |
| Зубчатая | serratus | — / Serratus anterior |

Правило подсчёта: **эффективный подход = рабочий подход (без разминочных и пропущенных) × `volume_weight`**. Порог близости к отказу (например, RIR ≤ ~4) — оценка без источника. Пользователю показывать «прямые + дробные», а в метрику недельной нагрузки брать дробную сумму. Такая модель совместима с основными моделями Pelland ([SportRxiv](https://sportrxiv.org/index.php/server/preprint/view/460)) и с Boostcamp, где жим лёжа = 1 подход груди + 0,5 трицепса ([Boostcamp](https://www.boostcamp.app/features/muscle-tracker)). Hevy считает подходы на группу в неделю, но метод не раскрывает. Правило «1 / 0,5» в блоге Hevy автор сам называет неточной эвристикой ([Hevy features](https://www.hevyapp.com/features/sets-per-muscle-group-per-week/); [Hevy blog](https://www.hevyapp.com/how-many-sets/)). Ориентиры исследований о том, какие мышцы реально растут, полезнее ЭМГ. Присед почти не растит хамстринги ([SBS: squats and adductors](https://www.strongerbyscience.com/squats-adductors/)), поэтому хамстрингам в приседе нужен вес ≤0,25. Хип-траст при сходном росте ягодиц почти не растит квадрицепс ([Plotkin 2023](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1279170/full)).

### 2.5. Тип нагрузки, шаги и e1RM

| load_type | Шаг по умолчанию | Как растёт нагрузка | e1RM |
|---|---|---|---|
| barbell | +2,5 кг суммарно (1,25 на сторону); новичку присед и тяга +5; при микроблинах +1 | Вес | Да (Epley ≤10 повт.) |
| ez_bar | Как штанга; вес грифа 7–10 кг уточнять | Вес | Частично |
| dumbbell | Зал: 2 или 2,5 кг на гантель (ряды 10-12-14 или 10-12,5-15); разборные дома 0,5–1,25 | Повторения до верхней границы, потом шаг | Да при ≥ ~10 кг на гантель, иначе по повторениям |
| kettlebell | +4 кг (8-12-16-20-24-28-32; у части брендов есть 14/18/22) | Повторения → подходы (до 5) → плотность → следующая гиря | Частично |
| machine_stack / cable | Шаг стека 2,5–10 кг (часто 5–7); у блоков с полиспастом килограммы несопоставимы | Повторения → шаг стека | Частично, отдельно по каждому `machine_id` |
| plate_loaded | +5 кг (по 2,5 на сторону), на одну сторону +2,5 | Вес | Частично |
| smith | Как штанга; вес грифа 0–25 кг в зависимости от противовеса | Вес | Отдельная шкала, со свободной штангой не сравнивать |
| bodyweight | — | Повторения → темп и пауза → рычаг или амплитуда → следующая ступень лестницы или добавочный вес | Нет (для подтягиваний и брусьев — по системной массе) |
| bodyweight_added | +1,25–2,5 кг (пояс, жилет, рюкзак) | Добавочный вес | Да: e1RM системы = Epley(BW×bw_fraction + добавка) |
| bodyweight_assisted_machine | −1 шаг противовеса (5–7 кг) | Уменьшение помощи (знак инвертирован) | Да через BW − противовес |
| bodyweight_assisted_band / band_resistance | Порядковый уровень резины (1…N) | Повторения → натяжение → следующая резина | Нет |
| isometric_time | +5–10 с | Время → следующая вариация | Нет |
| carry_distance | +2–4 кг на руку или +метры | кг × м | Нет |

Принципы шага взяты из заметок по каталогу; правило «2–10% за шаг» — из ACSM 2009 ([PDF](https://sfu.ca/~ryand/kin343/ACSMresistance.pdf)). Модель упражнений с весом тела повторяет Hevy, где три типа: Bodyweight, Assisted (BW − помощь) и Weighted (BW + добавка) ([Hevy Help](https://help.hevyapp.com/hc/en-us/articles/38386262243223-Bodyweight-Exercises-in-Hevy-Bodyweight-vs-Assisted-vs-Weighted)). Калькулятор arvo.guru считает 1ПМ подтягиваний по добавочному весу и советует прибавлять вес тела для «общей» силы ([arvo.guru](https://arvo.guru/tools/one-rep-max-calculator/weighted-pull-up)). В лог подхода нужно писать `external_kg` со знаком (+12,5 — пояс, −25 — гравитрон), снимок веса тела, уровень резины и уровень угла. Для австралийских подтягиваний и тяги на кольцах долю веса тела не нашли, поэтому e1RM в кг для них не считать.

### 2.6. Флаги нагрузки (enum `caution_flags`)

| Код в таблицах | enum | Смысл | Когда фильтровать |
|---|---|---|---|
| ОСЕВ | axial_spinal_load | Осевая нагрузка на позвоночник | Жалоба «поясница» |
| П-СГ / П-РЗ | lumbar_flexion_load / lumbar_extension_load | Сгибание или переразгибание поясницы под нагрузкой | «поясница» |
| ГЛУБ / КОЛ / ПФ | deep_knee_flexion / knee_pain / patellofemoral_sensitive | Глубокое сгибание, нагрузка на колено, надколенник | «колено» |
| ТБС | hip_impingement_deep_flexion | Глубокое сгибание в тазобедренном | «тазобедренный» |
| ГОЛЕН / БАЛ | ankle_mobility_required / balance_demand | Мобильность голеностопа / баланс | Новичок, 50+ |
| ХВАТ | grip_limited | Хват кончается раньше целевых мышц | Предложить лямки |
| ВАЛ | hernia_valsalva | Натуживание, внутрибрюшное давление | Грыжа, давление, беременность |
| БЕР | pregnancy_supine_caution | Положение лёжа на спине | Беременность |
| DOMS | high_eccentric_doms | Сильная крепатура от эксцентрики | Новичок, возврат |
| ПЛ1–3 / ЛОК1–3 / ЗАП1–3 | shoulder / elbow / wrist (low / med / high) | Нагрузка на плечо, локоть, запястье | «плечо», «локоть», «запястье» |
| ИМП / ПЛ-КР | impingement_position / shoulder_end_range | Отведение с внутренней ротацией; крайние позиции над головой | «плечо» |
| ШЕЯ | neck_strain | Напряжение шеи | «шея» |
| ПАД / ОПОРА / РЕЗ! | fall_risk / door_equipment / band_snap | Падение; самодельная опора (дверь, стол); риск разрыва резины | Дом, 50+ |
| ЧИТ | swing_cheat | Склонность к раскачке | Подсказка LLM |
| УДАР / ПЕРЕВ | high_impact / inverted | Ударная нагрузка; перевёрнутое положение | Вес, колени, беременность, гипертония, глаукома |

Флаги — это **теги нагрузки, а не диагнозы**. Их задача — исключить или понизить в ранге упражнения при жалобе пользователя и подсказать LLM безопасную формулировку.

### 2.7. Правило «отдельная запись или поле variant»

Отдельный id нужен, если выполняется хотя бы одно условие. (1) Меняется снаряд: штанга, гантели или тренажёр, а с ним шаг и округление. (2) Рабочий вес систематически отличается больше чем на ~10%: high-bar и low-bar, фронтальный и классический присед, классика и сумо, хип-траст и мостик с пола. Иначе ломаются e1RM и двойная прогрессия. (3) Меняется паттерн или профиль флагов: RDL и становая на прямых ногах, выпад вперёд и назад. Постановка стоп, ширина хвата (кроме узкого), наклон корпуса, угол троса и темп хранятся в `variant_attrs`. Порог 10% — проектное решение, исследований под него нет. Есть данные в пользу разделения: сгибание ног сидя дало больший рост хамстрингов, чем лёжа (+14,1% против +9,3%) ([Maeo 2021](https://pubmed.ncbi.nlm.nih.gov/33009197/)). Разгибание трицепса над головой дало примерно в 1,4 раза больший рост, чем разгибание вниз ([Maeo 2022](https://pubmed.ncbi.nlm.nih.gov/35819335/)). Наклон 30° лучше всего нагружает ключичную часть груди, а при 45° и больше нагрузка уходит на дельту ([Rodríguez-Ridao 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7579505/)). При этом махи с гантелями и на блоке дали одинаковую гипертрофию ([Larsen 2025](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2025.1611468/full)), а варианты хвата в подтягиваниях дают сопоставимую активность широчайших ([Snarr 2017](https://johk.pl/wp-content/uploads/2023/03/10078-58-2017-v58-2017-01.pdf); [Lusk 2010](https://pure.psu.edu/en/publications/grip-width-and-forearm-orientation-effects-on-muscle-activity-dur/)). Поэтому такие варианты можно менять между собой без потери стимула.

Алгоритм кнопки «Заменить»: (1) явные `subs_explicit` по сценарию пользователя → (2) то же `family` → (3) тот же `movement_pattern` с наибольшим пересечением primary-мышц → (4) фильтр по `equipment_available` → (5) исключить упражнения, чьи флаги пересекаются с жалобами → (6) ранжировать по уровню и `substitution_rank`. Если при замене меняется `load_type` или конкретный тренажёр, история e1RM не переносится, движок калибрует вес заново.

### 2.8. Источник данных: free-exercise-db как основа, своя русская редактура поверх

| Источник | Объём | Русский | Медиа | Лицензия данных | Хранить у себя в РФ | Вердикт |
|---|---|---|---|---|---|---|
| free-exercise-db | 800+ | нет | статичные JPG (лицензия изображений отдельно не указана) | **Unlicense** | да | **Основа** структуры и английских названий ([GitHub](https://github.com/yuhonas/free-exercise-db)) |
| wger | не проверено (API 403) | UI переведён на 78%, переводы упражнений — в самой базе | фото и SVG, часть из Википедии, файл SOURCES в каждой папке | CC BY-SA по записям; код AGPL-3.0 | да, с атрибуцией и share-alike | Только отдельные записи с атрибуцией в карточке; код в бэкенд не встраивать ([README](https://cdn.jsdelivr.net/gh/wger-project/wger@master/README.md); [docs](https://wger.readthedocs.io/en/latest/); [Weblate](https://hosted.weblate.org/projects/wger/); [LICENSE](https://github.com/wger-project/wger/blob/master/LICENSE.txt)) |
| ExerciseDB, датасет на Gumroad | 1 500+ с GIF и JSON | не указан | GIF до 1080p | проприетарная, разово $300, «includes commercial rights» | вероятно; ToS не проверены | Кандидат на медиа после проверки ToS ([Gumroad](https://exercisedb.gumroad.com/l/exercisedb); [Terms](https://exercisedb.notion.site/ExerciseDB-API-Terms-of-Use-226983b728ca8090bf7be79564e4b356)) |
| ExerciseDB / AscendAPI | 11 000+ (заявлено) | — | видео, GIF, фото | код AGPL; медиа не указаны; playground «not recommended for production» | неясно | Как справочник ([GitHub](https://github.com/exercisedb/exercisedb-api); [exercisedb.dev](https://exercisedb.dev/)) |
| MuscleWiki API | не указан | 14 языков на Growth+ (русский не проверен) | видео только стримингом | проприетарная, $10–200 в месяц | **нет**: медиа хранить запрещено, текст — до 30 дней | **Исключить**: право Каймановых островов, доступ могут отозвать сразу, обязательна атрибуция ([Terms](https://api.musclewiki.com/api-terms); [pricing](https://api.musclewiki.com/pricing.md)) |
| API Ninjas | 3 000+ | нет | картинки только на premium | проприетарная; на бесплатном плане коммерция запрещена | неясно | Нет ([API Ninjas](https://www.api-ninjas.com/api/exercises)) |
| hasaneyldrm/exercises-dataset | 1 324 | инструкции (заявлено 10 языков, в About — 6) | GIF 180×180 © Gym visual | MIT на текст; медиа по условиям Gym visual | проверить | Источник текстов и сверки ([GitHub](https://github.com/hasaneyldrm/exercises-dataset)) |
| Workout.cool | — | — | ссылки на YouTube | код MIT; источник базы не назван | — | Пример двуязычной модели `name / name_en` ([GitHub](https://github.com/Snouzy/workout-cool)) |
| ExRx, Liftosaur, sportwiki.to | — | — | — | страницы не загрузились | — | ExRx исключить (по памяти, переиспользование без разрешения запрещено; не проверено) |

Рабочая последовательность такая. Взять free-exercise-db и вручную отобрать 150–300 упражнений, полезных для самостоятельной силовой. Объединить их с каталогом раздела 3 (он шире по домашним вариантам и лестницам). Сделать машинный перевод и обязательную редактуру тренером. Добавить свою разметку паттернов, весов мышц, шагов, флагов и замен. Тексты free-exercise-db можно переводить и менять без обязательств. Готового качественного русскоязычного открытого датасета с понятной лицензией не нашли. Справочник упражнений не содержит персональных данных, поэтому 152-ФЗ на выбор источника не влияет. Важно другое: медиа и данные должны храниться у себя, а не запрашиваться из-за рубежа во время работы приложения, иначе страдает доступность.

### 2.9. Медиа: купить одну стилистическую серию и хостить в РФ

| Вариант | Стоимость | Ограничения | Рекомендация |
|---|---|---|---|
| Статичные фото free-exercise-db (старт и финиш) | 0 | Лицензия изображений не указана, происхождение не названо — проверить issues репозитория | MVP, если лицензия подтвердится |
| Gym visual | Иллюстрация <$0,75, GIF $0,9, видео $6 за штуку (после 10 / 10 / 5 в корзине) | Текст лицензии на главной не раскрыт | Для 150–300 упражнений около $135–270 (оценка) ([Gym visual](https://www.gymvisual.com/)) |
| ExerciseDB Gumroad | $300 разово за 1 500+ GIF | Self-hosting и ToS не проверены; есть бесплатный сэмпл на 30 упражнений | Альтернатива после проверки ToS ([Gumroad](https://exercisedb.gumroad.com/l/exercisedb)) |
| WorkoutLabs | Вся библиотека (679) от $1 200 в год или $3 500+ бессрочно; одна иллюстрация от $15 в год | Зарегистрированы в US Copyright Office; метаданные — платное дополнение | Если нужна векторная серия ([WorkoutLabs](https://workoutlabs.com/exercise-illustrations-licensing/)) |
| Hyperhuman | Цены не опубликованы | API только на Ultra annual или Enterprise; территория и каналы — в каждой лицензии | Для видео-классов, не для MVP ([Hyperhuman](https://hyperhuman.cc/fitness-content-licensing)) |
| Встраивание YouTube | 0 | В США встраивание признано покрытым лицензией YouTube (Richardson v. Townsquare; по комментарию к статье, подтверждено 2-м округом 23.04.2026), но к РФ это напрямую не применяется. YouTube в РФ ненадёжен как канал, ролик может удалить автор | Только временный fallback через официальный плеер ([Copyright Lately](https://copyrightlately.com/sdny-social-media-embedding/)) |
| Своя съёмка | Не оценивалась по источникам | Несколько съёмочных дней на 150 упражнений, 2 ракурса (оценка) | Единственный вариант без лицензионных ограничений, с русскими подписями |

Медиа одной стилистической серии хранить в своём S3-совместимом хранилище в РФ, конвертировать GIF в WebM/MP4 (они легче) и отдавать с lazy-load. У каждого файла в таблице `media` хранить свою лицензию и атрибуцию. Смешивать фото wger, GIF Gym visual и видео не стоит: это ухудшает впечатление от интерфейса.

---