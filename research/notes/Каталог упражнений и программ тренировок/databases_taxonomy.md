# Базы упражнений, медиа и таксономии для библиотеки упражнений (октябрь 2026)

Контекст: русскоязычный Telegram Mini App, бэкенд в РФ (152-ФЗ), rule-based движок адаптации, замены с сохранением паттерна движения, округление весов под оборудование, карточки с техникой (видео/анимация позже, lazy-load).

Ограничения сбора: прямой доступ к wger.de API, raw.githubusercontent и GitHub API из среды исследования был заблокирован прокси (403), поэтому точные счётчики wger и free-exercise-db проверить выгрузкой не удалось. Всё, что не подтверждено источником, вынесено в «Inferences» или «Gaps». Юридические выводы носят информационный характер, это не юридическая консультация.

## Вопрос 1. Какой источник можно законно использовать для наполнения коммерческого приложения и с какими обязательствами?

### Takeaway
Самый безопасный юридически вариант для данных — free-exercise-db (Unlicense, около 800 упражнений, есть статичные изображения, русского языка нет), который используется как «скелет» + собственная русская редактура и собственная таксономия. wger подходит, но несёт share-alike (CC BY-SA) на данные и разнородные лицензии по каждой записи и изображению. Коммерческие API (MuscleWiki, ExerciseDB/AscendAPI, API Ninjas) дают медиа и объём, но запрещают или ограничивают хранение и рехостинг, что плохо сочетается с хостингом в РФ и офлайн-кэшем. Для медиа лучше всего выкупить разовую лицензию (ExerciseDB-датасет на Gumroad, Gym visual, WorkoutLabs) или снимать своё.

### Cited Findings

