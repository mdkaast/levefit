# Strength-training trackers & AI/adaptive strength coaching apps — market notes (as of Oct 25, 2026)

Source caveat for the writer: many 2026 price/feature roundups come from competitor-run blogs (SensAI, Alpha Progression, Boostcamp, Fitbod, Dr. Muscle, FitBudd, Coachway). Their figures say they were checked against vendor pages and the App Store, but each one is flagged below. Company user counts are **claims**. App Store ratings are platform data on the check date.

---

## Q0. Product profiles (feature catalog / competitor-matrix raw data)

### Takeaway
The market splits into three groups: (1) cheap, fast loggers (Hevy, Strong, Setgraph, StrengthLog, Liftosaur), now adding simple rule-based progression and LLM hand-offs; (2) adaptive "coach" apps priced at $13–$50/mo (Fitbod, Gravl, Alpha Progression, Juggernaut AI, RP, Dr. Muscle, Evolve). Almost all of these run rule-based or "expert system" engines, even when marketed as AI; (3) human-coach products at $30–$200/mo (Ladder, Future, Caliber), plus coach-side SaaS (Hevy Coach, Trainerize).

### Cited Findings

**Hevy (hevyapp.com). Logger plus social, iOS/Android/Web/Apple Watch/Wear OS**
- Claims "17+ million athletes" and 4.9 on the App Store and Google Play from 630k+ combined ratings (site, Oct 2026). Features: routine planner, warm-up/drop/failure set types, automatic rest timers, notes, exercise charts, PRs, 1RM calculator, exercise videos, social feed (follow/like/comment, copy routines), web version — [hevyapp.com](https://www.hevyapp.com/)
- US App Store 4.9 from about 92k ratings (checked Sep 15, 2026); earlier claim of 16M+. Free: unlimited logging, no ads, capped at 4 routines, 7 custom exercises, 3 months of graph history. Pro: $2.99/mo (a second $3.99 SKU exists), $23.99/yr, $74.99 lifetime. Previous-session values auto-fill each set; supersets and drop sets are native; rest timer auto-starts — [SensAI Hevy review (competitor)](https://www.sensai.fit/blog/hevy-review-2026)
- **Hevy Trainer** (Pro) builds routines from 6 inputs (experience, goal, equipment, frequency, duration, muscle focus). It raises weight once the top of the rep range is hit on all sets (double progression). Hevy calls it "an algorithm, not AI." It uses no sleep/HRV/readiness inputs. A Hevy app for ChatGPT analyzes history, generates programs and saves routines back to Hevy, and works on the free tier. v3.1.13 (Sep 2026) added a "send workout to ChatGPT/Claude" button on the finish screen — [SensAI](https://www.sensai.fit/blog/hevy-review-2026)
- Pricing re-verified Sep 8, 2026; Hevy runs 50% first-year annual promos — [SensAI pricing comparison](https://www.sensai.fit/blog/fitness-app-pricing-free-tier-comparison)
- Reddit sentiment: "Easy to use, the free version has everything most people need"; "helps with progressive overload" — [GummySearch Reddit aggregation](https://gummysearch.com/tools/best-products/workout-apps/)

**Hevy Coach (trainer SaaS)**
- Priced by active clients: up to 10 for $25/mo, 11–25 for $50, 26–50 for $90, 51–100 for $160, up to 1,000 for $700. 30-day trial, no card. Clients get free Hevy Pro. No nutrition, client payments or white-label (figures as of Aug 2026, per a competitor) — [Coachway (competitor)](https://coachway.io/articles/hevy-coach-pricing/)

**Strong (strong.app). Minimalist logger, iOS/Android/Apple Watch**
- Pro $4.99/mo, $29.99/yr ($19.99 for 6 months), $99.99 lifetime. Free tier: unlimited logging, 3 custom routines, charts Pro-only — [SensAI pricing](https://www.sensai.fit/blog/fitness-app-pricing-free-tier-comparison)
- "Two-tap set logging," best-in-class CSV export. No social feed, AI, programming or exercise demos. Watch app is logging-only — [SensAI 4-way comparison (competitor)](https://www.sensai.fit/blog/hevy-vs-strong-vs-fitbod-vs-jefit)
- Praised for: fast, clean set entry; standalone Apple Watch logging; rest timer with wrist taps. Complaints: 3-routine cap; subscription instead of a flat fee; scrolling-wheel input on the watch is cumbersome; a rest setting carries over to other routines that use the same exercise; no notes that carry over between sessions; drop-set entry missing — [JustUseApp review aggregation](https://justuseapp.com/en/app/464254577/strong-workout-tracker-gym-log/reviews)

**Fitbod (fitbod.me). Black-box generator, iOS/Android/Watch**
- Inputs: goal, experience, equipment, split, duration and preferences. Exercise selection favors recovered muscles and learns from skips, replacements, deletions and "Recommend more/less/exclude". Progression raises load or reps after "comfortable" sessions and eases after hard ones. Proprietary **mStrength** deliberately varies intensity and volume. Estimated Strength, Max Effort Days and logged RIR refine estimates. Per-muscle recovery runs 0–100%, with full recovery up to 7 days; Apple Health/Strava activity is counted. After a break, weights are lowered. New users get conservative estimates from aggregate data. The help center **never uses the term ML** and describes **no per-workout "why" screen**; the Body-tab recovery heatmap is the main visible rationale — [Fitbod Help: How Fitbod Creates Your Workout](https://help.fitbod.me/hc/en-us/articles/360004429814-How-Fitbod-Creates-Your-Workout)
- Fitbod's own blog claims "over 100 million logged workouts" and, elsewhere on the same page, "more than 10 million users". It claims 1,600+ HD exercise videos and says a Digital AI Coach, Injury Mode and Clubs are "launching soon" — [Fitbod blog (self-promotional)](https://fitbod.me/blog/fitbod-vs-gravl-strength-training-app-review/)
- $15.99/mo, $95.99/yr. No free tier: a 7-day trial requires a card, and after it you cannot log new workouts. Legacy subscribers keep $12.99/$79.99 — [SensAI pricing](https://www.sensai.fit/blog/fitness-app-pricing-free-tier-comparison)
- Complaints: "many of the workouts generated don't make sense… sets and weights don't follow sound exercise science" (Trustpilot, Jan 2025). Trial converted to an annual charge (Oct 2026). "Way too expensive" (Oct 2026) — [Trustpilot Fitbod p.2](https://www.trustpilot.com/review/fitbod.me?page=2). Competitor-compiled complaints: "random" workouts lacking progression, too many exercises, dangerously heavy weight suggestions — [Dr. Muscle (competitor, financial stake)](https://dr-muscle.com/fitbod-app-review-alternative/)

**Alpha Progression (alphaprogression.com). Rule-based per-set recommendations, iOS/Android**
- Estimates a **10-rep max** per exercise and combines it with past performance, sets done today, planned targets and available gym weights. RIR is optional; if not entered, it is **inferred** from performance. No recommendation the first time an exercise is done. Adjusts weight and reps set by set. $12.99/mo, $79.99/yr, 14-day trial on yearly only. Free tier: unlimited logging, manual plans, all 795 exercises with videos; generator, recommendations and charts are Pro-only. Export CSV free; no Apple Watch (on roadmap); 13 languages. App Store 4.9 from 2,195 ratings (Oct 3, 2026) — [SensAI JAI vs RP vs AP (competitor)](https://www.sensai.fit/blog/juggernaut-ai-vs-rp-hypertrophy-vs-alpha-progression-2026)
- App Store: plan generator (goal, experience, days, target muscles); automatic warm-up sets; plate calculator showing the closest lower weight; multiple gyms with their own equipment and weights; exercises rated by "muscle-building potential"; planned deloads and weekly ramps in sets and RIR; auto PRs including "mini PRs" for reps and volume. Legacy prices $24.99/mo and $99.99/yr. A critical bug that blocked completing sets was fixed in v6.2/6.3 — [App Store](https://apps.apple.com/us/app/gym-workout-alpha-progression/id1462277793)

**Juggernaut AI (juggernautai.app). Powerlifting "expert system AI," iOS/Android**
- Per-set RPE, a daily readiness check (0–100 score since v3.0), and session/week/block check-ins. Adjusts before, during and between sessions and across blocks. Warm-up ratings can raise the day's target. Since v2.5, weekly check-ins can cut accessory sets. The maker calls it "expert system artificial intelligence." $34.99/mo, $349.99/yr, 2-week web trial. 4.8 from 5,655 ratings (Oct 3, 2026) — [SensAI](https://www.sensai.fit/blog/juggernaut-ai-vs-rp-hypertrophy-vs-alpha-progression-2026)
- Readiness 1–5 on motivation, sleep, calories, soreness/fatigue, plus per-muscle soreness; adjusts that day's loads and rep scheme. Example: an RPE 10 on set 2 dropped the third set of pull-ups. Onboarding: age, height, weight, history, frequency, goals, PRs, recovery, weak points. Cons: confusing dashboard, hard-to-read blue-on-black design, no live coach — [Garage Gym Reviews](https://garagegymreviews.com/juggernautai-review)

**RP Hypertrophy (rpstrength.com). Feedback-driven volume, iOS/Android (Play since Dec 2025)/Web**
- Uses pump, soreness and workload feedback, not RPE. Adjusts sets per muscle weekly. Load rises by a small % weekly, or by a rep if the increment falls outside the range. Deload in the last week of the block. $34.99/mo, $299.99/yr, no trial, 30-day refund (web only). 45+ premade plans, 250+ technique videos, English only, **no built-in rest timer by design**. 4.3 from 234 ratings — [SensAI](https://www.sensai.fit/blog/juggernaut-ai-vs-rp-hypertrophy-vs-alpha-progression-2026)
- Complaints: users must add sets manually when the app suggests 1 set per muscle; the 4-week meso feels too short; "Paid for one month… totally not worth it" (Reddit); no plate or warm-up calculator — [Dr. Muscle review (competitor, author admits bias)](https://dr-muscle.com/rp-hypertrophy-app-review/)

**Dr. Muscle (dr-muscle.com). "AI personal trainer," iOS/Android/PWA**
- Founded 2016 by Dr. Carl Juneau (PhD in exercise epidemiology). Jan 2026: Dr. Muscle X rebuilt as a PWA (x.dr-muscle.com) with the "training logic unchanged," a progressive-overload algorithm "refined over nearly a decade." Claims "hundreds of thousands of workouts." The rebuild was AI-coded with Claude and ChatGPT and claims $125k/yr in dev savings (self-reported) — [GlobeNewswire press release, Jan 5 2026](https://www.globenewswire.com/news-release/2026/01/05/3212909/0/en/AI-Workout-App-Dr-Muscle-Launches-New-App-Saves-125-000-a-Year-by-Replacing-Developers-with-AI.html)
- Self-described: a "plus set" sets next week's loads (autoregulatory PRE), daily undulating periodization, data-detected plateaus trigger deloads — [dr-muscle.com](https://dr-muscle.com/fitbod-app-review-alternative/)
- Price unclear: $49/mo cited, but the same page also gives "$10–15/mo" and "$297/yr". Complaints about billing after cancellation, a dated UI and no wearable integration. No evidence it explains its recommendations — [AIToolsBakery, Sep 2026](https://aitoolsbakery.com/blog/dr-muscle-review/)

**Gravl (gravl.ai). e1RM plus 3-point effort rating, iOS/Android/Garmin**
- Converts each set to an e1RM; the day-one estimate comes from the self-reported experience level. About a 7% fatigue discount on the 2nd exercise for the same muscle. Weights snap to available plates and dumbbells, with reps adjusted to keep difficulty similar. The user rates each exercise **Easy/Ideal/Hard**. Hard keeps the weight and adds one rep to a set (a "rep ladder," 8-7-6 to 8-8-8), and once all sets hit target the weight goes up one equipment step. Easy triggers a bigger recalibration. The estimate is capped at about 10% growth per session. After more than 2 weeks off, suggestions ease about 1% per week. Injury flags with check-ins every 2 weeks. Not conversational. $14.99/mo, $34.99 for 3 months, $59.99–89.99/yr. Free: 3 workouts. App Store 4.9 (about 5.5k ratings), Google Play 4.8 (about 16.8k). Claims 1M+ users; Google Play shows 1M+ downloads (Sep 28, 2026) — [SensAI Gravl review (competitor)](https://www.sensai.fit/blog/gravl-app-review-2026)
- **Directly relevant**: Gravl's "8-7-6 to 8-8-8" logic is almost the client's own bench example (80×8, 80×7, 80×6).

**Ladder (joinladder.com). Coach-led team programs, iOS/Watch only**
- 23 coach-led "teams." A new 7-day plan publishes every Sunday. Audio cues and set-by-set timing. "Programs are designed for a whole team, not per-member"; "coach-designed… not algorithm-generated"; AI is used only for nutrition (Smart Log). Added plateau alerts (Jul 2026) and movable rest days (Aug 2026). PRO $29.99/mo or $179.99/yr; ELITE+ up to $49.99/mo with 1:1 chat and form checks. 7-day trial, no free tier, no Android. App Store 5.0 from about 212k ratings. Claims 300k+ paid members (Oct 2025 press release). Nov 2024: $15M Series B (Point72, ADvantage) plus $90M go-to-market from General Catalyst (as of Oct 23, 2026) — [SensAI Ladder review (competitor)](https://www.sensai.fit/blog/ladder-app-review-2026)
- Sensor Tower: Ladder, Lazyfit and Bodbot led the growth of the US "AI-focused fitness" cohort in 2Q24 (+28% revenue, +59% downloads YoY) — [Sensor Tower, Sep 2024](https://sensortower.com/blog/ai-features-strengthen-fitness-apps)
- Note: the client's analysis lists Ladder as an AI competitor. It is actually human-coach and team-programmed, not adaptive per user.

**Future (future.co). 1:1 human coach, US only, iOS/Android/watches**
- $199/mo ($149/mo on a 12-month prepay; $50 first month). The coach writes the program and adjusts it weekly. Assistant Coach AI (Jan 2025) is coach-facing only; a free AI-coaching beta was cancelled in Jun 2026. 4.9 iOS from 10,703 ratings. Claims 100k+ members (as of Sep 27, 2026) — [SensAI Future review (competitor)](https://www.sensai.fit/blog/future-app-review-2026)

**Caliber (caliberstrong.com). Coaching plus free app**
- Free app with curated plans. Caliber Pro group coaching $19/mo. Premium 1:1 about $200/mo. Plans are modified by a certified coach (2025 review) — [Garage Gym Reviews](https://www.garagegymreviews.com/?p=206368). Strength Score: not verified in my sources.

**Zing Coach (zing.coach). AI fitness generalist, iOS/Android**
- $10M Series A (Jul 2024, Zubr Capital and Triple Point). 1M+ downloads since 2021, "25% MoM growth" (claim). The AI Coach uses an LLM with a tone tailored to the user's "emotional profile." Computer-vision fitness tests, body-composition scanner (claim to replace DEXA), Zenia acquisition for real-time tracking. CEO Tanya Parfenyuk — [Pulse2](https://pulse2.com/zing-coach-ai-based-fitness-app-company-raises-10-million-in-series-a)
- Trustpilot complaints (Aug 2025–Jan 2026): mostly billing and auto-renewal ($139 annual renewal, double charges, refunds denied). **Zing confirmed weights are not adjusted automatically** ("doesnt increase your weights"); no injury adaptation; no custom exercises; videos fail to load — [Trustpilot Zing](https://www.trustpilot.com/review/zing.coach?page=3). Workouts freeze between sets; plans stall after payment — [JustUseApp](https://justuseapp.com/en/app/1552207792/zing-expert-ai-fitness-coach/reviews)
- Implication: Zing is a home/general-fitness competitor, not a strength-progression one.

**JEFIT (jefit.com)**
- 1,400+ exercises including on the free tier; ad-supported. Elite $12.99/mo, $69.99/yr. Watch app Elite-only. Around since 2010 — [SensAI pricing](https://www.sensai.fit/blog/fitness-app-pricing-free-tier-comparison), [SensAI comparison](https://www.sensai.fit/blog/hevy-vs-strong-vs-fitbod-vs-jefit) (the comparison says JEFIT has no LLM features; JEFIT's own blog markets "AI-powered progressive overload," which I did not verify — [JEFIT blog](https://www.jefit.com/blog/7-best-ai-powered-progressive-overload-workout-trackers-of-2026-for-automated-strength-and-muscle-gains))

**Boostcamp (boostcamp.app). Program library plus tracker**
- Free: 14,000+ programs (mostly user-made), full tracker, RPE logging, rest timers, PR boards, weekly report, program builder, Strength Score; plate calculator limited to 10 uses. Pro $59.99/yr or $14.99/mo: all 132 coach programs (count of Pro-only programs inconsistent on the page), Muscle Tracker heatmap, questionnaire-based programs, **Auto Progression (linear, double progression, missed-rep adjustments)**, analytics — [Boostcamp "Is it free" (self-published)](https://www.boostcamp.app/is-boostcamp-free)

**StrengthLog (strengthlog.com, Styrkelabbet AB, Sweden)**
- Free: unlimited logging, 600+ exercises with video, linear-progression programs, 1RM estimates, warm-up suggestions, plate calculator, rest timer, Strength Levels, **monthly challenges, friend challenges, streaks** (gamification). Premium: double/triple progression, heatmaps, RPE/RIR/%1RM logging, **MCP integration to ChatGPT/Claude (read-only)**. $16.90/mo, $37.90 for 3 months, $109/yr. 4.9 from about 3.7k ratings. Complaints: small and unclear "complete set" tap target (tapping elsewhere edits values); cluttered home screen; no opt-out of Strength Levels — [App Store](https://apps.apple.com/us/app/-/id1434229662)

**Liftosaur (liftosaur.com). Scriptable, rule-based**
- Programs are plain text in **Liftoscript**. Finishing a workout rewrites the text with new weights, reps and sets. Built-in linear and double progression; custom logic is scriptable; RPE support. Presets include GZCLP and 5/3/1. Web editor — [Liftosaur overview](https://www.liftosaur.com/blog/posts/liftosaur-overview/). 4.9 from 338 ratings, free download — [AppFollow](https://apps.appfollow.io/ios/liftosaur-scriptable-workouts/1661880849?country=us). Source on GitHub — [github.com/astashov/liftosaur](https://github.com/astashov/liftosaur)

**Setgraph (iOS)**
- "Smart Plates" set the weight from the plates you load; a "next set due" signal replaces the rest timer; option to log only PRs; Live Activities / Dynamic Island. Pro is lifetime, monthly or yearly (prices not shown). 4.7 from about 2.9k ratings. Complaints: small "add set" button causes accidental edits to previous sets; users want comparison with their average, not just the last session — [App Store](https://apps.apple.com/us/app/setgraph-workout-tracker/id1209781676)

**Evolve AI (evolveai.app, Skynet Coaching). Powerlifting expert system**
- "Genesis expert system engine," block periodization (work capacity, hypertrophy, strength, peaking), end-of-block advice, difficulty and duration previews. Partner of Powerlifting America. IAPs from $20.99/mo to $219.99/yr. 4.5 from 436 ratings. Complaints: confusing UI and black screens; **"sleep and soreness inputs did not change the workout"**; warm-up RPE targets didn't match the plan — [App Store](https://apps.apple.com/us/app/-/id1631174176)

**Planfit (planfit.ai, Korea)**
- Claims 4M+ users, 16M+ workouts, 300M+ sets, 4.7 from 67k+ ratings; maps gym equipment (245k gyms). Seed round from Springcamp (2021). Founded 2021 — [Planfit About](https://planfit.ai/en/about)

**WHOOP Strength Trainer**
- Feb 2026: build routines from a text prompt or a screenshot/PDF; factors in lifting history, volume and the Recovery score; can suggest a de-loaded version when Recovery is low. Per-exercise trends were still "Coming Soon" — [Wareable, Feb 24 2026](https://www.wareable.com/fitness-trackers/whoop-coach-ai-strength-trainer-workout-builder-update)

**Gymshark Training**
- Free on-demand workouts with videos; can't customize workouts; no supersets or drop sets; weak progress tracking (2024 review) — [Tom's Guide](https://tomsguide.com/wellness/fitness/gymshark-training-app-review-effective-workouts-for-free). Not a real progression competitor.

**Trainerize (coach platform)**
- Free for 1 client, $9 for 2, $23 for 5, about $49 for 15, $120 for 50, about $250 for 200, Studio Plus $248 for up to 500. Add-ons: nutrition $20–45, video $10, payments $10, branded app $169 — [FitBudd (competitor)](https://www.fitbudd.com/insights/trainerize-pricing-explained-what-it-actually-costs-trainers-in-2026-vs-better-alternatives)

### Inferences
- In practice, "AI" in strength apps almost always means a deterministic rule engine or "expert system" (Juggernaut, Evolve, Gravl, Alpha Progression, Hevy Trainer, Boostcamp Auto Progression, Dr. Muscle). Real LLM use is limited to plan-building from prompts (WHOOP), external chat hand-offs (Hevy for ChatGPT, StrengthLog MCP), nutrition (Ladder) or motivational coaching (Zing). This matches the client's "rules decide, LLM explains" architecture and makes it a credible claim rather than a weakness.
- Price bands: loggers $3–5/mo (StrengthLog at $9/mo annualized is the outlier); adaptive apps $13–35/mo; human coaching $30–200/mo.

### Gaps
- Could not fetch current official pages for Strong, Fitbod, Caliber or Zing pricing; Zing's price ladder is unclear (user-reported $18.99–59.99).
- No public revenue for Hevy, Strong, Fitbod or Gravl from Sensor Tower or Appfigures. No independent user numbers for Hevy (17M is a claim) or Fitbod.
- Not researched: Strong's plate calculator and RPE details; Caliber's 2026 Strength Score; Setgraph prices; onboarding question lists for most apps beyond Juggernaut, Hevy Trainer, Fitbod and Alpha Progression.
- No Russian-language or Telegram Mini App fitness competitors were researched (out of scope here, but worth a separate check).

---

## Q1. Which products genuinely adapt the next session from actual performance, and how transparent are they?

### Takeaway
Real per-user adaptation from logged sets exists in Alpha Progression, Gravl, Juggernaut AI, Fitbod, RP, Dr. Muscle, Evolve, and partly in Hevy Trainer and Boostcamp Pro. **None documents a user-facing "why this recommendation" explanation.** Transparency comes from help-center articles or third-party reviews, not from inside the app.

### Cited Findings
- Fitbod adjusts load and reps from comfortable versus hard sessions, recovery % and breaks, but the help center describes no per-workout explanation screen; the recovery heatmap is the only visible rationale — [Fitbod Help](https://help.fitbod.me/hc/en-us/articles/360004429814-How-Fitbod-Creates-Your-Workout)
- Fitbod claims it "shows more of its work," but the detail lives in help articles — [Fitbod blog](https://fitbod.me/blog/fitbod-vs-gravl-strength-training-app-review/)
- Alpha Progression adapts set by set (10RM estimate, inferred RIR). Juggernaut adapts within and between sessions from RPE and readiness. RP adapts weekly volume from pump and soreness — [SensAI](https://www.sensai.fit/blog/juggernaut-ai-vs-rp-hypertrophy-vs-alpha-progression-2026)
- Gravl has an explicit, publishable rule set (rep ladder, ~10% cap, ~1%/week detraining) — [SensAI Gravl](https://www.sensai.fit/blog/gravl-app-review-2026)
- Hevy Trainer uses double progression only, with no readiness inputs — [SensAI Hevy](https://www.sensai.fit/blog/hevy-review-2026)
- Boostcamp Pro Auto Progression covers linear, double progression and "missed-rep adjustments" — [Boostcamp](https://www.boostcamp.app/is-boostcamp-free)
- Ladder and Future adapt only through human coaches (weekly); Ladder programs per team, not per member — [SensAI Ladder](https://www.sensai.fit/blog/ladder-app-review-2026), [SensAI Future](https://www.sensai.fit/blog/future-app-review-2026)
- Zing does not auto-adjust weights (company reply on Trustpilot) — [Trustpilot](https://www.trustpilot.com/review/zing.coach?page=3)
- Dr. Muscle: no evidence of explanation — [AIToolsBakery](https://aitoolsbakery.com/blog/dr-muscle-review/)
- Evolve gives "expanded advice at the end of each training block" (block-level, not per-set) — [App Store](https://apps.apple.com/us/app/-/id1631174176)

### Inferences
- Handling missed sessions and underperformance is thinly documented. Fitbod lowers weights after breaks; Gravl eases ~1%/week after more than 2 weeks off; Gravl's "Hard" rating holds the weight; Juggernaut drops sets on high RPE. Nobody documents a clear "you missed Tuesday, here's how the week reshuffles" flow. Ladder's movable rest days (Aug 2026) are the closest.

### Gaps
- Did not verify in-app screens of Alpha Progression or Gravl for tooltips explaining recommendations; reviewers don't mention any.

---

## Q2. Is "explained, rule-based adaptation" an open niche between dumb loggers and black-box generators?

### Takeaway
Yes, partly. The rule-based middle is crowded (Alpha Progression, Gravl, Boostcamp Pro, Hevy Trainer, Liftosaur), but **explainability is unclaimed**. Combining it with a gamified Telegram Mini App (no install, RU market) is not occupied by any product found.

### Cited Findings
- Hevy is moving up from logger toward adaptation (Trainer with double progression) and outsources "explanation" to ChatGPT/Claude via a hand-off button — [SensAI Hevy](https://www.sensai.fit/blog/hevy-review-2026)
- StrengthLog offers read-only MCP to ChatGPT/Claude — [App Store](https://apps.apple.com/us/app/-/id1434229662)
- The competitor critique of Hevy is that "rule-based progression can't diagnose plateaus." Ladder added "plateau alerts" in Jul 2026, showing the demand — [SensAI Hevy](https://www.sensai.fit/blog/hevy-review-2026), [SensAI Ladder](https://www.sensai.fit/blog/ladder-app-review-2026)
- SensAI states that among Hevy, Strong, Fitbod and Jefit "Nobody… is using LLM-based coaching" — [SensAI](https://www.sensai.fit/blog/hevy-vs-strong-vs-fitbod-vs-jefit)
- Liftosaur shows the extreme of transparency, with the program as editable text rules — [Liftosaur](https://www.liftosaur.com/blog/posts/liftosaur-overview/)
- Gamification precedent: StrengthLog's monthly and friend challenges, streaks and Strength Levels (some users dislike them and want an opt-out); Boostcamp's Strength Score; Alpha Progression's "mini PRs" — [StrengthLog App Store](https://apps.apple.com/us/app/-/id1434229662), [Boostcamp](https://www.boostcamp.app/is-boostcamp-free), [Alpha Progression App Store](https://apps.apple.com/us/app/gym-workout-alpha-progression/id1462277793)

### Inferences
- The closest "explained rules" competitor is the Hevy plus LLM hand-off pattern, which is generic and post-hoc. A native "plan vs actual, then decision, then the reason" card (e.g. "80×8/7/6: rep drop over 2 reps → hold 80 kg, target 8/8/7") would differentiate clearly. Gravl's rep-ladder rule is effectively this logic, but not presented as explanation.
- Risk: the explanation layer is easy to copy (Hevy already connects LLMs). The defensible parts are the rule engine's quality, the planned-vs-actual UX and the RU/Telegram distribution.
- Gamification should stay optional and "businesslike"; StrengthLog reviews show some lifters reject forced social/level elements.

### Gaps
- No Sensor Tower data on the size of the "middle" segment. No RU-market or Telegram-specific competitor scan.

---

## Q3. Recurring user complaints about AI-generated plans

### Takeaway
Complaints cluster around: nonsensical or random workouts and weights (Fitbod), adaptation that doesn't actually happen (Zing has no weight progression; Evolve ignores sleep and soreness), too little volume or a heavy manual-correction burden (RP), and, most loudly, aggressive billing and auto-renewals (Zing, Fitbod, Dr. Muscle).

### Cited Findings
- Fitbod: "many of the workouts generated don't make sense" (Jan 2025); trial auto-converted to an annual charge (Oct 2026) — [Trustpilot](https://www.trustpilot.com/review/fitbod.me?page=2)
- Fitbod (competitor-compiled): random workouts, no progression, too many exercises, dangerously heavy weights — [Dr. Muscle](https://dr-muscle.com/fitbod-app-review-alternative/)
- Zing: weights not auto-increased; no injury adaptation; renewal and refund disputes; plans stalled after payment — [Trustpilot](https://www.trustpilot.com/review/zing.coach?page=3), [JustUseApp](https://justuseapp.com/en/app/1552207792/zing-expert-ai-fitness-coach/reviews)
- Evolve: readiness inputs didn't change the workout; plan inconsistencies — [App Store](https://apps.apple.com/us/app/-/id1631174176)
- RP: 1-set suggestions forcing manual additions — [Dr. Muscle review](https://dr-muscle.com/rp-hypertrophy-app-review/)
- Dr. Muscle: charged after cancelling, refunds denied — [AIToolsBakery](https://aitoolsbakery.com/blog/dr-muscle-review/)
- Juggernaut: an overwhelming dashboard; the reviewer saw no new PRs in 6 weeks — [GGR](https://garagegymreviews.com/juggernautai-review)
- Research context: lifters underpredict reps to failure by about 0.95 reps on average (meta-analysis of 12 studies), so RIR-based inputs are noisy — [SensAI](https://www.sensai.fit/blog/juggernaut-ai-vs-rp-hypertrophy-vs-alpha-progression-2026)

### Inferences
- Trust breaks when an input visibly has no effect, or when the output can't be justified. An explicit "your input X changed Y" message addresses both. Transparent, fair billing is itself a differentiator in this category. Because RIR is unreliable, inferring effort from reps actually done versus planned (as Alpha Progression does) is safer for 6–36-month lifters.

### Gaps
- Could not pull Reddit threads directly (r/weightroom, r/naturalbodybuilding); the Reddit evidence is via aggregators and secondary quotes.

---

## Q4. Logging UX patterns that minimize taps during a set

### Takeaway
Best practice: pre-fill each set with the previous session's or the recommended values so logging is one tap to confirm; auto-start the rest timer on completion; control everything from the lock screen or watch; calculate weight from plates; give large, unambiguous tap targets.

### Cited Findings
- Hevy: previous-session values auto-fill; rest timer auto-starts; native supersets and drop sets; warm-up/drop/failure set types — [SensAI Hevy](https://www.sensai.fit/blog/hevy-review-2026), [hevyapp.com](https://www.hevyapp.com/)
- Strong: "two-tap set logging" — [SensAI](https://www.sensai.fit/blog/hevy-vs-strong-vs-fitbod-vs-jefit); watch scroll-wheel input is cumbersome, and users want keyboard input — [JustUseApp](https://justuseapp.com/en/app/464254577/strong-workout-tracker-gym-log/reviews)
- Setgraph: "Smart Plates" set the weight from the plates loaded; "next set due" instead of a timer; Live Activities / Dynamic Island; small "add set" button causes mis-taps — [App Store](https://apps.apple.com/us/app/setgraph-workout-tracker/id1209781676)
- Alpha Progression: per-set targets pre-filled; auto warm-up sets; plate calculator rounding down to an achievable weight; per-gym weights so recommendations are always loadable; optional RIR (inferred if skipped) — [App Store](https://apps.apple.com/us/app/gym-workout-alpha-progression/id1462277793), [SensAI](https://www.sensai.fit/blog/juggernaut-ai-vs-rp-hypertrophy-vs-alpha-progression-2026)
- Gravl: one 3-option rating per exercise (Easy/Ideal/Hard) instead of per-set RPE; snaps to available equipment — [SensAI Gravl](https://www.sensai.fit/blog/gravl-app-review-2026)
- StrengthLog: the complaint about a small or unclear "complete set" target shows the cost of getting this wrong — [App Store](https://apps.apple.com/us/app/-/id1434229662)
- Juggernaut: rest timer in a Live Activity — [SensAI](https://www.sensai.fit/blog/juggernaut-ai-vs-rp-hypertrophy-vs-alpha-progression-2026)

### Inferences
- For a Telegram Mini App (no Live Activities or watch): show the plan as pre-filled rows ("80 × 8") with one large "✓ as planned" button and quick "−1 / −2 rep" chips for underperformance (80×7, 80×6). Auto-start rest after confirmation. Ask one optional effort rating per exercise (Gravl-style) rather than per-set RIR. Telegram's MainButton and haptics fit this pattern. Equipment-aware rounding (Alpha Progression, Gravl) prevents unloadable recommendations.

### Gaps
- No quantitative tap-count benchmarks found. Telegram Mini App constraints (background timers, notifications while the screen is locked) were not researched and should be checked technically.
