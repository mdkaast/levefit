# Nutrition, calorie/macro tracking and meal-planning apps (state as of Oct 2026)

Scope note: research done 2026-10-25. Most prices come from third-party comparison blogs. Many of those are run by competing apps (Nutrola, NutriScan, PlateLens-affiliated sites), so treat prices as "reported" and check them in the app stores. Official pages fetched directly are marked (official). Several PubMed/PMC pages were blocked by reCAPTCHA. For those, abstract-level facts come from secondary summaries and are marked as such.

## 1. What makes adaptive nutrition coaching trustworthy (MacroFactor) and how is it explained to the user?

### Takeaway
MacroFactor's trust model has four parts. (1) It only infers expenditure from data the user already gives (weight trend + logged intake). (2) It is "adherence-neutral": no punishment and no "catch-up" for missed targets. (3) It publishes the mechanics and the known failure modes in long-form articles. (4) It gives a weekly check-in where every change is proposed and the user approves it. The specific maths is not disclosed, and the accuracy claims are internal (mostly the founder's own data), not independently validated. The same pattern maps directly onto a rule-based training coach that "explains its decisions".

### Cited Findings
**Algorithm mechanics (official)**
- Initial estimate from a custom BMR equation + activity factor. It is expected to converge in ~14–30 days. A smoothed weight trend separates real energy-store change from water/glycogen/sodium noise. Recent data counts more, but older data still counts. The calorie change implied by the trend + intake gives actual expenditure, and the goal rate becomes a surplus/deficit on top of it. — [MacroFactor: Algorithms and Core Philosophy](https://macrofactor.com/macrofactors-algorithms-and-core-philosophy/)
- "Adherence-neutral": over/under-eating doesn't degrade the adjustment. Each week is self-contained, with no subtraction to "make up" for overeating. When the user stops logging, the app carries forward the last high-confidence expenditure. — [same](https://macrofactor.com/macrofactors-algorithms-and-core-philosophy/)
- Anti-shame design: neutral numbers, no red warnings or pop-ups when targets are exceeded. MacroFactor argues that kinder UX produces more honest logging and therefore better recommendations. — [same](https://macrofactor.com/macrofactors-algorithms-and-core-philosophy/)
- The article openly lists limitations: creatine, carb/fiber shifts, and temporary activity spikes confuse the trend. It advises skipping a check-in or two after an anomalous event. — [same](https://macrofactor.com/macrofactors-algorithms-and-core-philosophy/)
- Coaching styles: "Coached" (default; protein set by training type plus the user's chosen point in the recommended range; carbs/fat by preference). At very low calories it protects fat first, then protein, then carbs. "Collaborative": the algorithm sets calories, the user sets macros. The UI doesn't steer users toward weight loss. — [same](https://macrofactor.com/macrofactors-algorithms-and-core-philosophy/)
- Weekly check-in: after a week of weight + nutrition data the app proposes new targets. "Coaching Modules" each address one specific issue, answer a likely question, or propose changes to data/program **only with user approval**. Check-ins can be dismissed and resumed later. — [Help: how adjustments are made (official)](https://help.macrofactorapp.com/en/articles/222-how-does-macrofactor-make-adjustments-for-a-weight-gain-or-weight-loss-goal)
- Goal rate is set as **% of bodyweight per week** (0.5%/wk = 1 lb at 200 lb, ~0.9 lb at 180 lb). Smoothing means only sustained 3–4-week trends drive big changes. There is a fat floor for "normal physiological function", and protein scales with estimated lean mass. No explicit calorie floor is stated. — [same](https://help.macrofactorapp.com/en/articles/222-how-does-macrofactor-make-adjustments-for-a-weight-gain-or-weight-loss-goal)
- Minimum data: nutrition logged ≥4/7 days (7 ideal), weight ≥1/7 days (≥3 ideal). — [same](https://help.macrofactorapp.com/en/articles/222-how-does-macrofactor-make-adjustments-for-a-weight-gain-or-weight-loss-goal); [Help: weigh-in frequency](https://help.macrofactorapp.com/en/articles/109-how-frequently-do-i-need-to-log-my-weight-for-the-expenditure-algorithm-and-weekly-coaching-updates)

**V3 algorithm (Greg Nuckols, 8 Oct 2024, official)**
- Inputs are only bodyweight + intake. Training/activity are treated as causes of expenditure change, not as inputs. — [Expenditure V3](https://macrofactor.com/expenditure-v3/)
- Changes: better handling of fluid noise (salty/carb meals, creatine, menstrual cycle). Gain and loss are now symmetric, which removes a 0–130 kcal/day upward bias for bulking. — [same](https://macrofactor.com/expenditure-v3/)
- Missing data: V2 paused with ≥2 missing days/week, V3 pauses only with >3 missing days in 7. It imputes intake on unlogged days with ~13% mean error (>90% of errors <30%). Deleting 50% of the founder's nutrition data at random left estimates close to the full-data results. — [same](https://macrofactor.com/expenditure-v3/)
- Claimed gains vs V2: day-to-day swings ~35% smaller, trend reversals detected 1–5 days sooner, ~10% better overall accuracy, weekly weight-change prediction error ~15% smaller. — [same](https://macrofactor.com/expenditure-v3/)
- **Caveat (fact about the evidence):** validation is internal, largely on the author's own multi-year data plus simulations. There is no independent validation, and the "secret sauce" specifics are withheld. — [same](https://macrofactor.com/expenditure-v3/)

**Other adaptive coaches**
- Carbon Diet Coach (Layne Norton): initial assessment, daily logging, weekly check-in with weight + progress photos. Macros adjust on actual vs expected progress, with phases for cut, maintenance, reverse diet and bulk, plus diet break / refeed suggestions. Reported price $9.99/mo or $79.99/yr, no free tier (trial only). Reported limitations: no barcode scanner, no AI logging, only 4 nutrients. Source is a competitor blog. — [Nutrola blog (competitor)](https://nutrola.app/en/blog/how-much-does-carbon-diet-coach-cost-now-2026); a different competitor quotes $14.99/mo — [Nutrola](https://nutrola.app/en/blog/why-is-carbon-diet-coach-so-expensive). **Conflict in reported price.**

### Inferences
- The trust model transfers to the training coach. Each one combines a model that is published even if the parameters aren't, an explicit list of the cases where it is wrong, a weekly cadence, changes the user approves, and no penalty for non-adherence.
- MacroFactor needs only two inputs (daily weight + intake). Since the training diary already has a bodyweight field, the TDEE-from-trend part can be built **without** a food diary only if intake is also approximately known. Without intake you can only steer by trend ("weight trend −0.3%/wk vs target −0.5% → eat ~X less"). That is how a "lite" module can work.
- A %-of-bodyweight goal rate plus a 3–4-week smoothing window are cheap, defensible defaults.

### Gaps
- MacroFactor's exact formulas and any peer-reviewed or independent validation: none found. The company says it withholds specifics.
- MacroFactor's public metrics (users, revenue): not found in this pass.
- RP Diet app: no reliable current price or feature source found.

## 2. How accurate is photo-based calorie estimation according to independent studies?

### Takeaway
Independent evidence from 2024–2026 is consistent. Photo AI **identifies** foods fairly well but **estimates energy poorly**. It systematically underestimates calories, by a mean of roughly 250–345 kcal/meal in an NIH test of four popular apps. Fat is underestimated most. Mixed or culturally diverse dishes and large portions are worst. General LLMs show ~35–40% error on weight and energy. Photo AI is fine as a "quick rough log + user edits" UX. It is not accurate enough to steer a cut or bulk by itself. The adaptive weight-trend correction (MacroFactor-style) partly compensates, because a systematic bias gets absorbed into the expenditure estimate.

### Cited Findings
- **NIH / NIDDK (Hengist & Charles), NUTRITION 2026 conference abstract, 25 Jul 2026, not yet peer-reviewed:** 102 standardized meals weighed to 0.1 g in a metabolic kitchen, photographed and run through MyFitnessPal, Lose It!, Cal AI and Appediet. All four **underestimated energy by ~250–345 kcal on average** and fat by ~30 g. Carbs were the most consistent macro. MFP and Lose It! did better on higher-calorie meals. A follow-up on more than 200 meals suggests ketogenic (high-fat) meals are worse. Only pooled figures were published, with no per-app breakdown. — [Newswise release](https://www.newswise.com/articles/photo-based-calorie-tracking-apps-may-underestimate-energy-in-meals); [HealthDay](https://www.healthday.com/health-news/nutrition/how-accurate-are-photo-based-calorie-apps-4-are-put-to-the-test)
- **Li et al. 2024, *Nutrients* 16(15):2573 (peer-reviewed):** tested 7 AI image apps on 22 images, 39 components and 7 mixed dishes.
  - Identification: MyFitnessPal 97%, Fastic 92%, HealthifyMe 90%, Foodvisor ~87%, Lose It! and FatSecret 46%.
  - Energy for single-component foods vs reference: MFP −3%, HealthifyMe +8%, Fastic +44%, Foodvisor −47%.
  - Mixed dishes: energy underestimated by up to 76%. The authors call energy estimation for mixed and culturally diverse dishes "poor".
  - Manual logging in 16 apps also showed large errors: Western diet +1040 kJ mean, Asian diet −1520 kJ, recommended diet −944 kJ.
  - — [MDPI Nutrients](https://www.mdpi.com/2072-6643/16/15/2573)
- **Fridolfsson et al. 2025 (peer-reviewed, title "Performance Evaluation of 3 Large Language Models for Nutritional Content Estimation from Food Images"):** ChatGPT-4o, Claude 3.5 Sonnet and Gemini 1.5 Pro on 52 foods. ChatGPT and Claude had ~36–40% error on weight/energy, Gemini ~65–70%. Macro errors were 42–110%, and protein error was >60% for all models. Errors grew with portion size, all models underestimated, and some foods were misidentified (falafel as meatballs, eggs as pasta). — PMC full text blocked by captcha; facts from secondary summaries: [Biolayne REPS review](https://biolayne.com/reps/issue-44/can-we-use-ai-to-accurately-track-calories-with-a-picture/), [Т—Ж, 9 Feb 2026](https://t-j.ru/ai-calorie-tracker/), PMC link: [PMC12513282](https://pmc.ncbi.nlm.nih.gov/articles/PMC12513282)
- **Manufacturer positioning:** MFP's CEO describes Cal AI as built for "speed over accuracy". MFP's own meal-scan instead lets users adjust inputs in detail. — [TechCrunch, 2 Mar 2026](https://techcrunch.com/2026/03/02/myfitnesspal-has-acquired-cal-ai-the-viral-calorie-app-built-by-teens)
- **MacroFactor AI logging (beta, Apr 2025):**
  - How it works: LLM prompts split the photo/text into ingredients, then each one is matched to MacroFactor database entries (lab-analyzed entries preferred) rather than LLM-generated nutrition. Every item is editable before logging, and recipes can be "exploded" into components.
  - Caveats MacroFactor itself states: it misses hidden ingredients (sauce under a bun) and under-estimated a rice portion in an example.
  - Photo tips: top-down, even light, a fist or scale for reference.
  - — [MacroFactor AI food logging](https://macrofactor.com/ai-food-logging/)
- **Suspect source, do not cite as evidence:** "Dietary Assessment Initiative" six-app 180-meal study (2026) reports PlateLens photo MAPE 1.1%, MacroFactor 4.8%, Foodvisor 5.1%, Cronometer 6.8%, Lose It! 9.4% and MFP 11.2%.
  - It is self-published, not peer-reviewed, uses its own registry, and has inconsistent author lists and an odd DOI format.
  - Its numbers are recycled by PlateLens-favouring blogs, e.g. [learnmuscles.com](https://learnmuscles.com/blog/2026/10/15/best-macro-tracker-apps-2026-tested-and-ranked/).
  - Its 1.1% photo error contradicts every peer-reviewed study above.
  - — [DAI page](https://dietaryassessmentinitiative.org/publications/six-app-validation-study-2026/)
- SnapCalorie markets depth-sensor (LiDAR) portion estimation. No independent validation was found. — [TechCrunch (funding)](https://techcrunch.com/?p=2561037)

### Inferences
- Photo-by-mass estimation (the original idea) has a structural error floor. Oil, sauces and hidden fat aren't visible, and the bias is downward. Sensible use: the photo pre-fills a plate of editable ingredients matched to a real database (the MacroFactor pattern), never a single opaque kcal number.
- Systematic underestimation by itself is partly harmless under an adaptive TDEE (the bias gets absorbed). But it makes any "you ate X kcal" absolute claim misleading, which matters for an "explained decisions" brand.
- An LLM-vision API (GPT/Claude/Gemini) plus a DB lookup is roughly what consumer apps do now. You can build it, but you should not claim accuracy.

### Gaps
- No peer-reviewed per-app accuracy numbers for Cal AI, SnapCalorie or Foodvisor specifically, beyond Li 2024 (Foodvisor −47% single-component).
- The J Acad Nutr Diet 2024 paper "Evaluating the Accuracy of Image-based Dietary Assessment Mobile Apps" could not be fetched: [JAND](https://www.jandonline.org/article/S2212-2672(24)00610-5/fulltext).
- No study on Russian-cuisine photo accuracy was found. Li 2024 suggests non-Western dishes do worse.

## 3. Minimal viable nutrition module for a strength goal vs full food diary — competitors, costs, databases

### Takeaway
For a strength-training audience, the evidence and competitors point to a "lite" module: a protein target (~1.6 g/kg/day is the meta-analytic plateau for lean-mass gains), a daily bodyweight trend with a goal rate in %BW/week, and a weekly check-in that adjusts a calorie guideline. A full diary is expensive. It needs a food DB, barcode, Russian product coverage, and moderation of user entries. Even big apps get criticised for DB errors and paywalls. Russian product coverage in open DBs is thin: about 28k products in Open Food Facts. The best RU DBs belong to local apps (FatSecret RU with user-built ~1.9M items, МЗР using Skurihin tables ~150k).

### Cited Findings
**Evidence base for a lite module**
- Morton et al. 2018, *Br J Sports Med*: protein supplementation beyond a total intake of **1.62 g/kg/day** gave no further resistance-training-induced fat-free-mass gains (rounded to ~1.6). — [summary page](https://www.egginfo.co.uk/research/systematic-review-meta-analysis-and-meta-regression-effect-protein-supplementation)
- Self-weighing as a weight-management tool, systematic review and meta-analysis (Zheng? / Madigan et al. 2015): details not fetched. — [PMC4546162](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4546162/), [PubMed 26293454](https://pubmed.ncbi.nlm.nih.gov/26293454/) (only the title was confirmed, so the effect size is a gap)
- MacroFactor's own engine needs only weight + intake, and treats training as a cause, not an input. — [V3](https://macrofactor.com/expenditure-v3/)

**Product snapshot (prices reported Oct 2026 unless noted; mostly from third-party blogs)**
| App | Price (reported) | Logging / AI | DB | Notes |
|---|---|---|---|---|
| MacroFactor | no free tier; 7-day trial; $11.99/mo, $47.99/6 mo, $71.99/yr | search, barcode, label scan, photo/voice AI, recipe import; weekly check-in | curated / lab-analyzed priority | no web app — [learnmuscles (PlateLens-biased)](https://learnmuscles.com/blog/2026/10/15/best-macro-tracker-apps-2026-tested-and-ranked/) |
| MyFitnessPal | free; Premium $19.99/mo or $79.99/yr; Premium+ $99.99/yr | barcode (paywalled since 2022), Meal Scan, voice; AI Nutrition Coach (2026) | ~20M foods, 68.5k brands, 380+ restaurant chains, incl. user entries | acquired Cal AI (closed Dec 2025, announced Mar 2026) — [learnmuscles](https://learnmuscles.com/blog/2026/10/15/best-macro-tracker-apps-2026-tested-and-ranked/); [TechCrunch](https://techcrunch.com/2026/03/02/myfitnesspal-has-acquired-cal-ai-the-viral-calorie-app-built-by-teens); [Pocket-lint barcode paywall](https://www.pocket-lint.com/apps/news/162386-wow-myfitnesspal-put-its-popular-barcode-scanner-feature-behind-a-paywall) |
| Cronometer | Basic free (barcode free); Gold $10.99/mo or $59.99/yr | photo/voice, AI coach, macro scheduler in Gold | 1.1M+ entries from NCCDB + USDA (verified) | DB quality praised; dated UI / learning curve — [learnmuscles](https://learnmuscles.com/blog/2026/10/15/best-macro-tracker-apps-2026-tested-and-ranked/); [Unstar](https://unstar.app/blog/calorie-tracking-apps-ranked-1-star-reviews-2026) |
| Lose It! | free with ads; Premium $79.99/yr; lifetime $299.99 | Snap It photo, Say It voice in Premium; barcode moving to Premium | 50M+ items | [learnmuscles](https://learnmuscles.com/blog/2026/10/15/best-macro-tracker-apps-2026-tested-and-ranked/) |
| Cal AI | (price not verified) | photo-first, "speed over accuracy" | now connected to MFP DB | 15M+ downloads, >$30M annual revenue in under 2 years (per MFP); stays a separate app — [TechCrunch](https://techcrunch.com/2026/03/02/myfitnesspal-has-acquired-cal-ai-the-viral-calorie-app-built-by-teens) |
| Carbon | $9.99/mo or $79.99/yr (conflicting $14.99/mo) | weekly check-in coach; no barcode/AI | — | [Nutrola](https://nutrola.app/en/blog/how-much-does-carbon-diet-coach-cost-now-2026) |
| Yazio | $9.99/mo or $44.99/yr; RU: 999₽/3 mo, 1,990₽/yr | AI camera in PRO | medium RU coverage | complaints about auto-renewal and fasting upsell — [Nutrola](https://nutrola.app/en/blog/how-much-does-carbon-diet-coach-cost-now-2026); [Zozhnik](https://zozhnik.ru/prilozhenie-dlya-podscheta-kalorij); [Unstar](https://unstar.app/blog/calorie-tracking-apps-ranked-1-star-reviews-2026) |
| Lifesum | RU: 749₽/mo, 2,390₽/yr | photo in PRO | limited RU coverage | payment problems from Russia; recipes gated — [Zozhnik](https://zozhnik.ru/prilozhenie-dlya-podscheta-kalorij); [Unstar](https://unstar.app/blog/calorie-tracking-apps-ranked-1-star-reviews-2026) |
| Noom | (price page not fetched) | psychology-based coaching | — | complaints: shame-based coaching, cancellation friction ("11 steps") — [Unstar](https://unstar.app/blog/calorie-tracking-apps-ranked-1-star-reviews-2026) |

**Russian-language market (as of Sep 2026)**
- FatSecret: 925₽/mo or 3,990₽/yr. User-built DB with ~1.9M items, photo in Premium. **Paying from Russia is a problem**: Russian cards don't work. — [Zozhnik, 5 Sep 2026 (owns a competing app, Зоя)](https://zozhnik.ru/prilozhenie-dlya-podscheta-kalorij); [RBC Trends](https://trends.rbc.ru/trends/social/6932918d9a79476440af9432)
- «Мой здоровый рацион» (МЗР): 449₽/3 mo, 899₽/yr. Skurihin tables (~150k), on RuStore, pays OK from Russia. — [Zozhnik](https://zozhnik.ru/prilozhenie-dlya-podscheta-kalorij)
- «Таблица калорийности и калории»: 589₽/mo, 2,590₽/yr. RBC calls it the best fit for Russian products. — [RBC Trends](https://trends.rbc.ru/trends/social/6932918d9a79476440af9432)
- Others: Arise (iOS, photo AI free, weak RU barcodes), Худеем вместе (free, AI photo), Зоя (390₽/mo; Skurihin + USDA in Russian + OFF), plus many small "ИИ счётчик калорий" apps on RuStore/App Store (FoodWarz, 1cal…). — [Zozhnik](https://zozhnik.ru/prilozhenie-dlya-podscheta-kalorij); [RuStore FoodWarz](https://www.rustore.ru/catalog/app/com.foodwarz.mobile)
- **Yandex / Sber:** no consumer calorie-tracking product from Yandex or Sber appears in the RU comparisons by Zozhnik and RBC. — [Zozhnik](https://zozhnik.ru/prilozhenie-dlya-podscheta-kalorij); [RBC](https://trends.rbc.ru/trends/social/6932918d9a79476440af9432)

**Food database APIs for a small team**
| API | Price / terms | Size / coverage | RU |
|---|---|---|---|
| Open Food Facts | free, **ODbL**: attribution + share-alike (a derived/merged DB must also be open); custom User-Agent required; per-endpoint rate limits | 2.8M+ products, 150+ countries; crowdsourced, variable quality | **Russia 28,463 products**, Belarus 1,052, Ukraine 5,152 (fetched Oct 2026) — [OFF conditions](https://support.openfoodfacts.org/help/en-gb/12-api-data-reuse/94-are-there-conditions-to-use-the-api); [OFF countries](https://world.openfoodfacts.org/countries); [Spike](https://spikeapi.com/blog/top-nutrition-apis-for-developers-2026) |
| USDA FoodData Central | free, **CC0 public domain**; data.gov key; 1,000 req/h/IP (DEMO_KEY 30/h); credit requested | ~380k foods; Foundation, SR Legacy, FNDDS, Branded (US) | generic foods only; no RU brands — [FDC API guide (official)](https://fdc.nal.usda.gov/api-guide) |
| FatSecret Platform | Basic: free, 5,000 calls/day, US only, English, attribution. **Premier Free**: unlimited, US dataset, barcode, for start-ups (<$1M revenue and <$1M raised), attribution. Premier: priced on request **by number of markets** (62+ countries, 26 languages), white label. Image recognition / NLP are paid add-ons (50% start-up discount), in tiers of 25k inputs/month | largest claimed global DB | RU not stated on the editions page; must be checked in the localization guide — [FatSecret editions (official)](https://platform.fatsecret.com/api-editions) |
| Edamam Food DB | Basic $14/mo (100k calls/mo, 30-day trial); Core $69/mo (750k); Plus $299/mo (5M); Unlimited custom; Vision from $0.015/call; **attribution mandatory** (breach means suspension) | ~1M foods incl. ~790k UPC | languages not stated — [Edamam (official)](https://developer.edamam.com/food-database-api) |
| Nutritionix | reported $50–500/mo by volume (third-party, unverified) | 800k+ products/menu items, mainly US | US-centric — [RaftLabs](https://www.raftlabs.com/blog/how-to-build-nutrition-tracking-app-like-myfitnesspal); [Spike](https://spikeapi.com/blog/top-nutrition-apis-for-developers-2026) |
| Passio Nutrition AI | token-based: $2.50/M tokens auto-refill, volume $2.35–2.45/M. Image recognition 3k–5k **or** 20–30k tokens per photo (the page contradicts itself); average user ~250k tokens/mo, which is roughly $0.6/user/mo; no free trial | coverage not stated | not stated — [Passio cost breakdown (official)](https://www.passio.ai/cost-breakdown) |

- Development cost benchmark: a nutrition-tracking MVP (logging, barcode, macros, reports) runs $35–65k over 12–14 weeks at $35–40/h. This comes from an agency, so it is indicative only. — [RaftLabs](https://www.raftlabs.com/blog/how-to-build-nutrition-tracking-app-like-myfitnesspal)

**Complaints and UX patterns**
- 1–3-star themes across the category: paywall ~29%, database errors ~18% (US/UK reviews). MFP: barcode paywall and user-entry errors. Cronometer: praised DB, dated UI. — [Unstar, 23 Apr 2026](https://unstar.app/blog/calorie-tracking-apps-ranked-1-star-reviews-2026)
- Manual logging itself is inaccurate across 16 apps (Li 2024: −1520 kJ on an Asian diet). DB quality matters as much as the input method. — [Nutrients](https://www.mdpi.com/2072-6643/16/15/2573)

### Inferences
- MVP for stage 3, in order:
  1. Daily weight plus a trend line, which the training diary may already have.
  2. A protein target (1.6–2.2 g/kg) with a simple tick or quick-add "protein grams".
  3. A weekly check-in: "trend vs goal rate leads to a kcal guideline change", with an explanation and approval.
  4. Optional quick-add of kcal.
  This gets most of MacroFactor's value with no food DB.
- A full diary for RU users needs a Russian DB. OFF (28k RU products, ODbL share-alike) is weak. FatSecret Premier covers multiple markets but is priced per market. Skurihin tables are what local apps use (licensing not researched). Payments for foreign apps are broken in RU, which is an opening for a Telegram-native product (Telegram Stars).
- Photo AI via an LLM vision API plus a DB match is the cheapest "wow" feature, at roughly cents per photo. It must be framed as an estimate.

### Gaps
- Licensing and cost of Skurihin tables, and whether FatSecret Premier includes Russia: not found.
- Official current prices for Noom, Lifesum (USD), Eat This Much, Mealime, RP Diet, SnapCalorie, Foodvisor: not verified this pass.
- Public user metrics: only Cal AI (15M downloads, $30M ARR per MFP) and MFP DB size were found. MacroFactor, Cronometer and Lose It user counts were not found.
- Recipe/meal-plan generation (Eat This Much, Mealime): not researched in depth.
- Effect sizes for self-weighing (Madigan 2015) were not extracted.

## 4. Safety: disordered-eating risks in calorie tracking and mitigations

### Takeaway
The risk is real and documented, though mostly in people who already have an eating disorder. Levinson et al. 2017: 73% of eating-disorder patients who used MyFitnessPal said it at least somewhat contributed to their disorder. Mitigation in the market is mostly design-level: neutral, non-shaming feedback (MacroFactor), user-chosen goals without weight-loss steering, and fat/protein floors. Explicit ED screening, hide-numbers modes and referral flows are rare. Users request them in forums for Cronometer and Yazio. No strong evidence was found that tracking causes ED in the general population.

### Cited Findings
- Levinson, Fewell & Brosof 2017, *Eating Behaviors* 27:14–16. N=105 ED patients. 74.3% had used MyFitnessPal. Of these, **73.1%** said it at least somewhat contributed to their ED, 62.9% at least moderately, and 30.3% very much. Perceived contribution correlated with restraint (r=.25), shape concern (.34) and weight concern (.36). — [PMC5700836](https://pmc.ncbi.nlm.nih.gov/articles/PMC5700836/); [PubMed 28843591](https://pubmed.ncbi.nlm.nih.gov/28843591/)
- MacroFactor's philosophy: no guilt, no red warnings, adherence-neutral, no UI pressure toward weight loss, a fat floor. It does **not** describe ED screening or referral. — [MacroFactor philosophy](https://macrofactor.com/macrofactors-algorithms-and-core-philosophy/)
- Noom is criticised by users for "shame-based coaching". — [Unstar](https://unstar.app/blog/calorie-tracking-apps-ranked-1-star-reviews-2026)
- Users ask for "hide all calorie information" modes, and one Cronometer thread complains an update was bad for ED recovery. — [Cronometer forum](https://forums.cronometer.com/discussion/1350/new-cronometer-update-isnt-great-if-youre-recovering-from-an-eating-disorder); [Cronometer forum: hide calories](https://forums.cronometer.com/discussion/comment/11651); [Yazio feature request](https://yazioen.featureupvote.com/suggestions/349684/tracker-without-calorie-amount)
- Google Maps removed a calorie feature over ED concerns. — [CFJC Today](https://cfjctoday.com/?p=689356)
- Duke Psychiatry commentary on tracking risk. — [Duke "The Trouble with Tracking"](https://psychiatry.duke.edu/blog/trouble-tracking) (not read in full)

### Inferences
- For the Mini App:
  - Make nutrition opt-in.
  - Default to protein and weight-trend views, with calories hidden or optional.
  - Use a %BW/week rate cap (for example ≤1%/wk for loss) and a calorie/fat floor.
  - Use neutral language with no red "over" states.
  - Add a short screening question or "I'd rather not see numbers" mode, plus a referral link (in RU, e.g. a helpline or specialist).
  - Don't offer "catch-up" deficits.
  - Exclude minors.
- The adaptive coach's explanations can themselves reduce anxiety ("weight up 0.8 kg is water after a high-carb day; trend unchanged").

### Gaps
- No peer-reviewed RCT showing that tracking apps cause new EDs in non-clinical users was found in this pass.
- Formal design guidelines (e.g. NEDA or BEAT guidance for apps) were not located.
- A second paper ([PMC8485346](https://pmc.ncbi.nlm.nih.gov/articles/PMC8485346/)) was blocked by captcha, so its content is unknown.