**free-exercise-db (github.com/yuhonas/free-exercise-db)**
- Лицензия репозитория — Unlicense (public domain dedication); README говорит о «800+» упражнениях; в каждом упражнении есть папка с изображениями в `exercises/`. Отдельная лицензия для изображений не указана, происхождение изображений в README не названо — [GitHub yuhonas/free-exercise-db](https://github.com/yuhonas/free-exercise-db)
- Поля: id, name, force, level, mechanic, equipment, primaryMuscles, secondaryMuscles, instructions, category, images; force/mechanic/equipment могут быть null (данные неполные) — [GitHub](https://github.com/yuhonas/free-exercise-db)
- Значения enum из schema.json: force = static/pull/push/null; level = beginner/intermediate/expert; mechanic = isolation/compound/null; equipment = medicine ball, dumbbell, body only, bands, kettlebells, foam roll, cable, machine, barbell, exercise ball, e-z curl bar, other, null; мышцы (17) = abdominals, abductors, adductors, biceps, calves, chest, forearms, glutes, hamstrings, lats, lower back, middle back, neck, quadriceps, shoulders, traps, triceps; category = powerlifting, strength, stretching, cardio, olympic weightlifting, strongman, plyometrics — [schema.json](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/schema.json)
- В репозитории 93 коммита и CI; дату последнего коммита подтвердить не удалось — [GitHub](https://github.com/yuhonas/free-exercise-db)

**wger (wger.de, github.com/wger-project/wger)**
- Код — AGPL-3.0-or-later; «Exercise/Ingredient Data: Creative Commons (see individual entries)»; документация — CC-BY-SA-4.0 — [wger README](https://cdn.jsdelivr.net/gh/wger-project/wger@master/README.md)
- В документации: начальные данные упражнений и продуктов под CC BY-SA 3.0; часть изображений взята из Википедии, в каждой папке с изображениями есть файл SOURCES с деталями — [wger docs](https://wger.readthedocs.io/en/latest/)
- Публичные эндпоинты (например, список упражнений) доступны без авторизации; троттлинг есть только у ингредиентов, регистрации и auth, «All other endpoints are unthrottled»; OpenAPI-схема лежит на /api/v2/schema — [wger API docs](https://wger.readthedocs.io/en/latest/api/api.html)
- AGPL §13: если вы модифицируете и запускаете код wger как сетевой сервис, нужно предлагать пользователям исходники модифицированной версии — [wger LICENSE](https://github.com/wger-project/wger/blob/master/LICENSE.txt)
- Weblate: язык Russian переведён на 78% по UI-компонентам (Web App, Webapp, Mobile App, Play Store, Glossary); отдельного компонента «Exercises» нет — переводы упражнений ведутся в самой базе wger, а не на Weblate — [Weblate wger](https://hosted.weblate.org/projects/wger/)

**ExerciseDB / AscendAPI**
- Бесплатный V1 API: «1,500 exercises with GIFs»; цены по запросу (support@ascendapi.com, docs.ascendapi.com) — [exercisedb.dev](https://exercisedb.dev/)
- Репозиторий exercisedb-api: лицензия AGPL-3.0 (на код); заявлено 11 000+ упражнений, 15 000+ видео, 20 000+ изображений, 5 000+ GIF; поля V2: exerciseId, name, imageUrl, equipments, bodyParts, gender, exerciseType, targetMuscles, secondaryMuscles, videoUrl, keywords, overview, instructions, exerciseTips, variations, relatedExerciseIds; лицензия на медиа не указана, playground «not recommended for production» — [GitHub exercisedb/exercisedb-api](https://github.com/exercisedb/exercisedb-api)
- Датасет на Gumroad: 1 500+ упражнений с GIF и JSON (exercises, body parts, equipment, muscles), цена $300, разовая покупка «includes commercial rights», планы Starter (180p/360p), Standard (+720p), Premium (+1080p); бесплатный сэмпл на 30 упражнений; про self-hosting и языки на странице ничего не сказано — [Gumroad ExerciseDB](https://exercisedb.gumroad.com/l/exercisedb)
- Terms of Use ExerciseDB (Notion) не загрузились — текст условий проверить не удалось — [ExerciseDB Terms](https://exercisedb.notion.site/ExerciseDB-API-Terms-of-Use-226983b728ca8090bf7be79564e4b356)

**MuscleWiki API**
- Тарифы: BASIC бесплатно (500 вызовов/мес, только playground); TESTING $10 (1 000, только английский); GROWTH $39.99 (30 000, 14 языков); PROFESSIONAL $99.99 (100 000, + рутины, bodymaps, secondary/tertiary muscles); ENTERPRISE $199.99 (300 000); годовая оплата −25%; top-up $10 за 5 000; коммерческое использование включено во все платные планы — [MuscleWiki pricing](https://api.musclewiki.com/pricing.md)
- Условия: метаданные можно кэшировать до 30 дней, миниатюры и bodymaps — до 24 часов, видео только транзитно; запрещено скачивать/хранить медиа в своём CDN или облаке, рехостить, перекодировать или скрывать брендинг MuscleWiki; обязательная строка «Exercise data and videos provided by MuscleWiki.com» в ToS или Privacy Policy; запрещено строить конкурирующий датасет и обучать ML; проксирование на сервере допустимо, если видео не пишется на диск; право — Каймановы острова; доступ можно отозвать немедленно — [MuscleWiki API Terms](https://api.musclewiki.com/api-terms)

**API Ninjas Exercises**
- Заявлено «over 3000 exercises»; поля: name, type, muscle (16 групп), difficulty (beginner/intermediate/expert), instructions, equipments, safety_info; изображения (старт/финиш) только на premium; максимум 5 результатов за запрос; «Commercial use of the Exercises API is not permitted on the free tier» — [API Ninjas Exercises](https://www.api-ninjas.com/api/exercises)

**Открытые приложения и производные датасеты**
- Workout.cool: код под MIT; сид в CSV (name/name_en, description, full_video_url и т.д.; атрибуты TYPE/PRIMARY_MUSCLE хранятся отдельными строками); видео в сэмпле ссылаются на YouTube; источник базы упражнений не назван, а автор упоминает лицензирование видео как проблему исходного проекта — [GitHub Snouzy/workout-cool](https://github.com/Snouzy/workout-cool)
- hasaneyldrm/exercises-dataset: 1 324 упражнения; код и тексты под MIT; медиа «© Gym visual», распространяются с разрешения в 180×180, переиспользование регулируется условиями Gym visual; в README заявлены инструкции на 10 языках, включая русский (в описании About — «6 languages», противоречие); поля: id, name, category, body_part, equipment, instructions, instruction_steps, muscle_group, secondary_muscles, target, media_id, gif_url, attribution — [GitHub hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset)
- Liftosaur, ExRx: страницы не загрузились (client_error / robots_disallowed) — [Liftosaur GitHub](https://github.com/liftosaur/liftosaur), [ExRx permission](https://exrx.net/Questions/Permission)

### Inferences
- **Сводная таблица (факты из источников выше, оценки помечены «~»):**

| Источник | Объём | Русский | Медиа | Лицензия данных | Коммерция | Хранение у себя (РФ) |
|---|---|---|---|---|---|---|
| free-exercise-db | 800+ | нет | статичные фото (JPG) | Unlicense | да, без обязательств | да |
| wger | ~сотни–тыс. (не проверено) | частично, качество неровное (оценка) | фото/SVG, часть из Википедии | CC BY-SA (по записям) | да, с атрибуцией и share-alike | да |
| ExerciseDB Gumroad | 1 500+ | нет (не указано) | GIF до 1080p | проприетарная, разово $300 | да (заявлено) | вероятно да, нужно проверить ToS |
| ExerciseDB/Ascend API | 11 000+ (заявл.) | не указано | видео/GIF/фото | проприетарная | по плану | не ясно |
| MuscleWiki API | не указано | в 14 языках (Growth+) — состав не проверен | видео | проприетарная | платные планы | **нет** (медиа не хранить, текст ≤30 дней) |
| API Ninjas | 3 000+ | нет | фото на premium | проприетарная | только premium | не ясно |
| exercises-dataset (Gym visual) | 1 324 | да (инструкции) | GIF 180×180 | MIT (текст) + © Gym visual (медиа) | медиа по условиям Gym visual | нужно проверить |

- **Рекомендация (вывод):** сид = free-exercise-db (структура и английские названия) → ручной отбор ~150–300 упражнений, релевантных для самостоятельной силовой (а не все 800) → своя русская редактура и своя таксономия (паттерны, группы замен, шаги веса). Тексты free-exercise-db можно переводить и менять без обязательств.
- **CC BY-SA (wger):** если включить тексты или изображения wger в свою базу, производная база (по крайней мере эти записи) должна распространяться под CC BY-SA с атрибуцией авторов. Для закрытого коммерческого каталога это неудобно, но допустимо, если держать wger-записи отдельно и показывать атрибуцию в карточке. Код wger (AGPL) лучше не встраивать в бэкенд.
- **MuscleWiki** юридически несовместим с моделью «всё на своём сервере в РФ»: каждая показанная видеозапись идёт с их серверов, а санкции и платежи из РФ создают риск отключения. Кроме того, это зависимость от сервиса под юрисдикцией Каймановых островов.
- **ExRx** исторически запрещает переиспользование контента без разрешения (по памяти, проверить не удалось) — исключить из источников данных.
- Fitbod и Hevy не предоставляют публичных баз для лицензирования — подтверждающего источника в этом исследовании нет, это вывод по отсутствию.

### Gaps
- Точное число упражнений в wger и доля переведённых на русский — API wger.de был недоступен из среды (403 / robots). Нужно проверить `GET https://wger.de/api/v2/exerciseinfo/?language=<ru_id>` и поле `license` у каждой записи и изображения.
- Лицензия изображений free-exercise-db отдельно не указана; происхождение фото не названо — перед коммерческим использованием стоит проверить issues репозитория.
- Тексты ExerciseDB Terms of Use, текущие цены AscendAPI и разрешено ли self-hosting GIF после покупки на Gumroad.
- Условия ExRx, Liftosaur, OpenLift и FitNotes — страницы не загрузились.
- Свежесть коммитов free-exercise-db и wger в 2026 году не подтверждена.

## Вопрос 2. Медиа для техники: варианты, стоимость, риски YouTube

### Takeaway
Дешевле всего выкупить готовую анимацию (Gym visual ~$0.9 за GIF, ExerciseDB $300 за 1 500 GIF, WorkoutLabs от $1 200/год за всю библиотеку) и хранить её у себя. Собственная съёмка даёт полный контроль и отсутствие зависимости. YouTube-встраивание в США в 2026 году признано покрытым лицензией YouTube (Richardson v. Townsquare, 2-й округ), но оно зависит от доступности YouTube в РФ и от того, не удалит ли автор ролик.

### Cited Findings
- Gym visual: иллюстрации дешевле $0.75/шт после 10 в корзине, анимированный GIF $0.9/шт после 10, видео $6/шт после 5; паки — по запросу; новый контент еженедельно; лицензионный текст на главной не раскрыт — [Gym visual](https://www.gymvisual.com/)
- WorkoutLabs: одна иллюстрация от $15/год или $25 бессрочно; вся библиотека (679 упражнений) от $1 200/год или $3 500+ бессрочно; API от $195 setup + $50/мес на время разработки; форматы PNG/SVG, анимация MP4/GIF/SVG; метаданные (мышцы, оборудование, инструкции) — платное дополнение; иллюстрации зарегистрированы в US Copyright Office — [WorkoutLabs licensing](https://workoutlabs.com/exercise-illustrations-licensing/)
- ExerciseDB Gumroad: $300 разово, 1 500+ GIF, разрешение по плану до 1080p, «commercial rights» — [Gumroad](https://exercisedb.gumroad.com/l/exercisedb)
- Hyperhuman: лицензирует клипы отдельных упражнений и классы (в том числе LES MILLS); прямой доступ к Stock Catalog API только на Ultra annual или Enterprise; цены не опубликованы; территория и каналы задаются в каждой лицензии — [Hyperhuman](https://hyperhuman.cc/fitness-content-licensing)
- MuscleWiki: видео только стримингом с их URL, брендинг MuscleWiki нельзя скрывать, встраивать их видео на внешние платформы запрещено — [MuscleWiki API Terms](https://api.musclewiki.com/api-terms)
- YouTube-встраивание: в деле Richardson v. Townsquare Media (S.D.N.Y.) суд признал, что ToS YouTube «explicitly and unambiguously» дают сублицензию на встраивание. По комментарию к статье, 23.04.2026 Второй округ (No. 25-291-cv) подтвердил отказ по иску о встраивании, но возобновил иски о полной перепубликации и скриншотах. Для Twitter/X (Lynk Media v. Mediaite) иск продолжен из-за неоднозначных условий; Instagram заявлял, что сублицензии на встраивание не даёт — [Copyright Lately](https://copyrightlately.com/sdny-social-media-embedding/)
- Muscle & Motion: страница с условиями лицензирования для приложений не найдена (в выдаче только статьи) — [Muscle & Motion](https://www.muscleandmotion.com/?p=16129)

### Inferences
- Для MVP: статичные фото free-exercise-db (Unlicense) или 2 кадра (старт/финиш) → затем купить GIF/MP4 у Gym visual для ~150–300 упражнений (~$135–270 по опубликованным ставкам; оценка) или пакет ExerciseDB за $300 после проверки ToS на self-hosting. Хранить в своём S3-совместимом хранилище в РФ, конвертировать в WebM/MP4 (меньше GIF) и отдавать с lazy-load.
- Собственная съёмка (оценка, без источника): 1 спортсмен + 1 оператор, 2 ракурса, 150 упражнений — несколько съёмочных дней; бюджет сильно зависит от региона. Это единственный вариант без лицензионных ограничений и с русской озвучкой и подписями.
- YouTube: решения американских судов не применяются напрямую к РФ; к тому же YouTube в РФ замедлен, поэтому для русской аудитории это ненадёжный UX-канал (вывод; источник о замедлении в этом исследовании не собирался). Embed — только как временный fallback, и только официальным плеером.
- Стилевая однородность важна: смешение источников (фото wger, GIF Gym visual, видео) ухудшает UX. Лучше одна лицензированная серия.

### Gaps
- Текст лицензии Gym visual (допускается ли использование в приложениях и self-hosting, бессрочно ли).
- Цены 3D-библиотек (Muscle & Motion, Visual Body, Lottie-паки) — данных не найдено.
- Реальная стоимость собственной видеосъёмки в РФ — источник не искался.

## Вопрос 3. Таксономия и подсчёт объёма (прямые и дробные подходы)

### Takeaway
Лучше всего поддержана дробная модель: подход засчитывается как 1 для целевой (primary) мышцы и как 0.5 для вспомогательных (secondary). В мета-регрессии Pelland et al. (2024) у неё были самые сильные относительные доказательства. Boostcamp использует процентные веса для каждой мышцы. Схема должна хранить вес вклада по каждой мышце (0–1), а не только список primary/secondary.

### Cited Findings
- Pelland, Remmert, Robinson, Hinson, Zourdos — «The Resistance Training Dose-Response: Meta-Regressions Exploring the Effects of Weekly Volume and Frequency on Muscle Hypertrophy and Strength Gain», SportRxiv preprint v2 (04.10.2024): 67 исследований, 2 058 участников; косвенные подходы взвешивались как 1 («total»), 0.5 («fractional») или 0 («direct»); у fractional — самые сильные относительные доказательства, поэтому именно он использован в основных моделях. Объём повышает и гипертрофию, и силу с убывающей отдачей (для силы плато выражено сильнее). Частота: для гипертрофии эффект совместим с пренебрежимым, для силы вероятность положительного эффекта 100% с убывающей отдачей — [SportRxiv preprint 460](https://sportrxiv.org/index.php/server/preprint/view/460)
- Boostcamp: не делит мышцы на primary/secondary, а задаёт каждому упражнению процент вклада по мышцам; пример — жим лёжа = 1 подход груди + 0.5 трицепса; разминочные и пропущенные подходы не считаются — [Boostcamp muscle tracker](https://www.boostcamp.app/features/muscle-tracker)
- Hevy: строит график подходов на мышечную группу в неделю или месяц; для кастомных упражнений нужно указать primary и secondary мышцы, чтобы они попали в графики; метод подсчёта (дробный или нет) на странице не раскрыт — [Hevy feature page](https://www.hevyapp.com/features/sets-per-muscle-group-per-week/)
- В статье блога Hevy правило «1 подход для primary, 0.5 для каждой secondary» — эвристика автора, а не описание работы приложения; автор признаёт, что она неточна — [Hevy blog: how many sets](https://www.hevyapp.com/how-many-sets/)
- Тегирование в разных базах:
  - free-exercise-db: force push/pull/static, mechanic compound/isolation, level, 17 упрощённых мышц, 12 типов оборудования — [schema.json](https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/schema.json)
  - API Ninjas: 16 мышечных групп, type и difficulty — [API Ninjas](https://www.api-ninjas.com/api/exercises)
  - ExerciseDB V2: bodyParts, targetMuscles, secondaryMuscles, equipments, exerciseType, variations, relatedExerciseIds — [exercisedb-api](https://github.com/exercisedb/exercisedb-api)
  - MuscleWiki: primary, secondary и tertiary мышцы (на плане Professional) — [MuscleWiki pricing](https://api.musclewiki.com/pricing.md)
  - Ни одна из этих открытых схем не содержит поля «паттерн движения» (squat/hinge/…) или шага загрузки.

### Inferences
- **Рекомендуемая таксономия (вывод):**
  - `movement_pattern` (одно значение): squat, hinge, lunge (single-leg knee-dominant), horizontal_push, vertical_push, horizontal_pull, vertical_pull, carry, rotation / anti_rotation (core), plus изоляция: elbow_flexion, elbow_extension, knee_extension, knee_flexion, hip_abduction, hip_adduction, calf_raise, shoulder_abduction (lateral raise), core_flexion. Паттерн — это главный ключ для замен.
  - `muscles`: два уровня — 1) анатомические мышцы (около 25–30: например, pectoralis major sternal/clavicular, anterior/lateral/posterior deltoid, latissimus, trapezius upper/mid, rhomboids, biceps, brachialis, triceps long/lateral, quads, hamstrings, glute max/med, adductors, calves gastrocnemius/soleus, erectors, rectus abdominis, obliques, forearms); 2) UI-группы (около 12–14: грудь, спина-ширина, спина-толщина, передняя/средняя/задняя дельта, бицепс, трицепс, квадрицепс, бицепс бедра, ягодицы, икры, пресс, поясница). Объём считается по UI-группам через маппинг.
  - `exercise_muscle.weight` ∈ {1.0, 0.5, 0.25}: в UI показывается «целевая / вспомогательная», а в расчёте объёма используется вес (совместимо с моделью Pelland и с подходом Boostcamp).
  - `equipment` (массив, обязательное всё): barbell, ez_bar, dumbbell, kettlebell, cable, machine_selectorized, machine_plate_loaded, smith, bodyweight, pullup_bar, dip_bars, bench_flat, bench_incline, band, trx. Это нужно для фильтра «что есть дома или в зале» и для округления.
  - `level` (beginner/intermediate/advanced), `mechanic` (compound/isolation), `force` (push/pull/static), `laterality` (bilateral / unilateral / alternating), `plane`/`grip` — опционально.
- **Подсчёт объёма (рекомендация):** «эффективный подход» = рабочий подход (без разминки) с RIR ≤ ~4 (порог RIR — оценка, источник в этом исследовании не собирался) × вес мышцы. Показывать пользователю как «прямые + дробные»; для метрики недельной нагрузки использовать дробную сумму.

### Gaps
- Как именно считают Alpha Progression и RP Hypertrophy App (прямые или дробные подходы) — официальные справочные страницы не найдены.
- Был ли препринт Pelland et al. опубликован в журнале к 2026 году — на странице SportRxiv статус не указан.
- Нет найденного стандарта (онтологии) паттернов движения среди открытых баз — таксономия выше сформирована самостоятельно.

## Вопрос 4. Какие поля нужны схеме (зрелые датасеты + требования движка) и русская локализация

### Takeaway
Открытые схемы покрывают только описательные поля (название, мышцы, оборудование, уровень, инструкции). Движку дополнительно нужны: паттерн, группа замены с рангом, шаг загрузки и тип нагрузки, флаг пригодности для e1RM, диапазон повторений по умолчанию, флаги противопоказаний. Готового качественного открытого русского датасета нет; ближайшие варианты — частичные переводы wger (CC BY-SA) и инструкции в exercises-dataset (с медиа под © Gym visual).

### Cited Findings
- Описательные поля зрелых датасетов: free-exercise-db (id, name, force, level, mechanic, equipment, primaryMuscles, secondaryMuscles, instructions, category, images) — [free-exercise-db](https://github.com/yuhonas/free-exercise-db); ExerciseDB V2 (overview, exerciseTips, variations, relatedExerciseIds, videoUrl, keywords) — [exercisedb-api](https://github.com/exercisedb/exercisedb-api); API Ninjas (safety_info) — [API Ninjas](https://www.api-ninjas.com/api/exercises)
- Русский: exercises-dataset заявляет инструкции на русском в списке из 10 языков (противоречит «6 languages» в About) — [hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset); MuscleWiki даёт 14 языков на плане Growth+ (наличие русского не проверено) — [MuscleWiki pricing](https://api.musclewiki.com/pricing.md); UI wger переведён на русский на 78%, переводы упражнений ведутся отдельно, в базе — [Weblate](https://hosted.weblate.org/projects/wger/)
- Workout.cool хранит двуязычные поля (name / name_en) — пример модели локализации в одной строке — [workout-cool](https://github.com/Snouzy/workout-cool)

### Inferences
- **Рекомендуемая схема (PostgreSQL; вывод):**
  - `exercise`: id (uuid), slug, `name_ru`, `name_en`, `aliases_ru[]` (для поиска: «становая», «румынка»), `movement_pattern`, `mechanic`, `force`, `laterality`, `level`, `category` (strength / mobility / cardio), `is_active`, `source` (free-exercise-db / wger / own), `source_id`, `license` (Unlicense / CC-BY-SA-4.0 / proprietary), `attribution` (text), `created_at`, `updated_at`.
  - `exercise_muscle`: exercise_id, muscle_id, `role` (primary / secondary / stabilizer), `volume_weight` (1.0 / 0.5 / 0.25 / 0).
  - `muscle`: id, name_ru, name_en, `ui_group_id`; `muscle_group_ui`: id, name_ru, sort.
  - `exercise_equipment`: exercise_id, equipment_id, `required` (bool); `equipment`: id, name_ru, `load_type`.
  - **Поля для движка:**
    - `load_type`: barbell_plates / dumbbell_fixed / dumbbell_adjustable / kettlebell / machine_stack / plate_loaded / bodyweight / bodyweight_plus / band / assisted.
    - `load_increment_kg` (по умолчанию: штанга 2.5, гантели 2, тренажёр 5; переопределяется инвентарём пользователя — `user_equipment.available_weights[]`).
    - `load_multiplier`: 2 для пар гантелей (если вес записывается на одну руку) и учёт веса грифа (`bar_weight_kg`).
    - `bodyweight_fraction`: доля веса тела для подтягиваний, отжиманий, отжиманий на брусьях (оценки нужно брать из литературы, источник не собирался).
    - `trackable_for_e1rm` (bool: только многосуставные упражнения со стабильной техникой и диапазоном 1–10 повторений; не для изоляции на тренажёре, планок и упражнений с резиной).
    - `default_rep_range` (min/max), `default_rest_s`, `progression_scheme` (double_progression / linear / rpe).
    - `substitution_group_id` + `substitution_rank` / `similarity` (одинаковый паттерн и primary-мышцы; ранжирование по оборудованию и уровню); `progression_of` / `regression_of` (ссылки для лестниц сложности: отжимания от стены → от скамьи → от пола).
    - `contraindication_flags[]`: axial_spinal_load, overhead_shoulder_flexion, deep_knee_flexion, high_impact, valsalva_heavy, wrist_extension_load, lumbar_flexion_loaded — используются как фильтр при пользовательских ограничениях («болит плечо»). Это не медицинские диагнозы, а теги нагрузки.
    - `technique_cues_ru[]`, `common_mistakes_ru[]`, `media` (таблица: type image/gif/mp4/webm, url, width, height, poster, `license`, `attribution`, `source`).
  - `exercise_translation` (exercise_id, lang, name, description, cues) — если в будущем понадобятся другие языки; на старте достаточно колонок `_ru` / `_en`.
- **Русская локализация (вывод):** машинный перевод free-exercise-db (Unlicense) + обязательная редактура тренером. Названия должны соответствовать устоявшемуся русскому жаргону зала («жим лёжа», «тяга в наклоне», «румынская тяга», «гакк-присед»), а ключевые 150–300 упражнений лучше вычитать вручную. Переводы wger, если использовать, требуют атрибуции и CC BY-SA. Качество переводов упражнений wger на русский не проверено (оценка: неполное и неравномерное, так как переводы делают волонтёры).
- **152-ФЗ:** справочник упражнений не содержит персональных данных, поэтому его источник на локализацию не влияет. Важно, чтобы медиа и данные хранились у себя, а не запрашивались в рантайме из-за рубежа (MuscleWiki этого не позволяет) — это вопрос доступности, а не 152-ФЗ.

### Gaps
- Не найден открытый русскоязычный датасет упражнений приемлемого качества с понятной лицензией (поиск на русском дал нерелевантную выдачу).
- Количество и качество русских переводов упражнений в wger — не проверено из-за блокировки API.
- Значения `bodyweight_fraction` (доля веса тела в отжиманиях, подтягиваниях) — источники не собирались.
