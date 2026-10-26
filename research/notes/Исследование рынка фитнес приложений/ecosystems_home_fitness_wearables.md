# Home-fitness platforms, fitness ecosystems, and wearable/recovery analytics (state as of 25 Oct 2026)

Scope: Nike Training Club, Apple Fitness+ / Apple Watch, Peloton (App, Strength+, Peloton IQ), Freeletics, Centr, Sweat, Les Mills+, FitOn, Tonal, Tempo, WHOOP, Oura, Garmin Connect / Connect+, Strava, Fitbit / Google Health, Samsung Health, Polar, Zwift, Sweatcoin, plus the HealthKit, Health Connect and wearable-API integration routes for a Telegram Mini App (TMA).
Client context: a TMA strength diary with game mechanics and a rule-based "Adaptive Workout Decision Engine" (the LLM only explains). Long-term goal: a "Personal Fitness OS".
Conventions: "Fact" means stated by a primary or official source. "Claim" means a company statement or vendor marketing. "Est." means a third-party estimate. Each price shows its check date or its source's date.

---

## Q1. How do readiness and recovery scores turn into training recommendations, and do users trust them?

### Takeaway
Every major wearable builds a 0–100 readiness or recovery composite from HRV, resting HR, sleep, recent load (and sometimes temperature or stress). The score is turned into advice through simple, published bands: "high = ready for challenge, low = rest/light activity". Only a few products (Polar Fitness Program, Garmin Fitness Coach / daily suggestions, WHOOP, Peloton IQ) actually change the planned workout. Strength training is a known blind spot: wrist sensors underweight lifting load, and nobody models per-muscle readiness yet (Garmin is only surveying it). Trust is mixed. Reviewers call readiness scores "arbitrary across all brands", and users report counter-intuitive results. That supports the client's approach: transparent rules, the user's own logged sets as the main signal, and wearable readiness as an optional modifier only.

### Cited Findings

#### Readiness score mechanics (official definitions)
- **Garmin Training Readiness** factors: last night's sleep score, recovery time, HRV status, acute load, 3-night sleep history and 3-day stress history. The score updates continuously through the day. Bands: 95–100 Prime, 75–94 High ("ready for challenges"), 50–74 Moderate, 25–49 Low ("time to slow down"), 1–24 Poor — [Garmin manual](https://www8.garmin.com/manuals/webhelp/GUID-31D23DBB-57C2-4DF7-A0C9-8D1A00AB4BE7/EN-US/GUID-C21BE0C8-A08E-4DA1-B6C6-2E0E2DDDB372.html)
- **Oura Readiness** contributors: lowest resting HR and when it occurred, body temperature, sleep, previous-day activity, plus HRV, sleep and activity "balance" (the past 14 days compared with the past 2 months, with the last 2–5 days weighted more). Menstrual cycle and pregnancy are accounted for. Bands: 85–100 Optimal ("may be ready for new challenges"), 70–84 Good, 60–69 Fair, 0–59 Pay Attention. Below 70, Oura advises prioritising rest, and it suggests limiting intense activity without going fully inactive (e.g. a 20-minute walk) — [Oura support](https://support.ouraring.com/hc/en-us/articles/360025589793)
- **Apple Watch Training Load** compares the intensity × duration of the last 7 days with the previous 28. It is shown on a scale from "well below" to "well above", and users can edit each workout's effort rating. Open via Activity app → Workload — [Apple Support](https://support.apple.com/guide/watch/track-your-training-load-apde4c07a6cf/watchos)
- **Samsung Health** (announced 4 Jun 2026, rollout from 8 Jun): an AI-powered Energy Score with daily tips on Home; a "Vitals" feature that compares overnight HR, HRV, respiration, skin temperature and SpO2 against your baseline (it needs 7 of the first 28 nights); and Daily Cardio Load, which recommends training targets and rest times. Samsung says the features are wellness-only — [Samsung Newsroom](https://news.samsung.com/us/samsung-health-app-evolves-with-ai-powered-proactive-intelligence-to-help-users-stay-ahead-of-their-health/)
- **WHOOP Recovery** (recovery score, HRV, RHR), **Strain** (day and activity) and **Sleep** are the core outputs, exposed in the API as separate scopes — [Terra blog on WHOOP API](https://tryterra.co/blog/whoop-api-data-access-permissions-limitations-2026)

#### Products where the score changes the plan (score → action)
- **Polar Fitness Program** (subscription): builds successive 4-week plans across 20 levels and moves the level up or down between periods based on goal completion. It includes cardio, strength and mobility targets, monitors Nightly Recharge and Cardio Load, and "suggests lighter sessions when your body isn't ready" — [Polar support](https://support.polar.com/en/fitness-program). Price not shown on the page. Launch covered by [DC Rainmaker, Apr 2025](https://dcrainmaker.com/2025/04/polar-launches-premium-subscription-service-says-hold-my-beer.html).
- **Garmin**: Fitness Coach adaptive plans combine cardio and strength and adjust using Body Battery and HRV. Strength Coach plans have accumulation, intensification and deload phases (Fenix 8, FR970, newer Venu and Vivoactive). Strength PRs per exercise were added in Q1 2026. Post-session muscle map. Automatic rep counting is "unreliable" on exercises with little wrist movement — [the5krunner, 2 Apr 2026](https://the5krunner.com/2026/04/02/garmin-strength-training-features-survey/)
- **WHOOP Strength Trainer** (launched 2023, expanded May 2026): muscular load is estimated from weights, reps and sets plus wrist accelerometer and gyroscope, with exercise-specific "movement profiles" (a squat is scored differently from a calf raise). Lifting now influences Strain and recovery guidance. Users can pre-build workouts, pick pre-built ones, or add sets after the session. "Exercise Trends" shows volume, history and PRs. WHOOP AI can build strength workouts from goals, equipment, target muscles and limitations. Wrist wear is required — [Gadgets & Wearables, 22 May 2026](https://gadgetsandwearables.com/2026/05/22/whoop-strength-trainer-2/); [WHOOP Locker](https://www.whoop.com/thelocker/introducing-strength-trainer-a-new-way-to-quantify-the-impact-of-your-strength-training/). Strength sessions raise Sleep Need — [WHOOP Locker](https://www.whoop.com/thelocker/introducing-strength-trainer-a-new-way-to-quantify-the-impact-of-your-strength-training/)
- **Peloton IQ** (1 Oct 2025): plans for goals such as weight loss, strength or "living longer"; Performance Estimates such as "harder than your usual"; uses Garmin, Fitbit and Apple Health data. Camera hardware enables rep counting, form feedback and weight and progressive-overload advice — [TechRadar](https://www.techradar.com/health-fitness/exercise-equipment/peloton-revamps-loads-of-its-fitness-equipment-introduces-an-ai-powered-coaching-features-and-of-course-hikes-prices); [Peloton IQ page](https://www.onepeloton.com/peloton-iq). The official page does not mention readiness or recovery integration specifically — [Peloton IQ page](https://www.onepeloton.com/peloton-iq)
- **Garmin Connect+ Active Intelligence**: AI prompts at wake-up, after workouts and in the evening, based on sleep, HRV, training load and stress. The reviewer says it "continues to restate thin insights" — [the5krunner, 20 Apr 2026](https://the5krunner.com/2026/04/20/garmin-connect-plus-review/)

#### Strength-specific gaps in readiness (important for the client)
- Garmin Training Load undervalues strength: a hard leg session can count for less than a moderate run because of lower EPOC. There is no neuromuscular recovery model (the muscle map shows what was worked, not what is ready), no "previous weight/reps" memory when logging, and third parties cannot write strength sessions into Connect (no addSet() in the Connect IQ SDK) — [the5krunner, 2 Apr 2026](https://the5krunner.com/2026/04/02/garmin-strength-training-features-survey/)
- An April 2026 Garmin survey tested eight concepts: Neuromuscular Readiness Score, Neuromuscular Training Effect, Strength Training Primary Benefit (hypertrophy / max strength / endurance), Acute Strength Load, Muscle Map for Recovery, Strength-vs-Cardio Load Ratio, Strength Balance Score, and Muscle Map per activity. It also asked how much manual input users would accept. These are planned, not shipped — [the5krunner](https://the5krunner.com/2026/04/02/garmin-strength-training-features-survey/)
- A reviewer says "no current product correctly measures muscular strain from strength work". The same reviewer credits WHOOP's velocity-based strength-strain model as unique but says users must build and follow the routine in-app — [the5krunner WHOOP 5.0/MG review, upd. 7 May 2026](https://the5krunner.com/2025/10/31/2026-whoop-5-0-mg-review-discount-accuracy-strain-recovery-athletes/)
- Apple: DC Rainmaker notes there is no native custom strength builder and no native iPhone workout builder. Structured workouts come only from third-party apps — [DC Rainmaker, Jun 2025](https://dcrainmaker.com/2025/06/apple-watchos-26-announced-workout-buddy-and-more-explained.html)

#### Trust evidence
- Reviewer: readiness scores are "arbitrary across all brands". WHOOP MG nightly HRV correlated poorly with a morning chest-strap reading (day-to-day r=0.30) but strongly with Oura (r≈0.84). Wrist strain is "much less" accurate than biceps placement for sport — [the5krunner](https://the5krunner.com/2025/10/31/2026-whoop-5-0-mg-review-discount-accuracy-strain-recovery-athletes/)
- WHOOP community thread (17 Oct 2025): a user reported 64% recovery with more sleep but 75% when the sleep window was trimmed. WHOOP Coach cited "proprietary algorithms", and support suggested moving the strap. The user regrets the purchase. A second user says a 10% HRV drop gave 43% recovery despite a 100% sleep score, and criticises percentage-change logic for low-HRV baselines — [WHOOP Community](https://www.community.whoop.com/t/nonsensical-recovery-score-make-it-make-sense/9660)
- An older but often-cited critique explains why Garmin Training Readiness is "not accurate" — [the5krunner, Aug 2023](https://the5krunner.com/2023/08/02/garmin-training-readiness-not-accurate-heres-why/). Forum discussions ask whether to move or skip workouts on low readiness — [TrainerRoad forum](https://www.trainerroad.com/forum/t/garmin-low-training-readiness-move-workout-or-skip/79182) (not fetched; title only)
- Garmin Connect+ review commenters argue "more metrics are not what users need", and some want an AI coach instead — [the5krunner](https://the5krunner.com/2026/04/20/garmin-connect-plus-review/)
- Peloton IQ hands-on (Women's Health, 12 May 2026, via The Clip Out): rep counter overcounted (12 vs 10). Form feedback missed small position errors. The weight-increase suggestion "matched how she coaches" clients. There is no input for injuries or how the body feels that day — [The Clip Out](https://theclipout.com/peloton-iq-womens-health-fast-company-review/)

#### AI vs rules (evidence)
- **WHOOP Coach**: generative, launched Sep 2023 "powered by OpenAI" (GPT-4) — [BusinessWire](https://www.businesswire.com/news/home/20230926899032/en/WHOOP-Unveils-the-New-WHOOP-Coach-Powered-by-OpenAI-the-First-Wearable-to-Deliver-Highly-Individualized-Performance-Coaching-on-Demand). Memory added in 2025. The reviewer calls it "the best AI coaching in sport tech" — [the5krunner](https://the5krunner.com/2025/10/31/2026-whoop-5-0-mg-review-discount-accuracy-strain-recovery-athletes/). The scores themselves are algorithmic, not LLM.
- **Oura Advisor** (rolled out to all members 31 Mar 2025): LLM that explains Sleep, Activity, Readiness and Stress data. It has "Memories", selectable tone (supportive to goal-oriented) and helps build action plans. Company surveys (not independently verified): 60% said it helped them understand metrics, 87% said it remembered their goals, 56% said it helped turn insights into action — [BusinessWire](https://www.businesswire.com/news/home/20250331565896/en/Oura-Advisor-an-AI-powered-Personal-Health-Companion-Now-Rolling-Out-to-All-Oura-Members)
- **Google Health Coach (Gemini)**: public preview launched Oct 2025 (US Android). It expanded to iOS and UK, CA, AU, NZ and SG on ~10–11 Feb 2026 — [TechRepublic](https://www.techrepublic.com/article/news-fitbit-ai-coach-expands-ios-five-markets/). Rebranded to Google Health app / Google Health Premium on 7 May 2026, rolled out to all users by 26 May 2026, live in 37 countries — [SensAI (competitor content)](https://www.sensai.fit/blog/google-health-premium-fitbit-ai-coach-2026). Onboarding is a short chat covering goals, sleep habits, training preferences and equipment. It generates routines, and the Today and Fitness tabs show plans with targets that "adjust in real time" — [TechRepublic](https://www.techrepublic.com/article/news-fitbit-ai-coach-expands-ios-five-markets/)
- **Apple Workout Buddy** (watchOS 26): generated voice (modelled on Fitness+ trainers) gives a pep talk, milestones and a recap. Positive-only. Supports run, walk, ride, HIIT and strength. English-only at launch. Needs an Apple Intelligence iPhone nearby and headphones — [DC Rainmaker](https://dcrainmaker.com/2025/06/apple-watchos-26-announced-workout-buddy-and-more-explained.html)
- **Apple AI health coach ("Mulberry"/Health+) was scaled back**: Bloomberg, 5 Feb 2026. Some features will move into the Health app instead of a paid coach — [PYMNTS](https://www.pymnts.com/apple/2026/apple-scales-back-ai-health-coach-plans/). Earlier reporting had the Health+ chatbot planned for 2026 — [AppleInsider, Nov 2025](https://appleinsider.com/articles/25/11/09/moving-apple-fitness-over-to-health-is-part-of-apples-2026-ai-plan)
- **Samsung**: "AI-powered" Energy Score, but the cited release describes no generative coach — [Samsung Newsroom](https://news.samsung.com/us/samsung-health-app-evolves-with-ai-powered-proactive-intelligence-to-help-users-stay-ahead-of-their-health/)

#### Wearable / recovery product profiles (compact)
| Product | Site | Platforms | Monetization (date) | Readiness → workout | AI | Notable UX |
|---|---|---|---|---|---|---|
| WHOOP | whoop.com | iOS, Android + screenless band | One $199/yr, Peak $239/yr, Life $359/yr (AU page, fetched 25 Oct 2026) [WHOOP](https://www.whoop.com/au/en/membership). Hardware is bundled in the membership. Advanced Labs blood test ~$200 extra [the5krunner](https://the5krunner.com/2025/10/31/2026-whoop-5-0-mg-review-discount-accuracy-strain-recovery-athletes/) | Recovery % + Strain target; Strength Trainer muscular load | LLM Coach (OpenAI) on top of algorithmic scores | 3 dials (Sleep/Recovery/Strain), Plan tab, Exercise Trends/PRs |
| Oura | ouraring.com | iOS, Android + ring | $5.99/mo membership [Oura blog](https://ouraring.com/blog/the-value-of-oura-membership/) | Bands with generic advice ("prioritise rest" below 70) | Oura Advisor LLM | Three daily scores; auto-detects 40+ activities, 89% accuracy (claim) [Oura blog](https://ouraring.com/blog/the-value-of-oura-membership/) |
| Garmin Connect / Connect+ | garmin.com | iOS, Android + watches | Core free; Connect+ $6.99/mo or $69.99/yr (since 27 Mar 2025) [the5krunner](https://the5krunner.com/2026/04/20/garmin-connect-plus-review/) | Training Readiness bands; Fitness Coach / Strength Coach plans | Active Intelligence (AI insights) — reviewer: thin | Live Activity mirrors strength sets and reps to the phone; Nutrition tracking with AI photo recognition added 5 Jan 2026 [the5krunner](https://the5krunner.com/2026/04/20/garmin-connect-plus-review/) |
| Google Health (ex-Fitbit) | — | Android, iOS; Fitbit Air $99 band | Premium $9.99/mo or $99.99/yr (annual up from $79.99); included in Google One AI Pro/Ultra [Android Authority, 7 May 2026](https://androidauthority.com/google-health-premium-price-inclusions-features-3664507/) | "Adaptive" plans; readiness link not confirmed | Gemini coach (real LLM) | Today / Fitness / Sleep / Health tabs; multimodal meal logging |
| Apple Watch / Health | apple.com | watchOS, iOS | Fitness+ $9.99/mo or $79.99/yr [SensAI, 1 Oct 2026](https://www.sensai.fit/blog/nike-training-club-vs-fiton-vs-apple-fitness-plus-2026) | Training Load 7-vs-28 days; effort rating | Workout Buddy (generated voice); AI coach shelved | Activity rings, Workload view; HR zones in HealthKit API in iOS 27 [WWDC26](https://developer.apple.com/videos/play/wwdc2026/207/) |
| Samsung Health | samsung.com | Android (Galaxy) | Pricing not in the release | Daily Cardio Load gives targets and rest times | "AI" Energy Score | Energy Score on Home |
| Polar | polar.com | iOS, Android + watches | Fitness Program subscription; price not on the support page | Nightly Recharge + Cardio Load → lighter sessions; 20 levels | Rules-based (no LLM claim) | 4-week blocks, level system (note the game-like levels) |

### Inferences
- All readiness products map one composite score into 4–5 bands with fixed copy. This is effectively rule-based even when marketed as "AI", and the generative layer (WHOOP Coach, Oura Advisor, Gemini) only explains. That validates the client's split: the rules decide, the LLM explains.
- For a strength-focused product, logged sets, reps, RPE and e1RM trends are a stronger and more trusted signal than wrist HRV. Wearable readiness should be a soft modifier (e.g. "readiness Low → cap top-set RPE or swap to the technique variant"), always shown with its reason and overridable by the user.
- Trust breaks when the score contradicts the user's felt state and there is no explanation ("proprietary algorithms"). Showing which inputs moved the decision is a differentiator.
- Per-muscle recovery maps and "neuromuscular readiness" are still unbuilt even at Garmin (survey stage, Apr 2026). The client can do a simple, explainable rule version from logged volume per muscle group without any wearable. This is a realistic "later" feature and could be an MVP-lite feature.
- Polar's 20-level Fitness Program and Zwift levels show that "levels" tied to real training compliance are an accepted pattern.

### Gaps
- No independent study found (2025–2026) on how often users follow or ignore readiness-based suggestions; trust evidence is anecdotal (forums, reviews).
- Polar Fitness Program price, Coros strength features and Coros readiness details were not verified.
- Whether Google's Gemini coach adjusts workouts by readiness or sleep is not confirmed by the sources fetched.
- Samsung Health premium pricing and any Samsung generative coach: not found.
- WHOOP's documented logic for how Recovery changes the recommended Strain target was not fetched.

---

## Q2. Which ecosystems combine training, nutrition and recovery successfully, and what did it cost them (complexity, churn)?

### Takeaway
No one has a clearly successful all-in-one "fitness OS". The closest are hardware-anchored ecosystems: WHOOP (recovery + strength + labs + LLM coach), Garmin (training + readiness + nutrition added Jan 2026 + Connect+), Google Health (Gemini coach + meal logging + $99 band) and Peloton (content + IQ + hardware). Each paid for breadth with subscription fatigue, price hikes and thin-feature criticism. Peloton is the clearest cautionary data point: 2.553M connected-fitness subscribers, down 8.8% year over year, while still raising prices. Apple shelved its paid AI health coach. Content-library apps (NTC free, FitOn freemium, Fitness+, Les Mills+, Centr, Sweat) compete on video classes and price, not on adaptive logic. The client's niche (self-guided strength + explainable progression + gamification) is underserved by them.

### Cited Findings

#### Peloton (App One, App+, Strength+, Peloton IQ, hardware)
- Prices: App One $15.99/mo or $159/yr; App+ $28.99/mo or $289/yr; 30-day trial with card — [SensAI, checked 1 Oct 2026](https://www.sensai.fit/blog/nike-training-club-vs-fiton-vs-apple-fitness-plus-2026). All-Access US/Canada raised $5 to $49.99/mo (Oct 2025, the first rise in 3 years); UK All-Access £39→£45, App+ £24→£28.99 — [TechRadar, 1 Oct 2025](https://www.techradar.com/health-fitness/exercise-equipment/peloton-revamps-loads-of-its-fitness-equipment-introduces-an-ai-powered-coaching-features-and-of-course-hikes-prices)
- **Strength+**: standalone $9.99/mo app with self-paced multi-week strength programs, a workout generator and audio guidance through earbuds. iOS since late 2024, Android since 20 Aug 2026 — [9to5Google](https://9to5google.com/2026/08/20/peloton-strength-plus-android-app-release/)
- Peloton IQ features (Personalized Plans, Recommendations, Rep Tracking, Form Feedback, Suggested Weights) need All-Access. Camera features are limited to Bike+, Tread+ and Row+ — [Peloton IQ](https://www.onepeloton.com/peloton-iq)
- **Public metrics, Q4 FY2026 (reported 6 Aug 2026)**: 2.553M connected-fitness subscribers (−8.8% YoY); 503K app subscriptions (−9%); 5.5M total members (−8%). Monthly CF churn was 2.2% in Q4 vs 1.8% a year earlier; Peloton attributed this to a one-time email-algorithm issue. FY revenue $2.446B (−1.8%), first full-year net profit ($63.2M), FCF $378M. Strength was 30% of completed workouts in Q4 (cardio 55%). Q1 FY27 guide: 2.455–2.475M subscribers — [Pelobuddy](https://www.pelobuddy.com/peloton-q4-fy2026-earnings/)

#### Apple Fitness+
- $9.99/mo or $79.99/yr; 12 workout types plus meditation; 5–45-minute sessions; Custom Plans; iPhone-only is OK; Apple devices only — [SensAI, 1 Oct 2026](https://www.sensai.fit/blog/nike-training-club-vs-fiton-vs-apple-fitness-plus-2026)
- Jan 2026 programs aimed at "decision fatigue": "Make Your Fitness Comeback" (4 weeks, 3×10 min), "The Strength Basics in 3 Weeks", "Back-to-Back Strength and HIIT" — [Athletech News](https://athletechnews.com/apple-tackles-decision-fatigue-with-new-years-fitness-rollout/)
- Bloomberg called Fitness+ Apple's weakest-performing paid service; it moved under the Health division in Oct 2025 — [AppleInsider](https://appleinsider.com/articles/25/11/09/moving-apple-fitness-over-to-health-is-part-of-apples-2026-ai-plan). The planned AI coach / Health+ was scaled back on 5 Feb 2026 — [PYMNTS](https://www.pymnts.com/apple/2026/apple-scales-back-ai-health-coach-plans/)

#### Content apps (video / guided classes)
- **Nike Training Club**: free, no IAP; trainer-led classes, whiteboard workouts, multi-week programs, Apple Health sync; 4.8★ from ~281K ratings — [SensAI, Aug–Oct 2026](https://www.sensai.fit/blog/best-home-workout-apps-no-equipment-2026)
- **FitOn**: free classes; PRO $19.99–$39.99 (regular annual $29.99 per TINA, as cited) adds meal plans, offline and HR zones; live classes nearly hourly with a live leaderboard; 4.9★ from ~283K ratings — [SensAI](https://www.sensai.fit/blog/nike-training-club-vs-fiton-vs-apple-fitness-plus-2026); [SensAI](https://www.sensai.fit/blog/best-home-workout-apps-no-equipment-2026)
- **Centr**: $29.99/mo, $59.99 per 3 months, $119.99/yr; structured celebrity-led programs (Hemsworth brand) — [SensAI](https://www.sensai.fit/blog/best-home-workout-apps-no-equipment-2026)
- **Les Mills+** (App Store IAP, checked 7 Jun 2026, $ storefront presumed US): Base $14.99/mo or $89.99/yr; Premium $29.99/mo or $179.99/yr — [AppPricingLab](https://www.apppricinglab.com/iap/apple/1483001711)
- **Sweat** (IAP, checked 21 Mar 2026): monthly $13.99–$24.99 (several SKUs), quarterly $54.99, yearly $134.99 — [AppPricingLab](https://apppricinglab.com/iap/apple/1049234587)
- **Freeletics**: the App Store describes an AI Coach that "customizes each workout to your fitness level, adjusting in real time based on your feedback" and adapts to time, travel or focus. IAP: Training Coach $34.99–$79.99; Training + Nutrition bundle $49.99–$89.99; 4.6★ from ~22K ratings — [App Store](https://apps.apple.com/app/id654810212). EU: Coach 12 weeks €39.99, 12 months €79.99 — [Subger (low-reliability aggregator)](https://subger.com/en/service/freeletics). The evidence is feedback-driven adaptation; the technical nature of the "AI" is not disclosed.

#### Smart hardware strength
- **Tonal 2**: $4,295 (bundle $5,215), or rental via Whim $279/mo plus a $49 setup fee. Required membership $59.95/mo with a 12-month commitment, unlimited household accounts. Adaptive weight after a strength assessment; modes Smart Flex, Chains, Eccentric; Spotter; Smart View camera form feedback; "Tonal Intelligence" personalised workouts, "Daily Lift" — [Tonal, fetched 25 Oct 2026](https://tonal.com/products/tonal-2)
- **Tempo**: membership $39/mo, AI form feedback via 3D infrared; >$316M raised; ~10% layoffs Mar 2022. No 2025–2026 updates found — [yespress profile (secondary)](https://yespress.io/tempo.md)

#### Ecosystems that bundle nutrition and recovery
- **Garmin Connect+** added nutrition tracking (barcode + AI image recognition) on 5 Jan 2026. Reviewer verdict: "generally not worth paying for", except for gym strength (Live Activity) or as a MyFitnessPal replacement. Users complain of a thin bundle and recurring cost — [the5krunner, 20 Apr 2026](https://the5krunner.com/2026/04/20/garmin-connect-plus-review/)
- **Google Health Premium** bundles the Gemini coach, adaptive fitness plans, sleep insights, and multimodal (text, photo, voice) meal logging. The annual price rose $20 — [Android Authority](https://androidauthority.com/google-health-premium-price-inclusions-features-3664507/). Photo meal estimates have no published accuracy data (competitor's claim) — [SensAI](https://www.sensai.fit/blog/google-health-premium-fitbit-ai-coach-2026)
- **WHOOP** has moved into healthspan ("Pace of Aging"), blood pressure, ECG and Advanced Labs (US only) on higher tiers — [WHOOP](https://www.whoop.com/au/en/membership). The BP feature is under FDA scrutiny (Jan 2026) — [the5krunner](https://the5krunner.com/2025/10/31/2026-whoop-5-0-mg-review-discount-accuracy-strain-recovery-athletes/)
- **Freeletics** sells a Training + Nutrition bundle — [App Store](https://apps.apple.com/app/id654810212)

#### Strava (social + training graph)
- Est. (Sacra): ~$490M ARR in 2025 (+32%); ~195M registered users and ~50M MAU; ~2% paid. $2.2B valuation (May 2025). Acquired Runna (Apr 2025) and The Breakaway (May 2025). Confidential S-1 filed Feb 2026. Prices: $79.99/yr, $11.99/mo, Family $139.99, Strava + Runna $149.99/yr — [Sacra](https://sacra.com/c/strava/) (estimates, not company-reported)

#### Engagement references
- **Zwift**: $19.99/mo (raised from $14.99 in May 2024) or $199.99/yr; the free 25 km monthly allowance ended in 2025. Reportedly >1M subscribers in 2024 (internal sources); peak concurrent users 41,680 in 2026 vs 49,114 in 2021. 2025 features: Bike Upgrades unlocked by milestones (Mar 2025); Progress Report replaced Streaks (Dec 2025) — [the5krunner, upd. 3 Oct 2026](https://the5krunner.com/2026/01/23/peak-zwift-2026-indoor-cycling-trends/)
- **Zwift levels**: level distribution of engaged subscribers, Jul 2025: 1–10 13%, 11–20 19.3%, 21–30 19.9%, 31–60 38.4%, 61–99 8.5%, 100 1%. Leveling was made harder in Jul 2024; Streak Flair added Apr 2025; Zwift is "looking seriously at creating more carrots" for level-100 riders — [Zwift Insider](https://zwiftinsider.com/level-stats-2025)
- **Sweatcoin**: >100M users and ~11M wallet opt-ins (company claim, Jul 2022). Rewards come from brand offers; the SWEAT token launched in Sep 2022 — [Decrypt](https://decrypt.co/106142/step-counter-app-sweatcoin-raises-13m-fund-leap-web3). No 2026 data found.

#### Product profile summary (content/ecosystem)
| Product | Format | Personalization | Social | Price (date) | AI reality |
|---|---|---|---|---|---|
| NTC | Video classes + programs | Light | Minimal | Free (Oct 2026) | None claimed |
| Apple Fitness+ | Video classes, Custom Plans | Plan builder | SharePlay, Activity rings sharing (not re-verified) | $9.99/mo (Oct 2026) | Workout Buddy voice |
| Peloton App / Strength+ | Video + audio self-paced | IQ plans and recs | Leaderboards (hardware) | $9.99–$28.99/mo | IQ: recs + CV on camera hardware |
| Freeletics | Generated bodyweight/gym sessions | Feedback-driven adaptation | Limited | $34.99–$79.99 per plan term | "AI Coach" claim; mechanism undisclosed |
| Centr / Sweat / Les Mills+ | Trainer-led programs / classes | Program choice | Community (Sweat) | $13.99–$29.99/mo | Not evidenced |
| FitOn | Free live/VOD classes | Light | Live leaderboard | Free / PRO ~$30/yr | Not evidenced |
| Tonal | Hardware + classes | Adaptive weight (sensor-driven) | — | $4,295 + $59.95/mo | "Tonal Intelligence" + camera |
| Zwift | Game world | Training plans | Group rides, races | $19.99/mo | N/A; engagement benchmark |

### Inferences
- Breadth costs money. Each ecosystem that added nutrition, labs or AI raised prices or added tiers (Peloton, Google +$20/yr, WHOOP 3 tiers, Garmin Connect+), and reviewers question the value. A TMA MVP should not add nutrition or recovery. Logged training and progression should be the whole MVP; nutrition and wearables come later as optional modules.
- Peloton's numbers (subscriber decline despite AI and price increases) suggest AI features do not stop churn on their own. Habit and progression loops matter more, which is where the game layer fits.
- Strength is now 30% of Peloton workouts, Peloton launched a standalone strength app, WHOOP and Garmin are investing in strength load, and Apple added strength programs. Strength is the current growth vector across incumbents, which validates the niche but signals rising competition.
- Zwift's experience suggests game levels need a long tail of "carrots" (unlocks beyond the max level) and anti-grind tuning (Zwift made leveling harder in 2024). This is directly relevant to the client's character leveling.
- Freeletics' "adapt via post-workout feedback" (too easy / too hard) is the most transferable pattern for a no-wearable MVP.

### Gaps
- No public churn, retention or revenue data was found for Freeletics, Centr, Sweat, Les Mills+, FitOn, NTC, Tonal, Tempo or WHOOP; only Peloton reports publicly.
- No source quantifies the complexity cost (e.g. support load, retention drop) of adding nutrition to a training app.
- Tempo's current status (2025–2026) is unclear; the only source found is a secondary profile with no recent entries.
- Sweatcoin and Sweat Economy 2026 metrics: none found.
- Sweat and Centr 2026 feature changes (any AI): not researched in depth.

---

## Q3. What integration routes are realistic for a web / Telegram Mini App?

### Takeaway
A TMA cannot read Apple HealthKit or Android Health Connect at all. Both are on-device stores with no web or REST API, and Telegram's Mini App API exposes no health data (only sensors such as accelerometer and gyroscope, plus location, biometrics and storage). The realistic routes are:
1. Manual logging in the TMA. This is the core and needs no integration.
2. Cloud OAuth APIs (WHOOP, Oura, Google Health API, Polar, Strava, and Garmin when approved), connected through a browser OAuth flow from the TMA to the client's backend.
3. A thin companion native app (or Terra / ROOK / Sahha mobile SDK) to bridge HealthKit and Health Connect to the backend.
4. Aggregators: Terra from $399/mo, Sahha from $299/mo, ROOK $399/mo, or the self-hosted Open Wearables.

In 2026 every cloud API is restrictive: approval gates, 10-user dev caps, and bans on sending data to AI. Garmin's program was paused in spring 2026. Fitbit Web API shuts down on 2 Nov 2026. Strava and Oura restrict AI use. Wearable integration is a "later" item, and the LLM-explanation layer must be designed around these AI clauses.

### Cited Findings

#### Telegram Mini App capabilities
- Native APIs in Telegram.WebApp include DeviceStorage and SecureStorage (Bot API 9.0), BiometricManager (7.2), LocationManager, Accelerometer, DeviceOrientation, Gyroscope, orientation lock, home-screen shortcuts and downloadFile (8.0), HapticFeedback (6.1), QR scanner (6.4) and CloudStorage (6.9). No health data or HealthKit API was found in the documentation read (the page was truncated at about 74%) — [Telegram Bot API: Web Apps](https://core.telegram.org/bots/webapps)
- Note: Accelerometer and Gyroscope access could in principle allow phone-in-pocket or phone-on-bar rep-counting experiments later (inference; no source tested this).

#### Apple HealthKit
- iPhone, Apple Watch, visionOS and iPadOS 17+ each have an on-device HealthKit store that syncs between devices. macOS 13+ and iPadOS ≤16 can include HealthKit code but cannot read or write data. The data model covers characteristics, samples (quantity, category, correlations for food and blood pressure), workouts (HKWorkout with type, duration, distance and energy, plus associated samples) and source/device metadata — [Apple: About the HealthKit framework](https://developer.apple.com/documentation/healthkit/about-the-healthkit-framework.md)
- The Apple documentation fetched shows no web or REST access. Access is through native APIs only, and a server gets data only if the app uploads it — [Apple docs](https://developer.apple.com/documentation/healthkit/about-the-healthkit-framework.md). Confirmed operationally by Terra: Apple Health is "on-device, mobile-only… no web API" — [Terra docs](https://docs.tryterra.co/faq/help-topics/data-api-sdk/mobile-sdk-setup-permissions-and-crashes/mobile-only-sources-need-sdk-not-web-or-rest)
- iOS 27 / watchOS 27 (WWDC26 session 207) add built-in HR and cycling-power zones on HKWorkout (zoneGroupsByType, live zone updates). No new sets/reps/weight types were mentioned — [WWDC26 207](https://developer.apple.com/videos/play/wwdc2026/207/)
- Apple has no native per-set strength data model or builder; third-party apps fill this gap — [DC Rainmaker](https://dcrainmaker.com/2025/06/apple-watchos-26-announced-workout-buddy-and-more-explained.html)

#### Android Health Connect
- Record types relevant here: ExerciseSessionRecord (exerciseType incl. STRENGTH_TRAINING and WEIGHTLIFTING, plus segments and laps), HeartRateRecord, RestingHeartRateRecord, HeartRateVariabilityRmssdRecord, SleepSessionRecord (stages), WeightRecord, BodyFatRecord, NutritionRecord (macros), Vo2MaxRecord and others. Background reads need READ_HEALTH_DATA_IN_BACKGROUND. Reading data older than 30 days needs READ_HEALTH_DATA_HISTORY — [Android Developers: data types](https://developer.android.com/health-and-fitness/guides/health-connect/plan/data-types)
- Health Connect is mobile-only, with no web API — [Terra docs](https://docs.tryterra.co/faq/help-topics/data-api-sdk/mobile-sdk-setup-permissions-and-crashes/mobile-only-sources-need-sdk-not-web-or-rest)
- Not verified: whether ExerciseSegment carries per-set repetition counts and weight (see Gaps).

#### Cloud APIs (usable from a backend with OAuth started in the TMA)
- **WHOOP API**: OAuth 2.0 with an `offline` scope for refresh. Scopes: read:recovery, read:cycles, read:sleep, read:workout, read:body_measurement, read:profile. Webhooks for sleep, recovery and workouts send IDs only. Rate limits 100 requests/min and 10K/day. Dev access is capped at 10 members until approval (privacy policy and design guidelines required). Selling data is banned. Currently free, but WHOOP may charge later — [Terra blog, 2026](https://tryterra.co/blog/whoop-api-data-access-permissions-limitations-2026)
- **Oura API v2**: OAuth2; 10-user cap until approved; Personal Access Tokens deprecated Dec 2025; Gen3+ users need an active membership. Data covers sleep, readiness, activity, HR and workouts. **Agreement effective 8 Jun 2026: sending API data into AI assistants is prohibited.** Training, fine-tuning or embeddings need written approval, as does charging users for connected functionality. Aggregators cannot pass Oura data, even derived, to AI systems. Oura may add API fees — [Terra blog](https://tryterra.co/blog/oura-api-ai-apps-access-permissions-commercial-restrictions) (secondary summary of Oura terms; verify with the primary [Oura API docs](https://partnersupport.ouraring.com/hc/en-us/articles/20949682312211-The-Oura-API))
- **Garmin Connect Developer Program** (Health, Activity, Women's Health, Training, Courses APIs): business-only, free to approved developers (some metrics may carry license fees), approval historically within ~2 business days, integration 1–4 weeks — [Garmin FAQ](https://developer.garmin.com/gc-developer-program/program-faq). **In spring 2026 the application form was replaced with "Under Construction"**, with no reopening date. Garmin may add fees with 30 days' notice — [Terra blog, 7 Sep 2026](https://tryterra.co/blog/garmin-connect-developer-program-pause). Third parties cannot write strength sets into Connect — [the5krunner](https://the5krunner.com/2026/04/02/garmin-strength-training-features-survey/); Hevy's push of completed sets was blocked — [the5krunner](https://the5krunner.com/2026/04/20/garmin-connect-plus-review/)
- **Google Health API** (successor to the Fitbit Web API, launched Mar 2026): REST, Google OAuth 2.0; all scopes "Restricted" (security review); a reconciled multi-source stream; parity with Health Connect planned for Q4 2026–Q1 2027. **Fitbit Web API support ended 30 Sep 2026; endpoints return 410 Gone from 2 Nov 2026** — [Google Developers](https://developers.google.com/health/about). The Google Fit REST API retired in Jun 2025 — [Terra blog](https://tryterra.co/blog/garmin-connect-developer-program-pause)
- **Strava API** (agreement of Nov 2024): no showing a user's data to other users; no use for "model training related to AI/ML"; restrictions on "analytics, analyses"; ~30 days' notice given — [DC Rainmaker](https://dcrainmaker.com/2024/11/stravas-changes-to-kill-off-apps.html)

#### Aggregators (pricing as published)
- **Terra**: Quick Start $499/mo monthly or $399/mo annual, 100K credits/mo; each active authentication costs 200 credits/mo (≈500 users if no event overage — inference from the page); overage from $0.005 per credit. Add-ons: Health Scores from $499/mo, Planned Workouts $99/mo, Streaming $99/mo; Enterprise is custom — [Terra pricing](https://tryterra.co/pricing). Apple Health, Samsung Health and Health Connect need the Terra mobile SDK (Swift, Kotlin, React Native, Flutter); the web widget cannot complete these connections. Garmin, Fitbit and Oura use REST — [Terra docs](https://docs.tryterra.co/faq/help-topics/data-api-sdk/mobile-sdk-setup-permissions-and-crashes/mobile-only-sources-need-sdk-not-web-or-rest). You still need your own WHOOP credentials and approval — [Terra WHOOP blog](https://tryterra.co/blog/whoop-api-data-access-permissions-limitations-2026)
- Alternatives, from a vendor comparison (Sahha), verified Jul 2026: Sahha $299/mo (annual) for 1,000 users with a 30-day trial; ROOK Core $399/mo for 750 users plus add-ons; Junction (ex-Vital) unpublished, legacy $0.50/user/mo with a $300 minimum; Thryve from €499/mo for 500 users; Spike from $450/mo; Fitrockr from €50/mo; **Open Wearables free, MIT, self-hosted, with its Apple Health SDK "coming soon"** — [Sahha comparison (vendor bias)](https://sahha.ai/compare/terra-alternatives/)

#### Route matrix for the client
| Route | Works in a pure TMA? | Data | Cost | Risk |
|---|---|---|---|---|
| Manual logging in the TMA | Yes | Sets, reps, weight, RPE, body weight | 0 | None; this is the core |
| WHOOP / Oura / Google Health / Polar / Strava OAuth → backend | Yes (OAuth in an external browser, callback to the backend) | Recovery, sleep, HRV, workouts | Free APIs, but approvals needed | Approval caps; AI-use bans (Oura, Strava); Garmin closed to new applicants |
| Companion iOS/Android app (own or via Terra/ROOK/Sahha SDK) | No (needs a store app) | HealthKit / Health Connect: workouts, HR, HRV, sleep, weight, nutrition | Dev cost + $299–$499/mo aggregator, or self-host | App review, two codebases |
| iOS Shortcuts / file export from Health | Partial (user-run) | Exported XML/CSV | 0 | Poor UX; not verified as a sustainable route |
| Aggregator REST only (no SDK) | Yes | Cloud wearables only (no Apple Health) | From $299–$399/mo | Cost before product-market fit |

### Inferences
- MVP: no integrations. Treat body weight, sleep hours and "how do you feel" check-ins as manual inputs to the rule engine. This mirrors what readiness scores do while staying transparent and wearable-free, and it avoids the AI-clause problem entirely.
- Later, phase 1: Google Health API + WHOOP + Polar direct OAuth from the backend (free, web-friendly). Do not pipe Oura or Strava data into the LLM explanation layer under current terms. The rule engine may use derived values only if the terms allow; legal review is needed.
- Later, phase 2: a minimal companion app (React Native or Flutter + the Terra/ROOK SDK, or HealthKit / Health Connect directly) for Apple Health and Health Connect. This unlocks Apple Watch and Samsung users, who are a large share of strength trainers.
- Aggregator pricing ($300–$500/mo minimum) is a poor fit before product-market fit. Open Wearables (self-hosted) or direct APIs are cheaper for a small TMA.
- Garmin is the most important strength-wearable ecosystem but is currently closed to new applicants and blocks set write-back, so do not promise "Garmin sync" in the roadmap.

### Gaps
- Whether Telegram's Mini App docs mention health data in the truncated last ~26% of the page was not checked (very unlikely, but unverified).
- Health Connect ExerciseSegment fields (per-set repetitions, weight) were not confirmed; the API reference fetch failed.
- Polar AccessLink, Coros and Samsung Health partner API terms in 2026 were not researched.
- WHOOP's AI-use terms were not verified from the primary source.
- Pricing for Terra's free or dev tier and startup programs: a startup accelerator page exists ([Terra](https://tryterra.co/startup-accelerator)) but was not fetched.
- No source documents a working Telegram Mini App that syncs with Apple Health. The "companion app" pattern is inferred from platform constraints.
