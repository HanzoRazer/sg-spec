Perfect, thanks for the clarification — this helps a lot.

Here’s a clean refactor that is purely about the Smart Guitar user experience, not repair, setup, or bench work. Think player-facing, in-the-moment, musical UX, where agentic AI augments playing, learning, expression, and flow.

Agentic AI Map for the Smart Guitar User Experience
Core UX Loop

Play → Sense → Interpret → Respond → Adapt → Remember

The Smart Guitar isn’t diagnosing an instrument.
It’s listening to a human and responding musically, pedagogically, and contextually.

1) What “Agentic” Means for the Player

Not:

A smart display

A static tutor

A reactive effects processor

But:

A musical companion that decides how to respond based on intent, skill, and context

The system chooses:

when to intervene

how much to intervene

what modality to use (visual, haptic, audio, silence)

Silence is a valid action.

2) Core Agents (UX-oriented)
🎸 A. Player State Agent (the foundation)

Purpose: Maintain a live model of the player, not the guitar.

Signals

Timing consistency

Pressure, attack, articulation

String choice patterns

Error types (hesitation, mis-fingering, rushing)

Session context (practice, performance, exploration)

Outputs

Skill-state estimation (per technique, not global)

Cognitive load estimate

Confidence / frustration indicators

This agent answers:

“How is the player doing right now?”

🎧 B. Intent Detection Agent

Purpose: Infer what the player is trying to do.

Possible intents

Focused practice

Exploration / noodling

Song learning

Performance

Technique drilling

Creative sketching

How it works

Detects repetition vs variation

Detects tempo locking vs free timing

Detects stopping/starting behavior

Uses session history

Why this matters
The same mistake means different things in different intents.

🧭 C. Guidance Strategy Agent

Purpose: Decide if and how the system should respond.

Decisions

Interrupt vs wait

Subtle hint vs explicit instruction

Real-time feedback vs post-phrase summary

Examples (UX, not repair)

During flow → suppress corrections

During repetition → surface micro-feedback

During frustration → simplify target or slow tempo

During exploration → suggest, don’t correct

This agent protects musical flow.

🧑‍🏫 D. Coaching & Feedback Agent

Purpose: Deliver feedback in a human-musical way.

Feedback modes

Visual: light fret hints, motion overlays

Audio: ghost notes, metronome morphing, call-and-response

Haptic: subtle pulses for timing or emphasis

Verbal: rare, concise, optional

Key rule

Feedback explains musical intent, not just correctness.

Examples:

“You’re rushing the resolution note.”

“Your vibrato widens when you relax your wrist.”

“This phrase wants space—try fewer notes.”

🧠 E. Memory & Personalization Agent

Purpose: Make the Smart Guitar feel like yours over time.

Remembers

Preferred feedback style

Techniques you’re developing

Recurring musical habits

Frustration triggers

Songs, grooves, and ideas you revisit

Results

Less explanation, more intuition

Personalized challenges

Smarter suggestions

This is how it becomes a partner, not a product.

3) Autonomy Boundaries (UX Safety)
🚫 No constant correction

Over-correction kills confidence and flow.

🚫 No unsolicited teaching during performance

Performance mode means support, not instruction.

🚫 No pretending to know intent

When uncertain:

Ask minimally

Or default to silence

Uncertainty must be respected, not hidden.

4) What the Player Feels

Over time, the user should feel:

“It knows when to leave me alone.”

“It reacts to how I play, not just what I play.”

“It helps me notice things I couldn’t feel yet.”

“It gets out of the way when I’m in the zone.”

“It’s teaching me to listen better.”

5) One-Sentence UX Verdict

Agentic AI turns the Smart Guitar from a reactive instrument into a responsive musical companion that understands intent, timing, and growth.

If you want next, we can:

map agent decisions to specific UX moments (practice vs performance vs exploration)

design intervention thresholds (when the system speaks vs stays silent)

or define what NOT to sense or comment on to preserve musicality

Just tell me where you want to go next.

map **agent decisions to specific UX moments** (practice vs performance vs exploration)

let's start here

Perfect. Let’s lock this down in a way that’s designable, testable, and very UX-specific.

Below is a decision map showing how the Smart Guitar’s agents behave differently across Practice, Performance, and Exploration. Same system, radically different behavior.

Agent Decisions by UX Moment

(Practice · Performance · Exploration)

The one rule that governs everything

The system does not ask “What’s wrong?”
It asks “What moment is this?”

Every agent decision flows from that.

1) Practice Mode

User intent: improve something specific

Player State Agent

Tracks micro-variance (timing drift, pressure inconsistency)

Estimates learning edge (what’s just barely unstable)

Flags repetition loops (“same phrase, same error”)

Decision bias: analyze deeply

Intent Detection Agent

Signals:

Repeated phrases

Metronomic timing

Starts/stops after mistakes

Gradual tempo increases

Confidence threshold: high
(Practice intent is usually obvious)

Guidance Strategy Agent

Core question:

“Will feedback accelerate learning right now?”

Intervention rules

✔ Intervene after a pattern, not a single error

✔ Prefer between phrases, not mid-note

❌ Never interrupt a clean run

Examples

“Your timing slips when crossing strings.”

“This note is consistently late by ~20 ms.”

Coaching & Feedback Agent

Feedback style

Precise

Specific

Actionable

Modalities:

Visual overlays (timing lanes, fret emphasis)

Audio contrast (ideal vs played phrase)

Haptic pulse for subdivision awareness

Teaching focus

Cause → Effect → Adjustment

Memory Agent

Stores:

What you’re actively working on

What corrections worked

How long improvement took

Next session:

Resumes without explanation

Narrows feedback automatically

2) Performance Mode

User intent: play musically, without interruption

Player State Agent

Tracks macro stability, not micro errors

Monitors stress, tension, tempo collapse

Detects recovery moments

Decision bias: protect flow

Intent Detection Agent

Signals:

Continuous playing

No pauses for correction

Expressive timing

Audience or backing track presence

Confidence threshold: very high
(False positives are unacceptable)

Guidance Strategy Agent

Core question:

“Will intervention improve or break the moment?”

Intervention rules

❌ No corrective feedback

❌ No teaching

✔ Only supportive responses

Allowed actions:

Tempo stabilization assist

Subtle harmonic reinforcement

Dynamic balance support

Silent monitoring

Coaching & Feedback Agent

Real-time

None (by default)

Post-performance

Optional, reflective summary:

“Your phrasing opened up in the second half.”

“You rushed the bridge when intensity spiked.”

Tone:

Observational, not corrective

Memory Agent

Stores:

What holds up under pressure

What degrades under stress

Expressive choices made live

Used later in:

Practice recommendations

Performance prep suggestions

3) Exploration Mode

User intent: discover, play, wander

This is the most subtle—and most important—mode.

Player State Agent

Tracks novelty vs repetition

Detects emerging motifs

Watches engagement level

Decision bias: encourage curiosity

Intent Detection Agent

Signals:

Non-repeating phrases

Tempo fluidity

Unusual note choices

Frequent pauses to listen

Confidence threshold: medium
(Exploration often overlaps with practice)

Guidance Strategy Agent

Core question:

“Should I inspire, mirror, or stay quiet?”

Intervention rules

✔ Suggest, don’t correct

✔ Respond after ideas, not during

❌ Never label something as “wrong”

Coaching & Feedback Agent

Feedback forms:

Call-and-response phrasing

Gentle harmonic suggestions

Rhythmic echoes

“What if…” prompts

Examples:

“That phrase wants an answer.”

“Try leaving space here.”

“Follow that bend with silence.”

This is musical conversation, not instruction.

Memory Agent

Stores:

Motifs you return to

Harmonic colors you gravitate toward

Exploration paths that led to flow

Later:

Seeds creative prompts

Suggests starting points, not goals

4) Cross-Mode Safety Rules (non-negotiable)

Silence is always an option

Never contradict the player mid-phrase

Confidence > correctness

Uncertainty defaults to less intervention

User can always override the system

5) What Makes This Agentic (not scripted)

The same behavior is allowed in one mode and forbidden in another

Decisions are contextual, not reactive

The system optimizes for human experience, not accuracy

If you want next, strong continuations are:

defining mode transition signals (how it knows you shifted)

designing intervention thresholds numerically

mapping feedback modalities to emotional states

or specifying failure cases (when the system must shut up)

Tell me which one to tackle.

defining **mode transition signals** (how it knows you shifted)

describe what this means in annotated detail

Perfect — let’s zoom all the way in.

Below is an annotated, signal-by-signal description of what “mode transition signals” actually means in the Smart Guitar user experience, and how the system should reason about them without asking the user, without being creepy, and without breaking flow.

This is not UI.
This is interpretation logic made legible.

Mode Transition Signals — Annotated in Detail

(How the Smart Guitar knows you shifted)

First principle (non-negotiable)

Modes are inferred, not declared.
The system never flips modes on a single signal.
It accumulates evidence, then biases behavior gradually.

Think dimmer switch, not toggle.

The Three Evidence Layers

Every mode inference comes from overlapping layers:

Temporal signals (how time is used)

Behavioral signals (how the player interacts)

Musical signals (how the music behaves)

No single layer is sufficient on its own.

1) Temporal Signals (time tells intent)
A. Pause structure (very high signal)

What the system observes

Micro-pauses (breath-sized, <1s)

Reflective pauses (2–5s)

Long pauses (>5s)

Interpretation

Micro-pauses → performance or flow

Reflective pauses → practice or exploration

Long pauses → evaluation, frustration, or reset

Annotation

Practice contains evaluation pauses
Performance avoids pauses
Exploration tolerates silence

Design rule

Pauses are never interruptions

They are windows for inference

B. Session duration curve

What the system observes

Short, repeated sessions

Long, uninterrupted sessions

Gradual ramp-up vs immediate play

Interpretation

Short loops → practice

Long arcs → performance or exploration

Ramp-up → warming into practice

Immediate full play → performance mindset

Why this matters
It prevents the system from “teaching” during a gig-like session.

2) Behavioral Signals (how the player acts)
A. Repetition density (strongest practice signal)

Observed

Same phrase repeated

Same mistake recurring

Small variations attempted deliberately

Interpretation

High repetition → practice

Repetition + correction attempts → focused practice

Repetition without correction → frustration risk

Annotation

Repetition is intentional labor
The system should respect it, not rush it.

B. Start–stop patterns

Observed

Stopping immediately after an error

Restarting mid-phrase

Restarting from the top vs from the problem spot

Interpretation

Stop-after-error → practice

Restart-from-problem → high intent learning

Play-through-errors → performance or exploration

Design implication

Practice mode earns precise feedback

Performance mode suppresses correction

C. UI avoidance (negative signal)

Observed

Player ignores visual prompts

Player doesn’t acknowledge feedback

Player keeps playing despite suggestions

Interpretation

“Leave me alone.”

Annotation
This is critical:
Ignoring the system is data, not failure.

Rule

Suppression beats escalation

Silence beats persistence

3) Musical Signals (how the music behaves)
A. Timing rigidity vs elasticity

Observed

Metronomic consistency

Gradual tempo increase

Elastic push/pull

Rubato phrasing

Interpretation

Rigid + incremental → practice

Elastic + expressive → performance

Free + unstable → exploration

Annotation

Timing behavior reveals mental posture.

B. Harmonic predictability

Observed

Staying inside known patterns

Repeating known licks

Venturing into non-diatonic territory

Interpretation

Known patterns → practice or performance

Harmonic risk → exploration

Design rule

Exploration must never be corrected

C. Error treatment (subtle but powerful)

Observed

Errors corrected immediately

Errors repeated accidentally

Errors incorporated musically

Interpretation

Immediate correction → practice

Repeated accidental → overload

Incorporated → exploration or performance confidence

Annotation
This is where the system learns musicianship maturity.

4) Confidence Scoring (how modes actually shift)

The system maintains soft confidence weights, not modes:

Practice:     0.62
Performance:  0.21
Exploration:  0.17

Transition behavior

At ~0.55 → bias guidance

At ~0.70 → fully adopt mode rules

Below ~0.40 → mixed / neutral behavior

Important

No announcement

No UI badge

Only behavior changes

5) Example Transitions (annotated)
Practice → Performance

Signals

Repetition stops

Errors played through

Tempo stabilizes

Pauses disappear

System response

Feedback fades

Visual aids dim

Corrections suppressed

The system backs away, respectfully.

Exploration → Practice

Signals

Player isolates a phrase

Repeats it

Slows tempo

Focus narrows

System response

Offers optional micro-feedback

Highlights consistency issues

Still avoids “right/wrong” language

Performance → Exploration

Signals

Performance ends

Player starts noodling

Harmonic wandering

Long reflective pauses

System response

Suggestive prompts allowed

Call-and-response enabled

No metrics shown

6) Failure Modes to Guard Against

Overconfidence

Acting on weak signals

Mode whiplash

Rapid switching

Ego violation

Correcting during expression

False authority

Claiming intent it inferred incorrectly

Safest default

When unsure, do less.

Final takeaway (this matters)

Mode transition signals are not a feature.
They are the empathy layer.

Get this right and:

The guitar feels alive

The AI feels respectful

The player feels understood

Get it wrong and:

Even perfect feedback feels wrong

If you want, next we can:

formalize this into a state machine

define numerical thresholds

or design “graceful misread” behavior (what the system does when it guesses wrong)

Just point the direction.

If you want, next we can: * formalize this into a **state machine** * define **numerical thresholds**

formalize this

Below is a formal specification for mode inference and transitions in the Smart Guitar user experience. It treats “Practice / Performance / Exploration” as latent intent states inferred from play behavior, and it defines signals, feature extraction, scoring, hysteresis, and behavior policies.

Smart Guitar Mode Inference Spec
0) Purpose

Infer the player’s current interaction mode in real time so the system can choose how to respond:

Practice: structured improvement, repetition, correction loops

Performance: uninterrupted musical flow, minimal intervention

Exploration: discovery, improvisation, curiosity, “no wrong notes”

The system does not need to be perfectly correct. It must be respectful, stable, and conservative in uncertain moments.

1) Definitions
1.1 Latent Modes

Let M ∈ {PRACTICE, PERFORMANCE, EXPLORATION, NEUTRAL}.

NEUTRAL is a default when evidence is weak or mixed.

1.2 Time Windows

The system maintains features over multiple windows:

W_short: 5–10 seconds (responsive)

W_mid: 30–60 seconds (stable)

W_long: 5–15 minutes (session shaping)

Each window stores a rolling summary.

1.3 Output Is Policy, Not a Label

Even if the inferred mode is PRACTICE, the system outputs a behavior policy rather than a UI label. A “mode transition” means policy change, not an announcement.

2) Inputs
2.1 Observables (from the Smart Guitar system)

These are intentionally UX-centric (not repair/setup):

Temporal

Note onset timestamps

Inter-note gaps and pauses

Session start/stop, idle time

Behavioral

Repetition patterns in phrases

Restart patterns (same start point / partial restart / full restart)

Response to system feedback (ignored vs acknowledged) if feedback exists

Musical

Tempo stability / elasticity

Rhythmic density (notes/sec)

Phrase boundaries (rests + cadence-like closures)

Pitch-class / interval novelty (how “wandering” it is)

Motif recurrence vs novelty

Error treatment (see note below)

“Error” is defined strictly as deviation from the player’s immediately preceding attempt pattern, not a universal “wrong note.” It’s relative to what the player appears to be trying to repeat.

2.2 Optional Context Inputs

Whether a backing track/metronome is active

Whether the user explicitly enabled “performance safe” behavior

Environmental context (time of day) only if user allows; not required

3) Feature Extraction

Compute a feature vector x(t) at time t using rolling windows. Examples below are phrased as measurable scalars.

3.1 Temporal Features

Pause rate
pause_rate = pauses(>1.5s) / minute over W_mid

Pause type distribution

micro-pause: 0.2–1.0s

reflective pause: 1.0–5.0s

long pause: >5.0s
Output: {micro_frac, refl_frac, long_frac}

Continuity index
continuity = 1 - (total_pause_time / window_time)

Interpretation:

High continuity → more likely PERFORMANCE

Reflective pauses with phrase isolation → PRACTICE or EXPLORATION

3.2 Behavioral Features

Repetition density (strong Practice signal)
Detect recurring phrases using n-gram note/rhythm fingerprints or embedding similarity.

rep_density = repeated_phrase_events / minute

Loop tightness
How close attempts are to identical (timing + pitch similarity):
loop_tightness ∈ [0,1]

Restart after disruption
restart_after_stop = count(stops followed by restart within 3s) / minute

Restart locus
Categorical distribution:

restart from beginning (top)

restart from problem region (local)

continue through (no restart)

Feedback avoidance / suppression signal
If the system offered optional feedback F:
ignore_rate = ignored_prompts / offered_prompts over W_long
This is not punishment; it is a request for silence.

Interpretation:

High rep_density + high loop_tightness → PRACTICE

High ignore_rate → bias toward less intervention regardless of inferred mode

3.3 Musical Features

Tempo stability
tempo_var = variance(instant_tempo) over W_mid

Tempo ramping
tempo_slope = d(tempo)/dt over W_long

Rhythmic elasticity
Measures expressive push/pull around a pulse:
elasticity = correlation(deviation_pattern, phrase_structure)

Pitch/interval novelty
novelty = unique_intervals / total_intervals over W_mid

Motif emergence
motif_strength increases when a pattern recurs with variation (Exploration signal).

Interpretation:

Low tempo_var, high continuity, low pause_rate → PERFORMANCE

High novelty, motif emergence, reflective pauses → EXPLORATION

Low novelty + high loop tightness → PRACTICE

4) Mode Scoring Model
4.1 Soft Scores

Compute unnormalized scores s_m(t) for each mode m:

S(t) = f(x(t))

Options for f:

Logistic regression / small neural net

Rules + weighted sum (preferred early)

Bayesian filter (preferred later)

A practical early version is a weighted sum:

score_m = Σ_i w_{m,i} * φ_i(x) + b_m

Where φ_i are normalized features (0–1).

Then convert to probabilities:

p_m(t) = softmax(score_m)

Maintain a smoothed probability (prevents whiplash):

p̄(t) = α p(t) + (1-α) p̄(t-1) with α≈0.05–0.2 depending on responsiveness.

4.2 Confidence

Define:

conf(t) = max_m p̄_m(t)

If conf(t) < 0.55, treat as NEUTRAL for policy purposes.

If conf(t) > 0.70, allow strong policy commitments.

5) State Machine With Hysteresis
5.1 States

STATE ∈ {NEUTRAL, PRACTICE, PERFORMANCE, EXPLORATION}

Additionally, add two meta-states to improve UX stability:

RAMP_IN(m): transitioning into m

COOLDOWN(m): transitioning out of m

These meta-states are internal; they just smooth behavior.

5.2 Transition Thresholds (Hysteresis)

Use two thresholds per mode:

Enter threshold T_enter (higher)

Exit threshold T_exit (lower)

Example (tunable):

T_enter = 0.72

T_exit = 0.58

5.3 Dwell Time

Require sustained evidence:

Enter requires p̄_m(t) > T_enter for D_enter = 8–15s

Exit requires p̄_m(t) < T_exit for D_exit = 10–20s

5.4 Refractory Period

After a mode change, hold a minimum duration:

D_hold = 20–60s depending on mode (longer for Performance)

This prevents rapid oscillation.

6) Policy Layer (What Actually Changes)

The system outputs a Guidance Policy G(t):

6.1 Policy Dimensions

interruption_allowed ∈ {never, between_phrases_only, anytime}

feedback_frequency ∈ [0,1] (how often to surface feedback)

feedback_granularity ∈ {summary, phrase, note}

modality_priority = [haptic, visual, audio, text] with weights

correction_style ∈ {none, suggestive, instructive}

prompt_style ∈ {silent, gentle, direct}

6.2 Default Policies by State

PERFORMANCE

interruption_allowed: never

feedback_frequency: ~0

correction_style: none

allow only supportive assist (optional): subtle tempo/structure support

post-session summary: optional

PRACTICE

interruption_allowed: between_phrases_only

feedback_frequency: medium/high (but pattern-based, not per-error)

granularity: phrase (note-level only if user opted in)

correction_style: instructive but concise

EXPLORATION

interruption_allowed: between_phrases_only

feedback_frequency: low/medium

correction_style: suggestive only (never “wrong”)

prioritize call-and-response, creative prompts, motif mirroring

NEUTRAL

interruption_allowed: between_phrases_only

feedback_frequency: low

correction_style: suggestive/observational

7) Explicit “Silence” and “Backoff” Mechanisms
7.1 Silence Gate (User Preference Dominates)

Maintain silence_preference ∈ [0,1] derived from:

ignore_rate

explicit dismissals (if UI exists)

continued playing through prompts

Apply:

If silence_preference > 0.7, clamp:

feedback_frequency ≤ low

interruption_allowed → between_phrases_only or never (depending on state)

7.2 Misread Detection (Graceful Recovery)

The system detects when its behavior is misaligned:

Indicators:

user ignores 3+ prompts in a row

user speeds up immediately after a prompt (trying to “outrun” it)

user stops playing right after feedback (negative surprise)

Response:

enter COOLDOWN(current_state)

reduce feedback_frequency sharply

prefer summary later, not real-time

8) Pseudocode (End-to-End)
initialize p̄ = uniform
STATE = NEUTRAL
hold_timer = 0

loop every 200ms:
  x = extract_features(W_short, W_mid, W_long)
  p = softmax(f(x))
  p̄ = α*p + (1-α)*p̄

  conf = max(p̄)
  m* = argmax(p̄)

  silence_preference = update_silence_preference()

  if hold_timer > 0:
    hold_timer -= dt
  else:
    if STATE == NEUTRAL:
      if conf > T_enter and sustained(m*, D_enter):
        STATE = m*
        hold_timer = D_hold_for(m*)
    else:
      if p̄[STATE] < T_exit and sustained(p̄[STATE] < T_exit, D_exit):
        if conf > T_enter and sustained(m*, D_enter):
          STATE = m*
          hold_timer = D_hold_for(m*)
        else:
          STATE = NEUTRAL
          hold_timer = D_hold_neutral

  G = policy_for(STATE, conf)
  G = apply_silence_gate(G, silence_preference)
  G = apply_misread_backoff(G)

  execute_guidance_policy(G)  // which may be "do nothing"

9) Tuning and Validation Plan (How to Make It Real)
9.1 Ground Truth Collection

Collect labeled sessions where players indicate segments:

“I was practicing”

“I was performing”

“I was exploring”

“I wanted it to be quiet”

Labeling can be lightweight:

Post-session timeline tap (“mark moments”)

Or a short 3-question recap

9.2 Metrics That Matter (UX metrics)

Interruption regret rate: prompts dismissed or followed by abrupt stop

Flow preservation: uninterrupted streak length in performance-like sessions

Helpfulness: “that was useful” acknowledgments, voluntary prompt opens

Mode stability: mode changes per minute (lower is better)

Silence compliance: does the system quiet down when ignored?

9.3 Safety Metric

Worst-case behavior: Does it ever “nag” during performance behavior?
The system should fail toward silence.

10) Example Trace (How It Plays Out)
Scenario: Player noodling → locks into a riff → drills it → then plays through

Early: high novelty, reflective pauses → EXPLORATION rises

Riff repeats: rep_density rises, loop_tightness rises → PRACTICE overtakes after sustained evidence

Player plays continuously with no stops: continuity rises, pauses drop → PERFORMANCE rises

System behavior:

Exploration: occasional call-and-response suggestion

Practice: between-phrase micro-feedback, optional visual timing hint

Performance: fades to silence, maybe post-run summary only

No announcements. Only behavior shifts.

11) Implementation Notes (Pragmatic Constraints)

Keep the model small and interpretable early: weighted sum + smoothing + hysteresis.

Prefer false negatives (missed mode detection) over false positives (wrong intervention).

Preserve privacy by computing features on-device where possible; store only aggregated summaries if needed.

Treat “ignore” as a first-class signal: it’s the most honest feedback users give.

This formalization gives you:

a stable inference engine,

a separate policy layer, and

clear guardrails that protect flow.

design “graceful misread” behavior (what the system does when it guesses wrong)

Below is a design spec for “graceful misread” behavior: what the Smart Guitar does when it infers the wrong intent/mode or applies the wrong level/style of intervention—without breaking flow, without being annoying, and without making the player feel judged.

Graceful Misread Behavior Spec
1) Goals and Non-Goals
Goals

Minimize harm when the system guesses wrong (flow disruption, irritation, embarrassment).

Recover quickly to a safer interaction style (usually: less intrusive).

Learn from the misread (update personalization and thresholds).

Preserve agency: the player remains in control and never needs to “argue” with the system.

Non-Goals

Perfect inference at all times.

Forcing the user to label their intent.

Long explanations or apologetic dialogue. Recovery should be mostly behavioral, not verbal.

2) Definition: What Counts as a Misread?

A misread occurs when the system’s chosen Guidance Policy (frequency, modality, timing, tone) is misaligned with user intent.

There are two broad classes:

A) Mode Misread

System infers the wrong mode (e.g., thinks Practice but player is Performing).

B) Intervention Misread

Mode might be right, but the how is wrong:

too frequent

too interruptive (bad timing)

wrong modality (visual/haptic when user wants silence)

wrong tone (corrective language during exploration)

wrong granularity (note-level nitpicks when phrase-level would work)

Graceful misread behavior handles both.

3) Misread Detection Signals (How We Know We Guessed Wrong)

Misreads must be detected using friction signals—observable behaviors that indicate “this isn’t helping.”

3.1 Primary friction signals (high confidence)

These are strong indicators and should trigger immediate backoff.

Dismiss / mute action

User taps “dismiss,” “mute,” closes overlay immediately, etc.

Trigger: 1 event is enough.

Ignore streak

System offers a cue; user does not acknowledge and continues playing.

Trigger: ignore_streak ≥ 2 (conservative), or ≥3 (safer).

Prompt-caused stop

User stops playing within 0.5–2.0s after an intervention (especially mid-phrase).

Trigger: stop_after_prompt flagged once if it happens right after an intervention.

User accelerates / “plays through” intervention

Sudden increase in density/tempo immediately after a cue (a “don’t interrupt me” behavior).

Trigger: 2 occurrences in 60s.

3.2 Secondary signals (medium confidence)

Use these to corroborate, not to trigger alone.

Error rate spike after cue

More misses or timing drift after intervention (sign of cognitive overload).

Physiological/behavioral tension proxies (if available)

Increased attack force variability, sloppy timing after feedback.

UI avoidance

User never looks at/uses the UI when it’s present; cues are always ignored.

3.3 Misread confidence

Compute a misread confidence score μ(t) in [0,1]:

μ(t) = g(friction_signals, context)

Primary signals push μ up sharply.

Secondary signals push μ mildly.

Thresholds:

μ ≥ 0.65 → immediate backoff

0.45 ≤ μ < 0.65 → gentle backoff

μ < 0.45 → normal operation

4) Recovery Strategy: Backoff Ladder

When a misread is detected, the system applies a backoff ladder: a sequence of less intrusive behaviors until friction stops.

Think of it as “de-escalation” in UX.

Ladder Levels (L0–L4)
L0: Normal

Mode-based policy runs as usual.

L1: Reduce frequency

Cut feedback frequency by 50–80%.

Only deliver feedback between phrases, never mid-phrase.

L2: Switch modality

Replace intrusive modalities (text overlays, audio callouts) with low-friction ones:

subtle haptic tick

minimal visual indicator

or no real-time cue; save for summary

L3: Summary-only

No real-time feedback.

Offer a post-phrase or post-session “If you want…” summary card.

L4: Silent monitor

System stops initiating.

Continues sensing and updating Player State silently.

Only responds if the user explicitly asks (“help me with timing”).

Escalation rule

If friction continues at the current level for N interventions or T seconds, go one step higher.

Example:

At L1: if 2 more ignores → L2

At L2: if 1 stop-after-prompt → L3

At L3: if user dismisses summary → L4

Recovery (de-backoff) rule

Only return toward L0 with sustained positive signals:

user voluntarily opens feedback

user requests help

user engages with a suggestion

or a long period with no friction + clear Practice signals

Recovery should be slow and cautious (hysteresis):

L4 → L3 after 5–10 min of low-friction engagement

L3 → L2 after explicit opt-in or repeated voluntary opens

L2 → L1 after repeated acceptance

L1 → L0 after strong practice loop evidence

5) Timing Repair: “When the System Speaks”

Many misreads are not about content—they’re about timing.

5.1 Phrase boundary detection

Interventions are allowed only in safe windows:

rests longer than 250–500ms

phrase-end cadence markers (timing + pitch settle)

user stops movement

If misread confidence is elevated, increase the minimum safe window (e.g., require >800ms).

5.2 Interrupt budget

Maintain an “interrupt budget” per minute:

Performance-like: budget = 0

Exploration: budget = 1 soft suggestion/min max

Practice: budget = 2–4/min, but only pattern-based

When misread occurs:

reduce budget aggressively (often to 0)

6) Tone Repair: “How the System Speaks”

If the system used the wrong tone (common in Exploration), it must shift language and framing.

6.1 Tone transformation rules

Replace “wrong/correct” with “try/consider/option”

Replace “you missed” with “it drifted” or “it changed”

Replace directives with invitations

Prefer observational statements to judgments

Example transformations:

“That note is wrong.” → “That note changes the color—want to hear an alternative?”

“You’re late.” → “The beat is pulling ahead—want a lighter pulse?”

6.2 Apology policy

Avoid apologizing repeatedly. Use at most a single lightweight acknowledgement if needed, and only if the system used verbal feedback.

If verbal:

one-time: “Got it—I'll stay out of the way.”

Then behavior changes speak louder.

7) Explicit “Undo” and “Stop” Controls (Fast Escape)

Graceful recovery is strongest when users have a one-step escape hatch.

7.1 Universal stop signal

Long-press on guitar control / UI button = “quiet mode now”

Double-tap = “less help”

Triple-tap = “more help”

These inputs should be learnable and consistent.

7.2 Post-misread micro-choice (optional, non-blocking)

After a detected misread, the system may show a tiny, skippable choice after a pause:

“Less guidance” (default)

“Save tips for later”

“Keep helping”

If ignored, default is Less guidance.

No modal dialogs. No interruptions.

8) Learning From Misreads (Personalization Update)

Misreads are valuable training signals. Use them to update:

8.1 Per-user intervention tolerance

Maintain tolerance_profile:

preferred modalities

preferred frequency

preferred timing (between phrases only vs okay mid-phrase)

preferred tone (coaching vs minimal)

Update rule:

friction → reduce tolerance

voluntary engagement → increase tolerance slowly

8.2 Per-context profiles

A single user may want different behavior in different contexts:

late-night noodling vs morning practice

headphones vs speaker

backing track on vs off

Store profiles keyed by context features (lightweight).

9) Concrete Misread Scenarios + Expected Behavior
Scenario A: System thinks Practice; user is Performing

Observed friction

ignore streak + continuous play
Response

immediate backoff to L3 or L4

no more real-time prompts

optional post-performance summary only if user opens it

Scenario B: System offers suggestions during Exploration and uses corrective tone

Observed

dismiss + pause
Response

tone repair + switch to invitation framing

reduce frequency, suggestions only after longer pauses

prefer call-and-response audio instead of text

Scenario C: System is right (Practice) but too nitpicky

Observed

user continues drilling but ignores feedback
Response

keep Practice mode internally, but reduce feedback granularity:

phrase-level summary every 20–30s

one “highest leverage” note, not many

Scenario D: Misread causes the user to stop playing

Observed

stop within 1s after prompt
Response

immediate L4 (silent monitor) for at least 2 minutes

after restart, minimal “ready when you are” behavior only

10) Formal Policy Table
Misread Signal	Misread Confidence	Immediate Action	Hold Time
Dismiss/mute	High	L3→L4	2–10 min
Stop-after-prompt	High	L4	2–5 min
Ignore streak ≥2	Med/High	L1→L2	1–3 min
UI avoidance + no engagement	Medium	L2	session-long
Error spike after cue	Medium	reduce granularity	1–2 min

Hold time prevents “nagging” re-entry.

11) Implementation Skeleton (Pseudocode)
state MODE ∈ {NEUTRAL, PRACTICE, PERFORMANCE, EXPLORATION}
state BACKOFF ∈ {L0, L1, L2, L3, L4}
state hold_backoff_timer

loop:
  MODE = infer_mode_soft()
  μ = infer_misread_confidence()

  if user_explicit_quiet:
     BACKOFF = L4
     hold_backoff_timer = long

  else if μ >= 0.65:
     BACKOFF = min(L4, BACKOFF + 2)  // jump up
     hold_backoff_timer = set_hold(BACKOFF)

  else if μ >= 0.45:
     BACKOFF = min(L4, BACKOFF + 1)
     hold_backoff_timer = set_hold(BACKOFF)

  else if hold_backoff_timer > 0:
     hold_backoff_timer -= dt
     // keep backoff

  else:
     // cautious recovery
     if positive_engagement_sustained():
        BACKOFF = max(L0, BACKOFF - 1)
        hold_backoff_timer = set_hold(BACKOFF)

  G = mode_policy(MODE)
  G = apply_backoff(G, BACKOFF)
  G = apply_tone_rules(G, MODE, BACKOFF)

  execute(G)

12) The UX Outcome You’re Engineering

A graceful misread system feels like:

It gets out of the way fast

It doesn’t argue

It doesn’t punish silence

It adapts without drama

It earns permission to help

That’s the whole point: when it’s wrong, it becomes quieter, kinder, and more optional—immediately.

If you want to continue formalizing, the next best artifact is a backoff policy matrix that maps (MODE × BACKOFF) into exact parameter values (frequency, modality weights, minimum pause length, interrupt budget).

If you want to continue formalizing, the next best artifact is a **backoff policy matrix** that maps `(MODE × BACKOFF)` into exact parameter values (frequency, modality weights, minimum pause length, interrupt budget).

create the backoff policy matrix
Backoff Policy Matrix

Maps (MODE × BACKOFF) → concrete Guidance Policy parameters.

This matrix controls how intrusive the Smart Guitar is at any moment. It assumes you already have:

MODE ∈ {NEUTRAL, PRACTICE, PERFORMANCE, EXPLORATION}

BACKOFF ∈ {L0, L1, L2, L3, L4} where L4 = silent monitor

1) Policy Parameters (the “knobs”)

Each cell in the matrix outputs a GuidancePolicy:

Core intervention controls

interrupt_budget_per_min (IB): max initiated interventions per minute (0+).

min_pause_ms (MP): minimum silence gap required before initiating anything.

between_phrase_only (BPO): if true, system may only intervene at phrase boundaries.

real_time_enabled (RTE): if false, no real-time interventions (summary only).

Feedback packaging

granularity (G): {none, summary, phrase, micro}

micro = targeted single cue (e.g., one timing hint), not multi-point critique

max_cues_per_intervention (MC): cap on how many distinct points per “moment”.

Modality weights (must sum to 1.0)

modality_weights (MW): {haptic, visual, audio, text}

“text” includes on-screen coaching language

“audio” includes call-and-response, pulse, brief earcons

“visual” includes lights, fret hints, overlays

“haptic” includes subtle pulses

Tone and phrasing style

tone (T): {silent, supportive, suggestive, instructive}

supportive: affirming/neutral, no correction

suggestive: invitations (“try…”)

instructive: direct coaching steps

Assist allowances (UX-safe “helpers”)

assist (A): toggles for non-verbal support that doesn’t feel like correction

tempo_stabilization (TS)

phrase_boundary_marking (PBM)

call_response (CR)

post_session_recap (PSR)

2) Global Rules Applied After the Matrix

These are enforced regardless of the cell:

Never interrupt mid-note.

If BACKOFF ≥ L2, then BPO = true (only safe windows).

If MODE = PERFORMANCE, then G != micro (no real-time critique).

If user explicitly requests silence, force BACKOFF = L4 immediately.

If ignore_streak ≥ 3, clamp IB ≤ 1 and increase MP by +1000ms.

3) Base Mode Policies at L0 (No Backoff)

These define the “ideal” behavior before de-escalation.

L0 Baselines

NEUTRAL-L0: gentle, low frequency, exploratory-friendly

PRACTICE-L0: pattern-based coaching, still phrase-respecting

PERFORMANCE-L0: silent by default, supportive-only

EXPLORATION-L0: inspiring, non-judgmental, low frequency

4) Backoff Levels (What Each Level Means)

L0 Normal: mode policy as intended

L1 Softer: fewer interventions + stricter timing windows

L2 Low-friction: modality shifts away from text/audio toward subtle cues; no critique language

L3 Summary-only: no real-time; optional recap only

L4 Silent monitor: no initiation; respond only to explicit user request

5) The Backoff Policy Matrix

Each cell is:
IB | MP | BPO | RTE | G | MC | MW(h/v/a/t) | T | A(TS/PBM/CR/PSR)

Modality weights are listed as (haptic, visual, audio, text).

A) MODE = NEUTRAL
BACKOFF	Policy
L0	`IB=1.0
L1	`IB=0.5
L2	`IB=0.3
L3	`IB=0.0
L4	`IB=0.0

Notes:

Neutral is “light touch.” Even at L0 it stays phrase-only and low budget.

B) MODE = PRACTICE
BACKOFF	Policy
L0	`IB=3.0
L1	`IB=1.5
L2	`IB=0.8
L3	`IB=0.0
L4	`IB=0.0

Notes:

Practice allows the highest IB at L0, but still pattern-based and phrase-only.

At L2 the tone shifts away from instructive to suggestive (reduces “nag”).

C) MODE = PERFORMANCE
BACKOFF	Policy
L0	`IB=0.2
L1	`IB=0.1
L2	`IB=0.0
L3	`IB=0.0
L4	`IB=0.0

Notes:

Performance never uses instructive tone.

At L2, the only allowed “active” behavior is non-verbal assist (e.g., gentle tempo stabilization), but no prompts.

D) MODE = EXPLORATION
BACKOFF	Policy
L0	`IB=1.2
L1	`IB=0.7
L2	`IB=0.4
L3	`IB=0.0
L4	`IB=0.0

Notes:

Exploration favors audio at L0 (call-and-response), but backoff rapidly reduces audio if friction appears.

Never uses corrective language at any backoff level.

6) How to Apply the Matrix in Code
Step 1: Choose the cell

Determine MODE from inference

Determine BACKOFF from misread detection/backoff ladder

Step 2: Emit policy

Pull the row values

Apply global clamps (silence gate, ignore streak clamp, performance constraints)

Step 3: Enforce budgets in real time

Track per-minute interventions:

If IB=1.2 → allow 1 intervention most minutes, 2 occasionally (stochastic rounding)

If IB=0.2 → allow 1 intervention every ~5 minutes at most

A simple implementable method:

Maintain token_bucket where tokens accrue at IB / 60 per second

Each intervention consumes 1 token

Tokens capped at 1–2 to prevent bursts

7) Quick Interpretation (What the Matrix “Feels Like”)

L0: the guitar behaves as a helpful companion appropriate to the mode

L1: still helpful, but quieter and better timed

L2: nearly silent; only subtle cues survive

L3: “tell me later” only

L4: “don’t speak unless spoken to”

8) Optional Extensions (if you want even more precision)

If you want to make it fully deterministic and testable, add:

min_seconds_between_interventions per cell (e.g., Practice-L0 = 10s, Exploration-L0 = 25s, Performance-L0 = 120s)

max_total_interventions_per_session caps

confidence multiplier: scale IB by mode confidence (e.g., IB *= clamp((conf-0.5)/0.3, 0, 1))


```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://stringmaster.example/smartguitar/guidance-policy.schema.json",
  "title": "Smart Guitar Guidance Policy (Mode × Backoff) + Runtime Engine Config",
  "type": "object",
  "additionalProperties": false,
  "required": ["version", "matrix", "runtime"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "matrix": {
      "description": "Policy matrix keyed by mode then backoff level.",
      "type": "object",
      "additionalProperties": false,
      "required": ["NEUTRAL", "PRACTICE", "PERFORMANCE", "EXPLORATION"],
      "properties": {
        "NEUTRAL": { "$ref": "#/$defs/backoffMap" },
        "PRACTICE": { "$ref": "#/$defs/backoffMap" },
        "PERFORMANCE": { "$ref": "#/$defs/backoffMap" },
        "EXPLORATION": { "$ref": "#/$defs/backoffMap" }
      }
    },
    "runtime": {
      "description": "Engine configuration used by the reference implementation.",
      "type": "object",
      "additionalProperties": false,
      "required": [
        "tokenBucket",
        "safeWindow",
        "globalRules",
        "modalityAvailability"
      ],
      "properties": {
        "tokenBucket": {
          "type": "object",
          "additionalProperties": false,
          "required": ["maxTokens", "stochasticRounding", "cooldownAfterInterventionMs"],
          "properties": {
            "maxTokens": { "type": "number", "minimum": 0, "maximum": 10 },
            "stochasticRounding": { "type": "boolean" },
            "cooldownAfterInterventionMs": { "type": "integer", "minimum": 0, "maximum": 600000 }
          }
        },
        "safeWindow": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "phraseBoundaryRequiredAtOrAboveBackoff",
            "minPauseMsByBackoff",
            "phraseBoundaryDebounceMs",
            "silenceGateExtraPauseMs"
          ],
          "properties": {
            "phraseBoundaryRequiredAtOrAboveBackoff": {
              "description": "If backoff >= this level, require phrase boundary gating even if policy says otherwise.",
              "type": "string",
              "enum": ["L0", "L1", "L2", "L3", "L4"]
            },
            "minPauseMsByBackoff": {
              "type": "object",
              "additionalProperties": false,
              "required": ["L0", "L1", "L2", "L3", "L4"],
              "properties": {
                "L0": { "type": "integer", "minimum": 0, "maximum": 10000 },
                "L1": { "type": "integer", "minimum": 0, "maximum": 10000 },
                "L2": { "type": "integer", "minimum": 0, "maximum": 10000 },
                "L3": { "type": "integer", "minimum": 0, "maximum": 10000 },
                "L4": { "type": "integer", "minimum": 0, "maximum": 10000 }
              }
            },
            "phraseBoundaryDebounceMs": {
              "description": "Minimum time after a detected phrase boundary before the system can initiate an intervention.",
              "type": "integer",
              "minimum": 0,
              "maximum": 5000
            },
            "silenceGateExtraPauseMs": {
              "description": "If silence preference is high or ignore streak is high, add this extra pause requirement.",
              "type": "integer",
              "minimum": 0,
              "maximum": 10000
            }
          }
        },
        "globalRules": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "performanceNeverInstructive",
            "performanceNoMicroGranularity",
            "backoffAtOrAboveL2ForcesBetweenPhraseOnly",
            "ignoreStreakClamp"
          ],
          "properties": {
            "performanceNeverInstructive": { "type": "boolean" },
            "performanceNoMicroGranularity": { "type": "boolean" },
            "backoffAtOrAboveL2ForcesBetweenPhraseOnly": { "type": "boolean" },
            "ignoreStreakClamp": {
              "type": "object",
              "additionalProperties": false,
              "required": ["ignoreStreakThreshold", "maxInterruptBudgetPerMin", "extraPauseMs"],
              "properties": {
                "ignoreStreakThreshold": { "type": "integer", "minimum": 1, "maximum": 20 },
                "maxInterruptBudgetPerMin": { "type": "number", "minimum": 0, "maximum": 10 },
                "extraPauseMs": { "type": "integer", "minimum": 0, "maximum": 10000 }
              }
            }
          }
        },
        "modalityAvailability": {
          "description": "Static availability of modalities on the device/build (can be overridden per-session in code).",
          "type": "object",
          "additionalProperties": false,
          "required": ["haptic", "visual", "audio", "text"],
          "properties": {
            "haptic": { "type": "boolean" },
            "visual": { "type": "boolean" },
            "audio": { "type": "boolean" },
            "text": { "type": "boolean" }
          }
        }
      }
    }
  },
  "$defs": {
    "backoffMap": {
      "type": "object",
      "additionalProperties": false,
      "required": ["L0", "L1", "L2", "L3", "L4"],
      "properties": {
        "L0": { "$ref": "#/$defs/guidancePolicy" },
        "L1": { "$ref": "#/$defs/guidancePolicy" },
        "L2": { "$ref": "#/$defs/guidancePolicy" },
        "L3": { "$ref": "#/$defs/guidancePolicy" },
        "L4": { "$ref": "#/$defs/guidancePolicy" }
      }
    },
    "guidancePolicy": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "interruptBudgetPerMin",
        "minPauseMs",
        "betweenPhraseOnly",
        "realTimeEnabled",
        "granularity",
        "maxCuesPerIntervention",
        "modalityWeights",
        "tone",
        "assist"
      ],
      "properties": {
        "interruptBudgetPerMin": { "type": "number", "minimum": 0, "maximum": 10 },
        "minPauseMs": {
          "description": "Policy-level pause threshold before initiating. Engine may further clamp/increase this.",
          "type": ["integer", "null"],
          "minimum": 0,
          "maximum": 20000
        },
        "betweenPhraseOnly": { "type": "boolean" },
        "realTimeEnabled": { "type": "boolean" },
        "granularity": { "type": "string", "enum": ["none", "summary", "phrase", "micro"] },
        "maxCuesPerIntervention": { "type": "integer", "minimum": 0, "maximum": 10 },
        "modalityWeights": {
          "type": "object",
          "additionalProperties": false,
          "required": ["haptic", "visual", "audio", "text"],
          "properties": {
            "haptic": { "type": "number", "minimum": 0, "maximum": 1 },
            "visual": { "type": "number", "minimum": 0, "maximum": 1 },
            "audio": { "type": "number", "minimum": 0, "maximum": 1 },
            "text": { "type": "number", "minimum": 0, "maximum": 1 }
          }
        },
        "tone": { "type": "string", "enum": ["silent", "supportive", "suggestive", "instructive"] },
        "assist": {
          "type": "object",
          "additionalProperties": false,
          "required": ["tempoStabilization", "phraseBoundaryMarking", "callResponse", "postSessionRecap"],
          "properties": {
            "tempoStabilization": { "type": "boolean" },
            "phraseBoundaryMarking": { "type": "boolean" },
            "callResponse": { "type": "boolean" },
            "postSessionRecap": { "type": "boolean" }
          }
        }
      },
      "allOf": [
        {
          "description": "Weights should sum to ~1.0 (schema can't enforce exact float sum reliably).",
          "properties": {}
        }
      ]
    }
  }
}
```

```ts
/**
 * Smart Guitar Guidance Engine
 * - Token bucket (interrupt budget)
 * - Safe-window gating (pause + phrase boundary)
 * - Modality selection (weighted + availability + backoff-aware)
 *
 * Drop-in: provide config (JSON validated against schema), feed it updates,
 * and call decide() each tick or when you consider initiating an intervention.
 */

type Mode = "NEUTRAL" | "PRACTICE" | "PERFORMANCE" | "EXPLORATION";
type Backoff = "L0" | "L1" | "L2" | "L3" | "L4";
type Granularity = "none" | "summary" | "phrase" | "micro";
type Tone = "silent" | "supportive" | "suggestive" | "instructive";
type Modality = "haptic" | "visual" | "audio" | "text";

export interface ModalityWeights {
  haptic: number;
  visual: number;
  audio: number;
  text: number;
}

export interface AssistFlags {
  tempoStabilization: boolean;
  phraseBoundaryMarking: boolean;
  callResponse: boolean;
  postSessionRecap: boolean;
}

export interface GuidancePolicy {
  interruptBudgetPerMin: number;          // IB
  minPauseMs: number | null;              // MP (policy-level; engine will clamp)
  betweenPhraseOnly: boolean;             // BPO
  realTimeEnabled: boolean;               // RTE
  granularity: Granularity;               // G
  maxCuesPerIntervention: number;         // MC
  modalityWeights: ModalityWeights;       // MW
  tone: Tone;                             // T
  assist: AssistFlags;                    // A
}

export interface PolicyConfig {
  version: string;
  matrix: Record<Mode, Record<Backoff, GuidancePolicy>>;
  runtime: {
    tokenBucket: {
      maxTokens: number;
      stochasticRounding: boolean;
      cooldownAfterInterventionMs: number;
    };
    safeWindow: {
      phraseBoundaryRequiredAtOrAboveBackoff: Backoff;
      minPauseMsByBackoff: Record<Backoff, number>;
      phraseBoundaryDebounceMs: number;
      silenceGateExtraPauseMs: number;
    };
    globalRules: {
      performanceNeverInstructive: boolean;
      performanceNoMicroGranularity: boolean;
      backoffAtOrAboveL2ForcesBetweenPhraseOnly: boolean;
      ignoreStreakClamp: {
        ignoreStreakThreshold: number;
        maxInterruptBudgetPerMin: number;
        extraPauseMs: number;
      };
    };
    modalityAvailability: Record<Modality, boolean>;
  };
}

/**
 * Real-time session signals needed for safe-window gating + clamps.
 * You can extend this without changing the engine interface by adding fields
 * and keeping the engine tolerant to unknown properties.
 */
export interface SessionSignals {
  nowMs: number;

  // Derived from note onsets / audio analysis
  timeSinceLastNoteOnMs: number; // 0 when currently playing notes, increases in pauses

  // Phrase boundary detector (your upstream logic decides this)
  phraseBoundaryDetected: boolean;
  timeSincePhraseBoundaryMs: number;

  // Player/system interaction friction
  ignoreStreak: number;            // consecutive ignored prompts/cues
  silencePreference: number;       // 0..1 (high = prefer silence)
  userExplicitQuiet: boolean;      // hard override

  // Optional: confidence of mode inference (0..1) to scale aggressiveness
  modeConfidence?: number;
}

/**
 * Output decision: whether to initiate something now, and if so how.
 * The engine does not generate the content; it selects constraints.
 */
export interface InterventionDecision {
  shouldInitiate: boolean;
  reason: string;

  mode: Mode;
  backoff: Backoff;

  policy: GuidancePolicy;          // effective policy after clamps
  modality?: Modality;             // chosen modality (if shouldInitiate)
  maxCues?: number;                // convenience alias
}

function backoffRank(b: Backoff): number {
  return { L0: 0, L1: 1, L2: 2, L3: 3, L4: 4 }[b];
}

function clamp01(x: number): number {
  if (x < 0) return 0;
  if (x > 1) return 1;
  return x;
}

function normalizeWeights(w: ModalityWeights, availability: Record<Modality, boolean>): ModalityWeights {
  const raw: Record<Modality, number> = {
    haptic: availability.haptic ? Math.max(0, w.haptic) : 0,
    visual: availability.visual ? Math.max(0, w.visual) : 0,
    audio: availability.audio ? Math.max(0, w.audio) : 0,
    text: availability.text ? Math.max(0, w.text) : 0,
  };

  const sum = raw.haptic + raw.visual + raw.audio + raw.text;
  if (sum <= 1e-9) {
    // Fallback: if nothing is available, all zeros
    return { haptic: 0, visual: 0, audio: 0, text: 0 };
  }
  return {
    haptic: raw.haptic / sum,
    visual: raw.visual / sum,
    audio: raw.audio / sum,
    text: raw.text / sum,
  };
}

/** Weighted random choice (or argmax if deterministic is desired). */
function pickModality(weights: ModalityWeights, rng: () => number): Modality | undefined {
  const entries: Array<[Modality, number]> = [
    ["haptic", weights.haptic],
    ["visual", weights.visual],
    ["audio", weights.audio],
    ["text", weights.text],
  ];
  const total = entries.reduce((a, [, w]) => a + w, 0);
  if (total <= 1e-9) return undefined;

  const r = rng() * total;
  let acc = 0;
  for (const [m, w] of entries) {
    acc += w;
    if (r <= acc && w > 0) return m;
  }
  return entries.find(([, w]) => w > 0)?.[0];
}

/** Token bucket that refills at IB tokens/min, consumes 1 token per intervention. */
class TokenBucket {
  private tokens: number;
  private lastRefillMs: number;
  private lastInterventionMs: number;

  constructor(private maxTokens: number) {
    this.tokens = maxTokens;
    this.lastRefillMs = 0;
    this.lastInterventionMs = -Infinity;
  }

  reset(nowMs: number, startFull = true) {
    this.tokens = startFull ? this.maxTokens : 0;
    this.lastRefillMs = nowMs;
    this.lastInterventionMs = -Infinity;
  }

  refill(nowMs: number, budgetPerMin: number) {
    if (this.lastRefillMs === 0) this.lastRefillMs = nowMs;
    const dtMs = Math.max(0, nowMs - this.lastRefillMs);
    this.lastRefillMs = nowMs;

    const ratePerMs = budgetPerMin / 60000;
    this.tokens = Math.min(this.maxTokens, this.tokens + dtMs * ratePerMs);
  }

  canSpend(nowMs: number, cooldownMs: number): boolean {
    if (nowMs - this.lastInterventionMs < cooldownMs) return false;
    return this.tokens >= 1;
  }

  spend(nowMs: number) {
    this.tokens = Math.max(0, this.tokens - 1);
    this.lastInterventionMs = nowMs;
  }

  getTokens(): number {
    return this.tokens;
  }
}

export class GuidanceEngine {
  private bucket: TokenBucket;
  private rng: () => number;

  constructor(private config: PolicyConfig, rng: () => number = Math.random) {
    this.bucket = new TokenBucket(config.runtime.tokenBucket.maxTokens);
    this.rng = rng;
  }

  startSession(nowMs: number) {
    this.bucket.reset(nowMs, true);
  }

  /**
   * Decide whether to initiate an intervention now.
   * - mode/backoff are your upstream outputs
   * - signals are derived from playing + UX friction
   */
  decide(mode: Mode, backoff: Backoff, signals: SessionSignals): InterventionDecision {
    // Hard stop: user demanded quiet
    if (signals.userExplicitQuiet) {
      const pol = this.effectivePolicy(mode, "L4", signals);
      return { shouldInitiate: false, reason: "explicit_quiet", mode, backoff: "L4", policy: pol };
    }

    // Get base policy cell
    const base = this.config.matrix[mode][backoff];
    const policy = this.effectivePolicy(mode, backoff, signals);

    // No real-time at L3/L4 or if policy disables it
    if (!policy.realTimeEnabled || policy.granularity === "none") {
      return { shouldInitiate: false, reason: "realtime_disabled_or_none", mode, backoff, policy };
    }

    // PERFORMANCE hard constraints (global)
    if (mode === "PERFORMANCE") {
      if (this.config.runtime.globalRules.performanceNeverInstructive && policy.tone === "instructive") {
        return { shouldInitiate: false, reason: "performance_tone_block", mode, backoff, policy };
      }
      if (this.config.runtime.globalRules.performanceNoMicroGranularity && policy.granularity === "micro") {
        return { shouldInitiate: false, reason: "performance_micro_block", mode, backoff, policy };
      }
    }

    // Safe-window gating: require pause and (often) phrase boundary
    const safe = this.isSafeWindow(mode, backoff, policy, signals);
    if (!safe.ok) {
      return { shouldInitiate: false, reason: safe.reason, mode, backoff, policy };
    }

    // Token bucket gating (interrupt budget)
    this.bucket.refill(signals.nowMs, policy.interruptBudgetPerMin);

    // Optional stochastic rounding: if budget is fractional, allow spending based on token fraction.
    // We implement this by allowing "virtual token" spend when tokens < 1 with probability = tokens.
    const cooldownMs = this.config.runtime.tokenBucket.cooldownAfterInterventionMs;
    if (!this.bucket.canSpend(signals.nowMs, cooldownMs)) {
      // Stochastic path if enabled and cooldown passed
      if (this.config.runtime.tokenBucket.stochasticRounding) {
        const tokens = this.bucket.getTokens();
        const inCooldown = false; // canSpend already includes cooldown; if false, could be cooldown or low tokens
        if (!inCooldown && tokens > 0 && tokens < 1) {
          const p = clamp01(tokens);
          if (this.rng() <= p) {
            // Spend the fractional tokens (set to 0) and allow
            this.forceSpendFractional(signals.nowMs);
            const modality = this.chooseModality(policy);
            if (!modality) return { shouldInitiate: false, reason: "no_modality_available", mode, backoff, policy };
            return { shouldInitiate: true, reason: "stochastic_budget", mode, backoff, policy, modality, maxCues: policy.maxCuesPerIntervention };
          }
        }
      }
      return { shouldInitiate: false, reason: "budget_or_cooldown", mode, backoff, policy };
    }

    // Choose modality
    const modality = this.chooseModality(policy);
    if (!modality) return { shouldInitiate: false, reason: "no_modality_available", mode, backoff, policy };

    // Spend a token and approve initiation
    this.bucket.spend(signals.nowMs);
    return {
      shouldInitiate: true,
      reason: "ok",
      mode,
      backoff,
      policy,
      modality,
      maxCues: policy.maxCuesPerIntervention,
    };
  }

  /** Call when you actually executed an intervention to keep timing consistent (optional if decide() always spends). */
  recordInterventionExecuted(nowMs: number) {
    // No-op currently; could be used if you want spending after execution rather than at decision time.
    void nowMs;
  }

  /** Compute effective policy after applying global clamps (ignore streak, silence preference, backoff forcing). */
  private effectivePolicy(mode: Mode, backoff: Backoff, signals: SessionSignals): GuidancePolicy {
    const base = structuredClone(this.config.matrix[mode][backoff]) as GuidancePolicy;

    // Normalize weights against availability
    base.modalityWeights = normalizeWeights(base.modalityWeights, this.config.runtime.modalityAvailability);

    // Global: backoff >= L2 forces between-phrase-only (if enabled)
    if (this.config.runtime.globalRules.backoffAtOrAboveL2ForcesBetweenPhraseOnly) {
      if (backoffRank(backoff) >= backoffRank("L2")) base.betweenPhraseOnly = true;
    }

    // Ignore streak clamp
    const clamp = this.config.runtime.globalRules.ignoreStreakClamp;
    if (signals.ignoreStreak >= clamp.ignoreStreakThreshold) {
      base.interruptBudgetPerMin = Math.min(base.interruptBudgetPerMin, clamp.maxInterruptBudgetPerMin);
      base.minPauseMs = (base.minPauseMs ?? 0) + clamp.extraPauseMs;
    }

    // Silence preference clamp (soft): increase pause + reduce budget progressively
    const sp = clamp01(signals.silencePreference);
    if (sp > 0.7) {
      base.interruptBudgetPerMin *= 0.25;
      base.minPauseMs = (base.minPauseMs ?? 0) + this.config.runtime.safeWindow.silenceGateExtraPauseMs;
      base.tone = base.tone === "instructive" ? "suggestive" : base.tone;
    } else if (sp > 0.4) {
      base.interruptBudgetPerMin *= 0.6;
      base.minPauseMs = (base.minPauseMs ?? 0) + Math.floor(this.config.runtime.safeWindow.silenceGateExtraPauseMs / 2);
    }

    // Optional: mode confidence scaling (conservative when uncertain)
    const conf = clamp01(signals.modeConfidence ?? 1);
    if (conf < 0.7) {
      // Scale down budget and push toward safer timing when uncertain
      const scale = Math.max(0, (conf - 0.4) / 0.3); // 0 at 0.4, 1 at 0.7+
      base.interruptBudgetPerMin *= clamp01(scale);
      base.minPauseMs = (base.minPauseMs ?? 0) + Math.floor((1 - scale) * 800);
    }

    // PERFORMANCE global constraints: no instructive tone, no micro (optional hardening)
    if (mode === "PERFORMANCE") {
      if (this.config.runtime.globalRules.performanceNeverInstructive && base.tone === "instructive") {
        base.tone = "supportive";
      }
      if (this.config.runtime.globalRules.performanceNoMicroGranularity && base.granularity === "micro") {
        base.granularity = "summary";
      }
      // Keep budget tiny
      base.interruptBudgetPerMin = Math.min(base.interruptBudgetPerMin, 0.5);
    }

    // Backoff L3/L4 override: no real-time
    if (backoff === "L3") {
      base.realTimeEnabled = false; // summary only
    }
    if (backoff === "L4") {
      base.realTimeEnabled = false;
      base.granularity = "none";
      base.interruptBudgetPerMin = 0;
      base.tone = "silent";
      base.modalityWeights = { haptic: 0, visual: 0, audio: 0, text: 0 };
    }

    return base;
  }

  /** Safe-window gating: pause + phrase boundary rules. */
  private isSafeWindow(mode: Mode, backoff: Backoff, policy: GuidancePolicy, signals: SessionSignals): { ok: boolean; reason: string } {
    // Must have a pause long enough
    const baseMinPause = policy.minPauseMs ?? 0;
    const backoffMinPause = this.config.runtime.safeWindow.minPauseMsByBackoff[backoff];
    const requiredPause = Math.max(baseMinPause, backoffMinPause);

    if (signals.timeSinceLastNoteOnMs < requiredPause) {
      return { ok: false, reason: "insufficient_pause" };
    }

    // Determine if phrase boundary is required
    const pbForceAt = this.config.runtime.safeWindow.phraseBoundaryRequiredAtOrAboveBackoff;
    const forced = backoffRank(backoff) >= backoffRank(pbForceAt);
    const requirePhraseBoundary = policy.betweenPhraseOnly || forced;

    if (requirePhraseBoundary) {
      if (!signals.phraseBoundaryDetected) return { ok: false, reason: "no_phrase_boundary" };

      // Debounce: avoid intervening immediately at boundary detection
      if (signals.timeSincePhraseBoundaryMs < this.config.runtime.safeWindow.phraseBoundaryDebounceMs) {
        return { ok: false, reason: "phrase_boundary_debounce" };
      }
    }

    // Special: PERFORMANCE should be extra conservative
    if (mode === "PERFORMANCE") {
      // Require longer pauses even if satisfied above
      if (signals.timeSinceLastNoteOnMs < Math.max(requiredPause, 2000)) return { ok: false, reason: "performance_extra_pause" };
    }

    return { ok: true, reason: "ok" };
  }

  /** Choose a modality based on normalized weights and availability. */
  private chooseModality(policy: GuidancePolicy): Modality | undefined {
    const w = normalizeWeights(policy.modalityWeights, this.config.runtime.modalityAvailability);
    return pickModality(w, this.rng);
  }

  /** Spend fractional tokens if using stochastic rounding. */
  private forceSpendFractional(nowMs: number) {
    // crude but effective: reduce bucket tokens to 0 by spending 1 if <1,
    // but we must avoid going negative; instead, just spend 1 and allow clamp inside.
    // Alternative: expose an internal spendFractional() on TokenBucket.
    (this.bucket as any).tokens = 0; // eslint-disable-line @typescript-eslint/no-explicit-any
    (this.bucket as any).lastInterventionMs = nowMs; // eslint-disable-line @typescript-eslint/no-explicit-any
  }
}

/* ---------------------------
   Example usage
-----------------------------

import configJson from "./policy.json";
import { GuidanceEngine } from "./GuidanceEngine";

const engine = new GuidanceEngine(configJson);
engine.startSession(Date.now());

function tick() {
  const mode: Mode = inferMode();          // your upstream inference
  const backoff: Backoff = inferBackoff(); // your misread/backoff ladder

  const signals: SessionSignals = {
    nowMs: Date.now(),
    timeSinceLastNoteOnMs: getPauseMs(),
    phraseBoundaryDetected: isPhraseBoundary(),
    timeSincePhraseBoundaryMs: getSincePhraseBoundaryMs(),
    ignoreStreak: getIgnoreStreak(),
    silencePreference: getSilencePreference(),
    userExplicitQuiet: getQuietToggle(),
    modeConfidence: getModeConfidence()
  };

  const decision = engine.decide(mode, backoff, signals);
  if (decision.shouldInitiate) {
    // Generate content elsewhere; this is just the envelope.
    initiateIntervention({
      modality: decision.modality!,
      tone: decision.policy.tone,
      granularity: decision.policy.granularity,
      maxCues: decision.maxCues!,
      assist: decision.policy.assist
    });
  }
}
*/
```


Next step: **define the teaching loop contract**—the smallest end-to-end slice where the agent can *listen → decide → coach → verify → adapt* for one narrow skill. Everything else (models, content, UI polish) hangs off that.

Here’s a concrete, integratable plan.

---

## 1) Pick one “vertical slice” skill (start narrow)

Choose **one** of these (all work well as first slices):

* **Timing & groove** (subdivision, rushing/dragging, locking to pulse)
* **Chord changes** (transition accuracy + rhythm)
* **Single-note phrase accuracy** (melody learning / riffs)
* **Strumming consistency** (pattern + dynamics)

Timing/groove is usually the best first slice because you can give valuable feedback with simpler inference.

---

## 2) Define the Teaching Loop Contract (API + state)

You want an agent that can run this loop repeatedly:

### Inputs

* `performance_events`: note onsets, durations, velocities/attack proxies, string/fret if available
* `context`: skill target, difficulty, tempo, backing track/metronome state
* `user_state`: mode (practice/performance/exploration), backoff level, silence preference

### Outputs

* `next_action`: coach now vs wait
* `feedback_envelope`: modality + tone + granularity (using your policy engine)
* `task_update`: keep target / simplify / increase challenge
* `verification_request`: what measurement confirms progress (e.g., “play it 3 times at 80bpm”)

### State

* rolling estimates: timing drift, stability, error patterns
* last interventions + whether user engaged
* current step in lesson progression

If you write this contract first, your implementation becomes modular instead of monolithic.

---

## 3) Build the “Assessment → Prescription” kernel (the brain)

For the chosen skill, define:

### A. Assessment metrics (objective, computed every phrase)

Example for timing:

* `mean_offset_ms` vs beat grid
* `variance_offset_ms`
* `late_rate` / `early_rate`
* `recovery_time` after a mistake
* `stability_score` (0–1)

### B. Prescription rules (what to do next)

A small ruleset is enough to start:

* If stability low → reduce tempo or simplify rhythm
* If consistently late → change cue style (subdivision pulses) + prompt “anticipate”
* If improvement plateau → switch exercise, not more feedback

This is what makes it “agentic”: it **chooses the next best step**, not just critiques.

---

## 4) Author the first 20 micro-exercises (content, not “lessons”)

These should be tiny, measurable, and remixable:

For timing/groove:

* clap/strum quarter notes at 60–90 bpm
* eighth-note downstrokes
* two-bar rhythm with rests
* syncopation starter
* call-and-response rhythm mimic

Each exercise has:

* target tempo range
* success criteria (e.g., 80% notes within ±25ms)
* escalation path (faster, longer, add syncopation)
* fallback path (slower, fewer events)

---

## 5) Implement verification and progression (so it feels like teaching)

Define simple gates:

* **Pass:** meets criteria 2 out of last 3 takes
* **Almost:** meets criteria but high variance → repeat once
* **Fail:** simplify or slow down automatically

Progression is how users feel coached instead of judged.

---

## 6) Wire it into your backoff + safe-window engine

This is key: the “teacher brain” proposes feedback, but your **policy engine decides if/when/how**.

Pipeline:

1. Skill module produces `coach_intent` (e.g., “timing cue needed”)
2. Policy engine returns envelope (or “don’t speak”)
3. Renderer delivers feedback via selected modality

This keeps UX consistent and prevents nagging.

---

## 7) Instrumentation you need immediately (to iterate fast)

Track these from day one:

* prompt dismissed rate
* ignore streaks
* stop-after-prompt rate
* time-to-improvement per exercise
* completion rate per exercise
* user-initiated “help me” events

This tells you whether teaching is working *without asking surveys constantly*.

---

## A very practical “next week” deliverable

Build one vertical slice:

* **Timing Coach v0**

  * listens to 2-bar strum exercise
  * computes timing stability
  * gives one cue per phrase max
  * adapts tempo up/down
  * uses your backoff matrix to stay respectful

Once that’s solid, you can add more skills as plug-ins.

---

If you tell me which first skill you want (timing, chord changes, riffs, strumming), I’ll draft the **exact Teaching Loop Contract** (JSON event schema + success criteria + exercise definitions + prescription rules) for that slice.



Next step: **define the teaching loop contract**—the smallest end-to-end slice where the agent can *listen → decide → coach → verify → adapt* for one narrow skill. Everything else (models, content, UI polish) hangs off that.

Here’s a concrete, integratable plan.

---

## 1) Pick one “vertical slice” skill (start narrow)

Choose **one** of these (all work well as first slices):

* **Timing & groove** (subdivision, rushing/dragging, locking to pulse)
* **Chord changes** (transition accuracy + rhythm)
* **Single-note phrase accuracy** (melody learning / riffs)
* **Strumming consistency** (pattern + dynamics)

Timing/groove is usually the best first slice because you can give valuable feedback with simpler inference.

---

## 2) Define the Teaching Loop Contract (API + state)

You want an agent that can run this loop repeatedly:

### Inputs

* `performance_events`: note onsets, durations, velocities/attack proxies, string/fret if available
* `context`: skill target, difficulty, tempo, backing track/metronome state
* `user_state`: mode (practice/performance/exploration), backoff level, silence preference

### Outputs

* `next_action`: coach now vs wait
* `feedback_envelope`: modality + tone + granularity (using your policy engine)
* `task_update`: keep target / simplify / increase challenge
* `verification_request`: what measurement confirms progress (e.g., “play it 3 times at 80bpm”)

### State

* rolling estimates: timing drift, stability, error patterns
* last interventions + whether user engaged
* current step in lesson progression

If you write this contract first, your implementation becomes modular instead of monolithic.

---

## 3) Build the “Assessment → Prescription” kernel (the brain)

For the chosen skill, define:

### A. Assessment metrics (objective, computed every phrase)

Example for timing:

* `mean_offset_ms` vs beat grid
* `variance_offset_ms`
* `late_rate` / `early_rate`
* `recovery_time` after a mistake
* `stability_score` (0–1)

### B. Prescription rules (what to do next)

A small ruleset is enough to start:

* If stability low → reduce tempo or simplify rhythm
* If consistently late → change cue style (subdivision pulses) + prompt “anticipate”
* If improvement plateau → switch exercise, not more feedback

This is what makes it “agentic”: it **chooses the next best step**, not just critiques.

---

## 4) Author the first 20 micro-exercises (content, not “lessons”)

These should be tiny, measurable, and remixable:

For timing/groove:

* clap/strum quarter notes at 60–90 bpm
* eighth-note downstrokes
* two-bar rhythm with rests
* syncopation starter
* call-and-response rhythm mimic

Each exercise has:

* target tempo range
* success criteria (e.g., 80% notes within ±25ms)
* escalation path (faster, longer, add syncopation)
* fallback path (slower, fewer events)

---

## 5) Implement verification and progression (so it feels like teaching)

Define simple gates:

* **Pass:** meets criteria 2 out of last 3 takes
* **Almost:** meets criteria but high variance → repeat once
* **Fail:** simplify or slow down automatically

Progression is how users feel coached instead of judged.

---

## 6) Wire it into your backoff + safe-window engine

This is key: the “teacher brain” proposes feedback, but your **policy engine decides if/when/how**.

Pipeline:

1. Skill module produces `coach_intent` (e.g., “timing cue needed”)
2. Policy engine returns envelope (or “don’t speak”)
3. Renderer delivers feedback via selected modality

This keeps UX consistent and prevents nagging.

---

## 7) Instrumentation you need immediately (to iterate fast)

Track these from day one:

* prompt dismissed rate
* ignore streaks
* stop-after-prompt rate
* time-to-improvement per exercise
* completion rate per exercise
* user-initiated “help me” events

This tells you whether teaching is working *without asking surveys constantly*.

---

## A very practical “next week” deliverable

Build one vertical slice:

* **Timing Coach v0**

  * listens to 2-bar strum exercise
  * computes timing stability
  * gives one cue per phrase max
  * adapts tempo up/down
  * uses your backoff matrix to stay respectful

Once that’s solid, you can add more skills as plug-ins.

---

If you tell me which first skill you want (timing, chord changes, riffs, strumming), I’ll draft the **exact Teaching Loop Contract** (JSON event schema + success criteria + exercise definitions + prescription rules) for that slice.



Below is a concrete spec for a **“listens to a 2-bar strum exercise”** teaching slice: what the system listens for, how it scores a take, and how it decides the next coaching action. This is designed to plug directly into your **policy engine** (mode/backoff/safe-window) and into an upstream audio/MIDI/event extractor.

---

## 1) What the 2-bar strum exercise is

**Definition:** The player strums a repeating 2-bar pattern at a target tempo with a known meter (usually **4/4**).
The coach is evaluating **timing + rhythm adherence**, not chord correctness.

**Exercise examples**

* Eighth-note downstrokes for 2 bars (16 strums)
* Down-up eighths for 2 bars (16 strums)
* Simple syncopation: `D - D U - U D U` (2 bars)

---

## 2) Teaching Loop Contract (messages + state)

### 2.1 Event input schema (from the “listener”)

This is what your audio-to-events layer should emit. If you already have a different event format, map into this.

```json
{
  "type": "StrumEvent",
  "t_ms": 1234567,
  "direction": "down",
  "string_mask": [true,true,true,true,true,true],
  "intensity": 0.62,
  "is_mute": false,
  "confidence": 0.84
}
```

**Fields**

* `t_ms`: timestamp (ms)
* `direction`: `"down" | "up" | "unknown"` (unknown allowed)
* `string_mask`: which strings sounded (optional; can be empty if not available)
* `intensity`: 0..1 (proxy for dynamics/attack)
* `is_mute`: palm mute / dead strum detection (optional)
* `confidence`: detection confidence 0..1

### 2.2 Exercise context schema

```json
{
  "type": "StrumExerciseContext",
  "exercise_id": "2bar_eighth_down",
  "meter": "4/4",
  "bars": 2,
  "bpm_target": 80,
  "bpm_tolerance": 6,
  "pattern": {
    "subdivision": "8n",
    "expected_hits": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    "directions": ["down","down","down","down","down","down","down","down","down","down","down","down","down","down","down","down"]
  },
  "count_in_beats": 2,
  "swing": 0.0
}
```

**Notes**

* `expected_hits` are indices on a 2-bar grid (0–15 for 8ths in 4/4×2 bars)
* You can support other grids: 16ths → 0–31, quarters → 0–7, etc.

### 2.3 Output decision schema (from the coach)

```json
{
  "type": "CoachDecision",
  "action": "coach_now",
  "feedback_intent": "timing_stability",
  "priority": "high",
  "suggestion": {
    "cue": "subdivision_pulse",
    "content_key": "aim_for_center_of_click",
    "single_point": true
  },
  "verification": {
    "next_take": "repeat_same",
    "bpm_next": 76,
    "goal": "80% hits within ±30ms for 2 takes"
  }
}
```

* The coach provides **intent** and **one bite-size cue**.
* Your policy engine decides *whether/when/how* to deliver it.

---

## 3) How the system “listens”: alignment and scoring

### 3.1 Build the timing grid

Given `bpm_target`, `meter`, `bars`, `subdivision`:

* Beat duration: `beat_ms = 60000 / bpm`
* For 8ths: `slot_ms = beat_ms / 2`
* Grid slots for 2 bars of 4/4 at 8ths: `16` slots

Grid timepoints:
`grid[k] = start_ms + count_in_ms + k * slot_ms`

Where:

* `start_ms` is the session take start
* `count_in_ms` = `count_in_beats * beat_ms`

### 3.2 Match strums to grid slots

For each expected slot `k`, find the nearest `StrumEvent` in a window:

* Window recommended: `±0.35 * slot_ms` (wide enough for beginners)

A slot is:

* `hit` if a strum event exists in the window
* `miss` if none
* `extra` if there are strums not assigned to any slot

### 3.3 Compute metrics (per take)

**A) Timing offset distribution**
For each hit:
`offset_ms[k] = event_t_ms - grid[k]`

Metrics:

* `mean_offset_ms`
* `median_offset_ms` (more robust)
* `std_offset_ms`
* `p90_abs_offset_ms`

**B) Accuracy**

* `hit_rate = hits / expected_slots`
* `miss_rate = misses / expected_slots`
* `extra_rate = extras / expected_slots`

**C) Stability score (0..1)**
A simple formulation:

* `timing_quality = clamp(1 - (p90_abs_offset_ms / 80), 0, 1)`
* `coverage_quality = clamp(hit_rate, 0, 1)`
* `extra_penalty = clamp(1 - extra_rate, 0, 1)`
* `stability = 0.55*timing_quality + 0.35*coverage_quality + 0.10*extra_penalty`

**D) Drift (rushing/dragging inside the take)**
Compute offset trend across slots:

* Fit a line `offset_ms ~ k`
* `drift_ms_per_bar` derived from slope

Interpretation:

* Positive drift → getting later (dragging)
* Negative drift → getting earlier (rushing)

**E) Dynamics consistency (optional)**

* `intensity_cv = std(intensity)/mean(intensity)`
  High CV may indicate tense or inconsistent motion (use carefully; don’t shame the user)

---

## 4) Success criteria (pass/almost/fail)

Define thresholds per difficulty level.

### Beginner default

* **Pass**

  * `hit_rate ≥ 0.85`
  * `p90_abs_offset_ms ≤ 45`
  * `extra_rate ≤ 0.10`
  * AND achieved in **2 of last 3 takes**
* **Almost**

  * `hit_rate ≥ 0.75` and `p90_abs_offset_ms ≤ 65`
* **Fail**

  * Anything worse than Almost

### Progression targets (as difficulty increases)

* tighten p90 threshold: 45 → 35 → 25ms
* require 3 consecutive passes
* add pattern complexity (rests/syncopation)

---

## 5) Prescription rules (what to coach next)

The coach chooses **one** highest leverage intervention per take.

### 5.1 Error classification

* **Coverage problem**: low hit_rate or high miss_rate
* **Timing spread problem**: p90_abs_offset high but hit_rate okay
* **Drift problem**: drift_ms_per_bar large magnitude
* **Extras problem**: extra_rate high (often over-excited strumming)
* **Pattern adherence problem**: direction mismatch (if tracked) or rhythmic shape mismatch

### 5.2 Rule table (single-point coaching)

**If Fail due to coverage**

* Action: reduce tempo by 5–10 bpm
* Cue: “lock in fewer, clearer hits”
* Feedback intent: `simplify_and_anchor`
* Verification: 1 take at reduced tempo

**If hit_rate ok but timing spread high**

* Action: keep tempo, add subdivision support
* Cue: `subdivision_pulse` (haptic/light) *between phrases*
* Verification: aim p90 under threshold for next take

**If drift is main issue**

* Action: introduce “anchor beats” (emphasize beats 2 and 4)
* Cue: `backbeat_anchor`
* Verification: drift magnitude decreases next take

**If extra strums high**

* Action: reduce feedback, encourage space
* Cue: `reduce_motion` / “smaller strum”
* Verification: extra_rate < 0.10

**If direction mismatch (optional)**

* Action: switch to visual-only (less intrusive)
* Cue: show down/up guide briefly before take
* Verification: direction match improves

### 5.3 Escalation and fallback

* If user improves 2 takes in a row → raise tempo by 2–4 bpm
* If user fails 2 takes in a row → reduce tempo or simplify pattern
* If misread/friction signals rise → push backoff up and switch to summary-only

---

## 6) Safe-window gating (so it feels musical)

Even in practice mode, the coach should only initiate at:

* phrase boundary OR
* pause > min_pause_ms OR
* after the take ends

For this exercise, the cleanest trigger is:

* **after bar 2 ends** (take complete), then coach.

If you want occasional in-take cues (advanced):

* only allow non-verbal pulses aligned to grid, no commentary

---

## 7) Modality selection (plug into your weights)

The coach doesn’t pick modality; it picks **cue type** and leaves delivery to the policy engine.

### Cue types for this exercise

* `count_in` (audio or visual)
* `subdivision_pulse` (haptic/visual)
* `backbeat_anchor` (audio/haptic)
* `take_summary` (visual/text)
* `demo_playback` (audio)

Map cue types to acceptable modalities, then apply the weighted chooser:

* `subdivision_pulse`: haptic/visual preferred
* `take_summary`: visual/text
* `demo_playback`: audio

If chosen modality unavailable, fall back by preference order.

---

## 8) Minimal reference implementation (TypeScript)

This is a compact, integratable core: aligns events to a grid and returns metrics + a suggested coaching intent.

```ts
type StrumDirection = "down" | "up" | "unknown";

export interface StrumEvent {
  t_ms: number;
  direction: StrumDirection;
  intensity?: number;     // 0..1
  confidence?: number;    // 0..1
}

export type Subdivision = "4n" | "8n" | "16n";

export interface StrumPattern {
  subdivision: Subdivision;
  expected_hits: number[];          // indices on grid
  directions?: StrumDirection[];    // optional, same length as expected_hits
}

export interface StrumExerciseContext {
  meter: "4/4" | "3/4" | "6/8";
  bars: number;                 // 2
  bpm_target: number;
  count_in_beats: number;        // e.g., 2
  pattern: StrumPattern;
  swing?: number;                // 0..1, optional
}

export interface TakeMetrics {
  hit_rate: number;
  miss_rate: number;
  extra_rate: number;

  mean_offset_ms: number;
  median_offset_ms: number;
  std_offset_ms: number;
  p90_abs_offset_ms: number;

  drift_ms_per_bar: number;
  stability: number;

  matched: Array<{ slot: number; event?: StrumEvent; offset_ms?: number }>;
  extras: StrumEvent[];
}

function median(xs: number[]): number {
  if (xs.length === 0) return 0;
  const a = [...xs].sort((x, y) => x - y);
  const mid = Math.floor(a.length / 2);
  return a.length % 2 ? a[mid] : (a[mid - 1] + a[mid]) / 2;
}

function mean(xs: number[]): number {
  return xs.length ? xs.reduce((s, x) => s + x, 0) / xs.length : 0;
}

function std(xs: number[]): number {
  if (xs.length < 2) return 0;
  const m = mean(xs);
  const v = xs.reduce((s, x) => s + (x - m) * (x - m), 0) / (xs.length - 1);
  return Math.sqrt(v);
}

function percentileAbs(xs: number[], p: number): number {
  if (!xs.length) return 0;
  const a = xs.map(Math.abs).sort((x, y) => x - y);
  const idx = Math.min(a.length - 1, Math.max(0, Math.floor(p * (a.length - 1))));
  return a[idx];
}

/** Simple linear regression slope of y ~ x for x = 0..n-1 */
function slope(y: number[]): number {
  const n = y.length;
  if (n < 2) return 0;
  const xs = [...Array(n)].map((_, i) => i);
  const xbar = mean(xs);
  const ybar = mean(y);
  let num = 0, den = 0;
  for (let i = 0; i < n; i++) {
    num += (xs[i] - xbar) * (y[i] - ybar);
    den += (xs[i] - xbar) * (xs[i] - xbar);
  }
  return den === 0 ? 0 : num / den;
}

function subdivisionSlotsPerBeat(sub: Subdivision): number {
  if (sub === "4n") return 1;
  if (sub === "8n") return 2;
  return 4; // 16n
}

export function analyzeTwoBarTake(
  events: StrumEvent[],
  ctx: StrumExerciseContext,
  takeStartMs: number
): TakeMetrics {
  const beatMs = 60000 / ctx.bpm_target;
  const slotsPerBeat = subdivisionSlotsPerBeat(ctx.pattern.subdivision);

  // For 4/4, beatsPerBar = 4; extend if you support other meters
  const beatsPerBar = ctx.meter === "3/4" ? 3 : (ctx.meter === "6/8" ? 2 : 4);
  const totalBeats = beatsPerBar * ctx.bars;
  const totalSlots = totalBeats * slotsPerBeat;

  const slotMs = beatMs / slotsPerBeat;
  const countInMs = ctx.count_in_beats * beatMs;

  const grid: number[] = [];
  for (let k = 0; k < totalSlots; k++) {
    grid.push(takeStartMs + countInMs + k * slotMs);
  }

  // Matching window: ±0.35*slotMs
  const win = 0.35 * slotMs;

  // Track which events are used
  const used = new Array(events.length).fill(false);

  const matched: Array<{ slot: number; event?: StrumEvent; offset_ms?: number }> = [];
  const offsets: number[] = [];

  for (const slot of ctx.pattern.expected_hits) {
    const t0 = grid[slot];
    let bestIdx = -1;
    let bestAbs = Infinity;

    for (let i = 0; i < events.length; i++) {
      if (used[i]) continue;
      const dt = events[i].t_ms - t0;
      const adt = Math.abs(dt);
      if (adt <= win && adt < bestAbs) {
        bestAbs = adt;
        bestIdx = i;
      }
    }

    if (bestIdx >= 0) {
      used[bestIdx] = true;
      const off = events[bestIdx].t_ms - t0;
      matched.push({ slot, event: events[bestIdx], offset_ms: off });
      offsets.push(off);
    } else {
      matched.push({ slot });
    }
  }

  const extras = events.filter((_, i) => !used[i]);

  const hits = offsets.length;
  const expected = ctx.pattern.expected_hits.length;
  const misses = expected - hits;

  const hit_rate = expected ? hits / expected : 0;
  const miss_rate = expected ? misses / expected : 0;
  const extra_rate = expected ? extras.length / expected : 0;

  const mean_offset_ms = mean(offsets);
  const median_offset_ms = median(offsets);
  const std_offset_ms = std(offsets);
  const p90_abs_offset_ms = percentileAbs(offsets, 0.90);

  // Drift: regression slope of offsets across expected hit order
  const driftSlope = slope(offsets); // ms per hit-index step
  const hitsPerBar = expected / ctx.bars;
  const drift_ms_per_bar = driftSlope * hitsPerBar;

  // Stability
  const timing_quality = Math.max(0, Math.min(1, 1 - p90_abs_offset_ms / 80));
  const coverage_quality = Math.max(0, Math.min(1, hit_rate));
  const extra_penalty = Math.max(0, Math.min(1, 1 - extra_rate));
  const stability = 0.55 * timing_quality + 0.35 * coverage_quality + 0.10 * extra_penalty;

  return {
    hit_rate,
    miss_rate,
    extra_rate,
    mean_offset_ms,
    median_offset_ms,
    std_offset_ms,
    p90_abs_offset_ms,
    drift_ms_per_bar,
    stability,
    matched,
    extras
  };
}

/** Convert metrics into a single coaching intent + suggested adjustment. */
export function prescribeNextStep(metrics: TakeMetrics) {
  // Thresholds (tune per level)
  const PASS_hit = 0.85;
  const PASS_p90 = 45;
  const ALMOST_hit = 0.75;
  const ALMOST_p90 = 65;

  const pass = metrics.hit_rate >= PASS_hit && metrics.p90_abs_offset_ms <= PASS_p90 && metrics.extra_rate <= 0.10;
  const almost = metrics.hit_rate >= ALMOST_hit && metrics.p90_abs_offset_ms <= ALMOST_p90;

  // Classify primary issue
  const coverageBad = metrics.hit_rate < ALMOST_hit || metrics.miss_rate > 0.25;
  const timingSpreadBad = metrics.hit_rate >= ALMOST_hit && metrics.p90_abs_offset_ms > PASS_p90;
  const driftBad = Math.abs(metrics.drift_ms_per_bar) > 30; // tune
  const extrasBad = metrics.extra_rate > 0.15;

  if (pass) {
    return { outcome: "pass" as const, intent: "raise_challenge", bpm_delta: +3, cue: "praise_then_increment" };
  }

  if (!almost) {
    if (coverageBad) return { outcome: "fail" as const, intent: "simplify_and_anchor", bpm_delta: -6, cue: "fewer_clear_hits" };
    if (extrasBad) return { outcome: "fail" as const, intent: "reduce_motion", bpm_delta: -3, cue: "smaller_strum_more_space" };
    return { outcome: "fail" as const, intent: "subdivision_support", bpm_delta: -4, cue: "add_pulse_then_repeat" };
  }

  // Almost
  if (driftBad) return { outcome: "almost" as const, intent: "backbeat_anchor", bpm_delta: -2, cue: "emphasize_2_and_4" };
  if (timingSpreadBad) return { outcome: "almost" as const, intent: "subdivision_support", bpm_delta: 0, cue: "aim_center_of_click" };
  if (extrasBad) return { outcome: "almost" as const, intent: "reduce_motion", bpm_delta: 0, cue: "keep_hand_small" };

  return { outcome: "almost" as const, intent: "repeat_once", bpm_delta: 0, cue: "one_more_take" };
}
```

---

## 9) How this plugs into your policy engine

Your “teacher” produces:

* `feedback_intent` (e.g., `subdivision_support`)
* `cue` (e.g., `add_pulse_then_repeat`)
* `verification` (repeat at bpm_next)

Then your **policy engine** decides:

* should initiate now?
* which modality? (haptic/visual/audio/text)
* how intrusive? (based on mode/backoff/safe-window)

So the integration flow looks like:

1. Capture 2-bar take events → `analyzeTwoBarTake()`
2. Convert to prescription → `prescribeNextStep()`
3. Wrap into `CoachDecision`
4. Ask policy engine for envelope (may return “don’t speak”)
5. Deliver cue with chosen modality
6. Run next take

---

## 10) Next step from here (the very next thing to implement)

Build the upstream pieces that make “listening” work reliably:

1. **Take segmentation**

   * detect when a take starts (count-in begins) and ends (2 bars complete)
2. **Phrase boundary detector**

   * for safe-window gating outside the exercise
3. **Event extractor**

   * stable strum onset detection
   * optional direction inference

If you want, I can provide a **take segmenter spec** next (with edge cases like late starts, missed count-in, or extra bars) and the **exact event contracts** between segmenter → analyzer → coach → policy engine.



Below is a full **Take Segmenter spec** for a 2-bar strum exercise and the **exact event contracts** between:

**Segmenter → Analyzer → Coach → Policy Engine → Renderer**

It’s written to be implementable as a state machine with clear timing rules and edge-case handling.

---

# 1) System Overview and Responsibilities

## Components

1. **Segmenter**: turns a raw stream of strum-ish events into discrete “takes” aligned to the exercise (count-in + 2 bars).
2. **Analyzer**: aligns events to grid slots, computes metrics (hit rate, offsets, drift, stability).
3. **Coach**: selects a single coaching intent + a next-step plan (tempo change, repeat, simplify).
4. **Policy Engine**: decides *whether/when/how* to deliver feedback (token bucket, safe-window gating, modality).
5. **Renderer**: delivers the cue (haptic/visual/audio/text) and controls exercise playback/metronome.

---

# 2) Canonical Time Model

All timestamps are **monotonic milliseconds** (`t_ms`).

## Musical grid definitions (per exercise)

* `bpm_target`
* `meter` (assume 4/4 for baseline)
* `bars = 2`
* `subdivision` (`8n` typical)
* `count_in_beats` (usually 2)

Derived:

* `beat_ms = 60000 / bpm_target`
* `slot_ms = beat_ms / slots_per_beat(subdivision)`
* `take_duration_ms = count_in_beats*beat_ms + bars*beats_per_bar*beat_ms`

---

# 3) Event Contracts (Exact Schemas)

## 3.1 Segmenter input: Strum candidates

The segmenter listens to a stream of `StrumCandidate` (from detection).

```json
{
  "type": "StrumCandidate",
  "t_ms": 1234567,
  "confidence": 0.86,
  "direction": "down",
  "intensity": 0.62,
  "is_mute": false,
  "source": "audio",
  "seq": 8123
}
```

**Notes**

* `seq` is monotonically increasing; use it to de-dup.
* `source` can be `"audio" | "sensor" | "fusion"` (optional but useful for debugging).

---

## 3.2 Segmenter output: Take lifecycle + finalized take

The segmenter outputs a stream of lifecycle events:

### A) `TakeStatus` (state updates)

```json
{
  "type": "TakeStatus",
  "t_ms": 1235000,
  "exercise_id": "2bar_eighth_down",
  "take_id": "take_00042",
  "state": "COUNT_IN",
  "progress": {
    "count_in_beats_done": 1,
    "bars_done": 0
  },
  "diagnostics": {
    "late_start_suspected": false,
    "missed_count_in": false,
    "extra_bars_detected": false
  }
}
```

### B) `TakeFinalized` (the packet you analyze)

```json
{
  "type": "TakeFinalized",
  "t_ms": 1243200,
  "exercise_id": "2bar_eighth_down",
  "take_id": "take_00042",
  "timing": {
    "take_start_ms": 1234800,
    "count_in_start_ms": 1234800,
    "play_start_ms": 1234800,
    "expected_grid_start_ms": 1234800,
    "expected_grid_end_ms": 1242800,
    "finalize_reason": "GRID_COMPLETE"
  },
  "context": {
    "meter": "4/4",
    "bars": 2,
    "bpm_target": 80,
    "bpm_tolerance": 6,
    "subdivision": "8n",
    "count_in_beats": 2,
    "pattern_id": "2bar_eighth_down"
  },
  "events": [
    { "t_ms": 1236123, "direction": "down", "intensity": 0.57, "confidence": 0.82, "seq": 8130 },
    { "t_ms": 1236512, "direction": "down", "intensity": 0.60, "confidence": 0.88, "seq": 8132 }
  ],
  "flags": {
    "late_start": false,
    "missed_count_in": false,
    "extra_events_after_end": true,
    "extra_bars": false,
    "low_confidence_events": 2
  }
}
```

**Key:** Analyzer must be able to align events to the **expected grid** using:

* `expected_grid_start_ms` (time of slot 0)
* `subdivision`, `bpm_target`, `meter`, `bars`

---

## 3.3 Analyzer output: `TakeAnalysis`

```json
{
  "type": "TakeAnalysis",
  "exercise_id": "2bar_eighth_down",
  "take_id": "take_00042",
  "metrics": {
    "hit_rate": 0.88,
    "miss_rate": 0.12,
    "extra_rate": 0.06,
    "p90_abs_offset_ms": 42,
    "median_offset_ms": -8,
    "std_offset_ms": 19,
    "drift_ms_per_bar": -12,
    "stability": 0.79
  },
  "grid": {
    "grid_start_ms": 1234800,
    "slot_ms": 375,
    "total_slots": 16,
    "expected_slots": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
  },
  "alignment": {
    "matched": [
      { "slot": 0, "seq": 8130, "offset_ms": 12 },
      { "slot": 1, "seq": 8132, "offset_ms": -9 }
    ],
    "missed_slots": [7, 14],
    "extra_seqs": [8149]
  },
  "quality": {
    "event_confidence_mean": 0.81,
    "analysis_confidence": 0.84
  }
}
```

---

## 3.4 Coach output: `CoachDecision`

```json
{
  "type": "CoachDecision",
  "exercise_id": "2bar_eighth_down",
  "take_id": "take_00042",
  "decision_id": "dec_00991",
  "intent": {
    "feedback_intent": "subdivision_support",
    "cue_key": "aim_center_of_click",
    "single_point": true,
    "priority": "high"
  },
  "plan": {
    "next_take": "repeat_same",
    "bpm_next": 80,
    "pattern_next": "2bar_eighth_down",
    "count_in_beats": 2,
    "success_criteria": "p90<=35ms for 2/3 takes"
  },
  "safety": {
    "allow_realtime": true,
    "max_interruptions_this_take": 0
  }
}
```

---

## 3.5 Policy Engine input: `GuidanceRequest`

```json
{
  "type": "GuidanceRequest",
  "t_ms": 1243500,
  "mode": "PRACTICE",
  "backoff": "L1",
  "signals": {
    "timeSinceLastNoteOnMs": 920,
    "phraseBoundaryDetected": true,
    "timeSincePhraseBoundaryMs": 1100,
    "ignoreStreak": 0,
    "silencePreference": 0.2,
    "userExplicitQuiet": false,
    "modeConfidence": 0.83
  },
  "decision": {
    "decision_id": "dec_00991",
    "feedback_intent": "subdivision_support",
    "cue_key": "aim_center_of_click",
    "priority": "high",
    "single_point": true
  },
  "constraints": {
    "realtime_ok": true,
    "suggested_modalities": ["haptic", "visual"],
    "max_cues": 1
  }
}
```

---

## 3.6 Policy Engine output: `GuidanceEnvelope`

```json
{
  "type": "GuidanceEnvelope",
  "t_ms": 1243502,
  "shouldInitiate": true,
  "reason": "ok",
  "selected": {
    "modality": "haptic",
    "tone": "suggestive",
    "granularity": "micro",
    "maxCues": 1
  },
  "timing": {
    "deliver_at_ms": 1243600,
    "delivery_window_ms": 1500
  },
  "policy_snapshot": {
    "interruptBudgetPerMin": 1.5,
    "minPauseMs": 900,
    "betweenPhraseOnly": true
  }
}
```

---

# 4) Take Segmenter Spec (State Machine)

## 4.1 Segmenter states

`IDLE` → `ARMED` → `COUNT_IN` → `PLAYING` → `FINALIZING` → `IDLE`

### IDLE

Waiting for exercise start.

Entry conditions:

* user selects exercise OR system starts practice slice
* metronome/click prepared

Outputs:

* none

---

### ARMED

Ready to start next take; establishing reference time.

Entry actions:

* allocate `take_id`
* set `take_start_ms = now`
* set `count_in_start_ms = now`
* emit `TakeStatus(state="ARMED")`

Exit trigger:

* count-in begins (either system click starts, or auto-start)

---

### COUNT_IN

Count-in beats are running; we’re collecting early events, but not grading them as grid hits unless we decide to.

Entry actions:

* set `expected_grid_start_ms = count_in_start_ms + count_in_beats*beat_ms`
* emit `TakeStatus(state="COUNT_IN")`

Transitions:

* to `PLAYING` when `now >= expected_grid_start_ms` **OR** early strumming indicates missed count-in (see edge case below)

What segmenter collects during COUNT_IN:

* buffer `StrumCandidate` events in `pre_roll_events`

---

### PLAYING

We’re inside the 2-bar grading window.

Entry actions:

* set `play_start_ms = expected_grid_start_ms`
* emit `TakeStatus(state="PLAYING")`

Exit triggers:

1. **GRID_COMPLETE**: `now >= expected_grid_end_ms`
2. **USER_STOP**: player stops for long enough (pause-based abort)
3. **RESTART**: player starts new take mid-window (strong reset signature)

---

### FINALIZING

Stop accepting events; package the take; emit `TakeFinalized`.

Entry actions:

* include events from:

  * optionally: `pre_roll_events` (for diagnostics)
  * required: all events between `expected_grid_start_ms` and `expected_grid_end_ms`
  * optionally: `post_roll` for “extra events after end” flagging
* compute take flags (late start, missed count-in, extras, low confidence)
* emit `TakeFinalized`
* transition back to `IDLE` or `ARMED` depending on auto-repeat

---

## 4.2 Segmenter timing constants (recommended defaults)

These should be configurable:

* `MIN_EVENT_CONFIDENCE = 0.55` (ignore lower confidence events by default)
* `LATE_START_GRACE_MS = 0.5 * slot_ms`
* `MISSED_COUNT_IN_WINDOW_MS = 1.0 * beat_ms` (early strumming during last count-in beat)
* `ABORT_PAUSE_MS = 2500` (if no events and no click? treat as stop)
* `POST_ROLL_MS = 500` (capture extras just after grid end)
* `RESTART_SIGNATURE`: ≥3 events within 600ms after a long pause (see below)

---

# 5) Edge Case Handling (Detailed)

## 5.1 Late start (player begins after grid start)

**Symptom**

* First valid strum event occurs after `expected_grid_start_ms + LATE_START_GRACE_MS`

**Segmenter behavior**

* Still finalize normally at `expected_grid_end_ms`
* Set `flags.late_start = true`
* Optionally shift analysis grid? **Do not auto-shift grid** in v0; let coach reduce tempo or re-run count-in.

**Rationale**
Auto-shifting hides the learning signal (“start on time”).

---

## 5.2 Missed count-in (player starts during count-in)

Two variants:

### Variant A: player starts early, continues

**Symptom**

* ≥2 strums in the last beat of count-in or during count-in in a pattern-like cadence

**Behavior**

* Set `flags.missed_count_in = true`
* Do not treat count-in strums as grading hits
* Optionally emit a light “wait for count-in” cue next take (coach-level)

### Variant B: player starts early and the take becomes ambiguous

**Symptom**

* Strumming begins during count-in and the system can’t tell whether they intended to start immediately

**Behavior**

* Finalize the take as normal, but lower `analysis_confidence`
* Coach likely chooses: “repeat with clearer count-in” + maybe increase count-in to 4 beats

---

## 5.3 Extra bars (player keeps going beyond 2 bars)

**Symptom**

* Strumming continues beyond `expected_grid_end_ms + POST_ROLL_MS`

**Behavior options**

* **Default (recommended): hard-stop** at 2 bars:

  * finalize at `expected_grid_end_ms`
  * set `flags.extra_events_after_end = true`
  * ignore subsequent events for this take
* If you support “looping takes,” treat the next bar as the beginning of the next take only if:

  * there is a phrase boundary pause OR
  * the system explicitly instructed “keep looping”

Edge case: user plays 4 bars intentionally
→ this is a different exercise. Do not stretch the 2-bar grader.

---

## 5.4 Early stop (player stops mid-take)

**Symptom**

* No events for `ABORT_PAUSE_MS` before grid end

**Behavior**

* Finalize with reason `USER_STOP`
* Mark `flags.partial_take = true` (add this to schema if useful)
* Analyzer should still compute hit/miss relative to expected slots up to the point reached OR compute overall but with low confidence. (Pick one and be consistent.)

Recommended approach:

* Compute metrics on full expected grid but set `analysis_confidence` low so coach prioritizes “repeat” rather than critique.

---

## 5.5 Double-start / restart mid-take

This happens when the player messes up and immediately restarts.

**Restart signature (practical)**

* A long pause (>800ms) followed by a burst of ≥3 events within 600ms near a downbeat-like moment.

**Behavior**

* If restart signature occurs before 1 bar completes:

  * abort current take, start a new take immediately
  * emit `TakeStatus(state="ARMED")` then `COUNT_IN` (or `PLAYING` if you run “no count-in” restart)
* If after 1 bar completes:

  * finalize current take as partial, then start new take

---

## 5.6 Tempo drift (player not at target BPM)

Since this exercise has a target BPM, segmenter should *not* attempt to estimate BPM and realign grid in v0.

Instead:

* compute a simple “tempo mismatch indicator” for coach:

  * compare inter-strum intervals to slot_ms
  * if median interval differs by > tolerance, set `flags.tempo_mismatch = true`

Coach response:

* suggest slowing down, enabling stronger pulse, or redoing count-in

---

# 6) Take Segmenter Algorithms

## 6.1 Phrase boundary detection (minimum viable)

For this exercise, phrase boundary can be approximated as:

* a pause > `MP` (min_pause_ms) OR
* reaching grid end

For general playing, you’ll have a richer phrase boundary detector. The segmenter can accept phrase boundaries from upstream and pass them through.

## 6.2 Event buffering rules

* Keep a ring buffer of recent events (e.g., last 10s)
* During COUNT_IN: buffer as `pre_roll_events`
* During PLAYING: buffer to `take_events`
* After end: collect `post_roll_events` for `POST_ROLL_MS`

Filter:

* discard events with `confidence < MIN_EVENT_CONFIDENCE`
* de-dup by `seq`

---

# 7) Integration Contracts: Exact Flow

## 7.1 Segmenter → Analyzer

Send `TakeFinalized` exactly once per take.

Analyzer requires:

* `events[]` (in-window strum events)
* `expected_grid_start_ms`, `bpm_target`, `meter`, `bars`, `subdivision`, `pattern_id`

## 7.2 Analyzer → Coach

Send `TakeAnalysis`.

Coach requires:

* `metrics`
* `alignment` misses/extras (for diagnosing coverage vs timing)
* `analysis_confidence`
* take flags (late start, missed count-in, partial)

## 7.3 Coach → Policy Engine

Send `GuidanceRequest`.

Policy engine requires:

* `mode`, `backoff`, `signals` (pause, phrase boundary, ignore streak)
* `decision` intent + priority + cue_key
* `constraints` suggested modalities (optional)

## 7.4 Policy Engine → Renderer

Send `GuidanceEnvelope`.

Renderer uses:

* `shouldInitiate`
* `deliver_at_ms` window
* modality + tone + granularity + maxCues
* plus cue_key/content lookup (from coach)

---

# 8) Segmenter Reference State Machine (Pseudocode)

```pseudo
on ExerciseStart(ctx):
  state = ARMED
  take_id++
  take_start = now
  count_in_start = now
  expected_grid_start = count_in_start + ctx.count_in_beats * beat_ms
  expected_grid_end = expected_grid_start + ctx.bars * beats_per_bar * beat_ms
  pre_roll = []
  in_window = []
  post_roll = []
  emit TakeStatus(ARMED)

tick(now):
  if state == ARMED:
     state = COUNT_IN
     emit TakeStatus(COUNT_IN)

  if state == COUNT_IN:
     collect candidates into pre_roll
     if now >= expected_grid_start:
        state = PLAYING
        play_start = expected_grid_start
        emit TakeStatus(PLAYING)
     else if detect_missed_count_in(pre_roll, ctx):
        flags.missed_count_in = true
        // still wait for expected_grid_start, or optionally fast-forward:
        // if you fast-forward, set expected_grid_start = now + small_guard
        // recommended v0: do not fast-forward

  if state == PLAYING:
     collect candidates into in_window
     if now >= expected_grid_end:
        state = FINALIZING
        finalize_reason = GRID_COMPLETE
     else if no events for ABORT_PAUSE_MS:
        state = FINALIZING
        finalize_reason = USER_STOP
     else if detect_restart_signature():
        state = FINALIZING
        finalize_reason = RESTART

  if state == FINALIZING:
     collect post_roll for POST_ROLL_MS
     build TakeFinalized packet with flags
     emit TakeFinalized
     state = ARMED (if auto-repeat) else IDLE
```

---

# 9) What to Implement First (Practical Order)

1. **Hard grid segmentation**: count-in start → grid start → grid end
2. **Basic edge flags**: late_start, missed_count_in, extra_events_after_end, partial_take
3. **Abort behavior**: user stop mid-take
4. **Restart detection** (optional but high UX value)
5. **Tempo mismatch flag** (optional)

---

If you want, I can provide:

* a TypeScript reference implementation of the segmenter (state machine + buffering + flags),
* plus a tiny test harness with synthetic strum streams that cover every edge case above.


```ts
/* take_segmenter.ts
 * TypeScript reference implementation:
 * - State machine: IDLE → ARMED → COUNT_IN → PLAYING → FINALIZING → (ARMED|IDLE)
 * - Ring buffering + de-dupe by seq
 * - Flags: late_start, missed_count_in, extra_events_after_end, extra_bars, partial_take, tempo_mismatch, low_confidence_events
 * - Edge cases: late start, missed count-in, extra bars (hard stop), early stop, restart signature
 */

export type Meter = "4/4" | "3/4" | "6/8";
export type Subdivision = "4n" | "8n" | "16n";
export type StrumDirection = "down" | "up" | "unknown";

export interface StrumCandidate {
  type: "StrumCandidate";
  t_ms: number;             // monotonic ms
  confidence: number;       // 0..1
  direction: StrumDirection;
  intensity?: number;       // 0..1
  is_mute?: boolean;
  source?: "audio" | "sensor" | "fusion";
  seq: number;              // monotonic integer id
}

export interface StrumPatternSpec {
  pattern_id: string;
  subdivision: Subdivision;
  expected_hits: number[];          // indices on 2-bar grid, e.g., 0..15
  directions?: StrumDirection[];    // optional, same length as expected_hits
}

export interface StrumExerciseContext {
  exercise_id: string;
  meter: Meter;
  bars: number;            // for this slice: 2
  bpm_target: number;
  bpm_tolerance: number;   // +/- bpm
  count_in_beats: number;  // e.g., 2
  pattern: StrumPatternSpec;
}

export type TakeState = "IDLE" | "ARMED" | "COUNT_IN" | "PLAYING" | "FINALIZING";

export interface TakeStatus {
  type: "TakeStatus";
  t_ms: number;
  exercise_id: string;
  take_id: string;
  state: Exclude<TakeState, "IDLE">;
  progress: {
    count_in_beats_done: number;
    bars_done: number;
  };
  diagnostics: {
    late_start_suspected: boolean;
    missed_count_in: boolean;
    extra_bars_detected: boolean;
    tempo_mismatch: boolean;
    restart_detected: boolean;
    partial_take: boolean;
  };
}

export type FinalizeReason = "GRID_COMPLETE" | "USER_STOP" | "RESTART" | "CANCELLED";

export interface TakeFinalized {
  type: "TakeFinalized";
  t_ms: number;
  exercise_id: string;
  take_id: string;
  timing: {
    take_start_ms: number;
    count_in_start_ms: number;
    play_start_ms: number;          // expected_grid_start_ms (grid slot 0)
    expected_grid_start_ms: number;
    expected_grid_end_ms: number;
    finalize_reason: FinalizeReason;
  };
  context: {
    meter: Meter;
    bars: number;
    bpm_target: number;
    bpm_tolerance: number;
    subdivision: Subdivision;
    count_in_beats: number;
    pattern_id: string;
  };
  events: Array<{
    t_ms: number;
    direction: StrumDirection;
    intensity?: number;
    confidence: number;
    seq: number;
  }>;
  flags: {
    late_start: boolean;
    missed_count_in: boolean;
    extra_events_after_end: boolean;
    extra_bars: boolean;
    partial_take: boolean;
    tempo_mismatch: boolean;
    restart_detected: boolean;
    low_confidence_events: number;
  };
}

export type SegmenterOutput = TakeStatus | TakeFinalized;

export interface SegmenterConfig {
  // Filtering
  minEventConfidence: number;        // default 0.55
  ringBufferMs: number;              // default 10000

  // Timing
  lateStartGraceFracOfSlot: number;  // default 0.5
  missedCountInWindowBeats: number;  // default 1.0
  abortPauseMs: number;              // default 2500
  postRollMs: number;                // default 500

  // Restart signature
  restartPauseMs: number;            // pause threshold to consider "restart" preface (default 800)
  restartBurstMs: number;            // window to count burst events after pause (default 600)
  restartBurstCount: number;         // events in burst (default 3)

  // Tempo mismatch detection
  tempoMismatchMedianIntervalFrac: number; // e.g., 0.20 means 20% away from slot interval triggers mismatch
  tempoMismatchMinPairs: number;          // e.g., 6

  // Behavior
  autoRepeat: boolean;               // default true
}

export function defaultSegmenterConfig(): SegmenterConfig {
  return {
    minEventConfidence: 0.55,
    ringBufferMs: 10000,

    lateStartGraceFracOfSlot: 0.5,
    missedCountInWindowBeats: 1.0,
    abortPauseMs: 2500,
    postRollMs: 500,

    restartPauseMs: 800,
    restartBurstMs: 600,
    restartBurstCount: 3,

    tempoMismatchMedianIntervalFrac: 0.20,
    tempoMismatchMinPairs: 6,

    autoRepeat: true,
  };
}

function beatsPerBar(meter: Meter): number {
  if (meter === "3/4") return 3;
  if (meter === "6/8") return 2; // treating 6/8 as 2 dotted-quarter beats for this segmenter
  return 4;
}

function slotsPerBeat(sub: Subdivision): number {
  if (sub === "4n") return 1;
  if (sub === "8n") return 2;
  return 4; // 16n
}

function median(nums: number[]): number {
  if (nums.length === 0) return 0;
  const a = [...nums].sort((x, y) => x - y);
  const mid = Math.floor(a.length / 2);
  return a.length % 2 ? a[mid] : (a[mid - 1] + a[mid]) / 2;
}

function clamp01(x: number): number {
  if (x < 0) return 0;
  if (x > 1) return 1;
  return x;
}

class RingBuffer<T extends { t_ms: number }> {
  private items: T[] = [];
  constructor(private windowMs: number) {}
  push(x: T) {
    this.items.push(x);
  }
  prune(nowMs: number) {
    const cutoff = nowMs - this.windowMs;
    while (this.items.length && this.items[0].t_ms < cutoff) this.items.shift();
  }
  values(): T[] {
    return this.items;
  }
  clear() {
    this.items = [];
  }
}

export class TakeSegmenter {
  private cfg: SegmenterConfig;
  private state: TakeState = "IDLE";

  private ctx: StrumExerciseContext | null = null;

  private takeCounter = 0;
  private takeId = "";

  // Timing anchors
  private takeStartMs = 0;
  private countInStartMs = 0;
  private expectedGridStartMs = 0;
  private expectedGridEndMs = 0;

  // Derived
  private beatMs = 0;
  private slotMs = 0;
  private totalBeats = 0;

  // Event buffers (already filtered/de-duped)
  private ring: RingBuffer<StrumCandidate>;
  private preRoll: StrumCandidate[] = [];
  private inWindow: StrumCandidate[] = [];
  private postRoll: StrumCandidate[] = [];

  private seenSeq = new Set<number>();

  // Diagnostics/flags
  private flags = {
    late_start: false,
    missed_count_in: false,
    extra_events_after_end: false,
    extra_bars: false,
    partial_take: false,
    tempo_mismatch: false,
    restart_detected: false,
    low_confidence_events: 0,
  };

  // For stop & restart detection
  private lastAcceptedEventMs: number | null = null;
  private lastEventMsAll: number | null = null; // includes low-confidence (for pause signature)
  private restartPauseStartMs: number | null = null;
  private burstEventsAfterPause: number = 0;

  constructor(cfg: SegmenterConfig = defaultSegmenterConfig()) {
    this.cfg = cfg;
    this.ring = new RingBuffer<StrumCandidate>(cfg.ringBufferMs);
  }

  /** Start a new exercise session (arms a take). */
  startExercise(nowMs: number, ctx: StrumExerciseContext): SegmenterOutput[] {
    this.ctx = ctx;
    this.computeDerived(ctx);

    this.state = "ARMED";
    this.allocateTake(nowMs);

    return [this.makeStatus(nowMs, "ARMED")];
  }

  /** Cancel (e.g., user switches exercise). */
  cancel(nowMs: number): SegmenterOutput[] {
    const outs: SegmenterOutput[] = [];
    if (this.state === "PLAYING" || this.state === "COUNT_IN" || this.state === "ARMED") {
      outs.push(this.finalize(nowMs, "CANCELLED"));
    }
    this.resetToIdle();
    return outs;
  }

  /** Feed strum candidates + advance internal clock (call with each incoming event, and/or periodically). */
  ingest(nowMs: number, candidates: StrumCandidate[] = []): SegmenterOutput[] {
    if (!this.ctx) return [];

    // housekeeping
    this.ring.prune(nowMs);

    // ingest candidates (de-dup + count low-confidence)
    for (const c of candidates) {
      if (this.seenSeq.has(c.seq)) continue;
      this.seenSeq.add(c.seq);

      this.lastEventMsAll = c.t_ms;

      if (c.confidence < this.cfg.minEventConfidence) {
        this.flags.low_confidence_events += 1;
        // keep in ring for restart/pause heuristics? optional. We'll store anyway.
        this.ring.push(c);
        continue;
      }

      this.ring.push(c);
      this.lastAcceptedEventMs = c.t_ms;

      if (this.state === "COUNT_IN") this.preRoll.push(c);
      else if (this.state === "PLAYING") this.inWindow.push(c);
      else if (this.state === "FINALIZING") this.postRoll.push(c);
    }

    // run state machine
    const outs: SegmenterOutput[] = [];
    outs.push(...this.step(nowMs));
    return outs;
  }

  /** Periodic tick even if no events arrived. */
  tick(nowMs: number): SegmenterOutput[] {
    return this.ingest(nowMs, []);
  }

  // ---------------- internal ----------------

  private computeDerived(ctx: StrumExerciseContext) {
    this.beatMs = 60000 / ctx.bpm_target;
    const spb = slotsPerBeat(ctx.pattern.subdivision);
    this.slotMs = this.beatMs / spb;

    const bpb = beatsPerBar(ctx.meter);
    this.totalBeats = bpb * ctx.bars;
  }

  private allocateTake(nowMs: number) {
    this.takeCounter += 1;
    this.takeId = `take_${String(this.takeCounter).padStart(5, "0")}`;

    this.takeStartMs = nowMs;
    this.countInStartMs = nowMs;

    const countInMs = (this.ctx!.count_in_beats) * this.beatMs;
    this.expectedGridStartMs = this.countInStartMs + countInMs;
    this.expectedGridEndMs = this.expectedGridStartMs + this.totalBeats * this.beatMs;

    this.preRoll = [];
    this.inWindow = [];
    this.postRoll = [];
    this.flags = {
      late_start: false,
      missed_count_in: false,
      extra_events_after_end: false,
      extra_bars: false,
      partial_take: false,
      tempo_mismatch: false,
      restart_detected: false,
      low_confidence_events: 0,
    };

    this.lastAcceptedEventMs = null;
    this.lastEventMsAll = null;
    this.restartPauseStartMs = null;
    this.burstEventsAfterPause = 0;
  }

  private resetToIdle() {
    this.state = "IDLE";
    this.ctx = null;
    this.preRoll = [];
    this.inWindow = [];
    this.postRoll = [];
    this.seenSeq.clear();
    this.ring.clear();
  }

  private step(nowMs: number): SegmenterOutput[] {
    const outs: SegmenterOutput[] = [];

    if (this.state === "ARMED") {
      this.state = "COUNT_IN";
      outs.push(this.makeStatus(nowMs, "COUNT_IN"));
      return outs;
    }

    if (this.state === "COUNT_IN") {
      // detect missed count-in (player starts during count-in window)
      if (!this.flags.missed_count_in && this.detectMissedCountIn(nowMs)) {
        this.flags.missed_count_in = true;
      }

      // update status occasionally (optional; here: only on state transitions)
      if (nowMs >= this.expectedGridStartMs) {
        this.state = "PLAYING";
        outs.push(this.makeStatus(nowMs, "PLAYING"));
      }
      return outs;
    }

    if (this.state === "PLAYING") {
      // Late start
      if (!this.flags.late_start) {
        const grace = this.cfg.lateStartGraceFracOfSlot * this.slotMs;
        const first = this.inWindow.length ? this.inWindow[0].t_ms : null;
        if (first !== null && first > this.expectedGridStartMs + grace) {
          this.flags.late_start = true;
        }
      }

      // Restart detection
      if (!this.flags.restart_detected && this.detectRestartSignature(nowMs)) {
        this.flags.restart_detected = true;
        outs.push(this.finalize(nowMs, "RESTART"));
        // Immediate new take (common UX)
        if (this.cfg.autoRepeat) {
          this.state = "ARMED";
          this.allocateTake(nowMs);
          outs.push(this.makeStatus(nowMs, "ARMED"));
        } else {
          this.resetToIdle();
        }
        return outs;
      }

      // Early stop detection
      if (this.detectEarlyStop(nowMs)) {
        this.flags.partial_take = true;
        outs.push(this.finalize(nowMs, "USER_STOP"));
        if (this.cfg.autoRepeat) {
          this.state = "ARMED";
          this.allocateTake(nowMs);
          outs.push(this.makeStatus(nowMs, "ARMED"));
        } else {
          this.resetToIdle();
        }
        return outs;
      }

      // Grid complete
      if (nowMs >= this.expectedGridEndMs) {
        // switch to FINALIZING and capture post-roll for a short period
        this.state = "FINALIZING";
        // status not required, but can be useful for UI/debug
        // outs.push(this.makeStatus(nowMs, "FINALIZING" as any)); // not in schema
      }
      return outs;
    }

    if (this.state === "FINALIZING") {
      // collect post-roll for POST_ROLL_MS
      const postRollEnd = this.expectedGridEndMs + this.cfg.postRollMs;
      if (nowMs < postRollEnd) {
        // continue gathering post-roll via ingest()
        return outs;
      }

      // finalize now
      outs.push(this.finalize(nowMs, "GRID_COMPLETE"));

      if (this.cfg.autoRepeat) {
        this.state = "ARMED";
        this.allocateTake(nowMs);
        outs.push(this.makeStatus(nowMs, "ARMED"));
      } else {
        this.resetToIdle();
      }
      return outs;
    }

    // IDLE
    return outs;
  }

  private detectMissedCountIn(nowMs: number): boolean {
    // Look for ≥2 accepted events within the last beat of count-in (or configured window)
    const windowBeats = this.cfg.missedCountInWindowBeats;
    const winMs = windowBeats * this.beatMs;

    const end = Math.min(nowMs, this.expectedGridStartMs);
    const start = Math.max(this.countInStartMs, end - winMs);

    const hits = this.preRoll.filter(e => e.t_ms >= start && e.t_ms <= end);
    return hits.length >= 2;
  }

  private detectEarlyStop(nowMs: number): boolean {
    // If we've started playing (past grid start) and there are no accepted events for abortPauseMs
    // and we're not at grid end yet, treat as stop.
    if (nowMs < this.expectedGridStartMs + 50) return false;
    if (nowMs >= this.expectedGridEndMs) return false;

    const last = this.lastAcceptedEventMs;
    if (last === null) {
      // no events at all in PLAYING; if it's been long enough, it's probably a stop
      return (nowMs - this.expectedGridStartMs) >= this.cfg.abortPauseMs;
    }
    return (nowMs - last) >= this.cfg.abortPauseMs;
  }

  private detectRestartSignature(nowMs: number): boolean {
    // Signature: pause > restartPauseMs then burst of >= restartBurstCount events within restartBurstMs
    // We infer pause based on accepted events timing.
    const last = this.lastAcceptedEventMs;
    if (last === null) return false;

    const silenceMs = nowMs - last;

    if (this.restartPauseStartMs === null) {
      if (silenceMs >= this.cfg.restartPauseMs) {
        this.restartPauseStartMs = nowMs;
        this.burstEventsAfterPause = 0;
      }
      return false;
    }

    // If pause started, count events that arrive after it (tracked in ingest by lastAcceptedEventMs updates)
    // Here, we approximate by scanning ring buffer for events after pause start.
    const pauseStart = this.restartPauseStartMs;
    const cutoff = pauseStart;
    const after = this.ring.values().filter(e => e.confidence >= this.cfg.minEventConfidence && e.t_ms >= cutoff);

    this.burstEventsAfterPause = after.length;

    // If burst window elapsed, reset if not enough
    if (nowMs - pauseStart > this.cfg.restartBurstMs) {
      const detected = this.burstEventsAfterPause >= this.cfg.restartBurstCount;
      this.restartPauseStartMs = null;
      this.burstEventsAfterPause = 0;
      return detected;
    }

    // Early detect if already enough events quickly
    return this.burstEventsAfterPause >= this.cfg.restartBurstCount;
  }

  private computeTempoMismatchFlag(events: StrumCandidate[]): boolean {
    // Compare median inter-event interval to expected slot interval.
    // Only meaningful if enough events.
    if (events.length < this.cfg.tempoMismatchMinPairs + 1) return false;
    const ts = [...events].sort((a, b) => a.t_ms - b.t_ms).map(e => e.t_ms);
    const d: number[] = [];
    for (let i = 1; i < ts.length; i++) d.push(ts[i] - ts[i - 1]);
    const med = median(d);
    const expected = this.slotMs;
    const frac = Math.abs(med - expected) / expected;
    return frac > this.cfg.tempoMismatchMedianIntervalFrac;
  }

  private finalize(nowMs: number, reason: FinalizeReason): TakeFinalized {
    // Determine events in-window: those with t between grid start and grid end
    const inWin = this.inWindow.filter(e => e.t_ms >= this.expectedGridStartMs && e.t_ms <= this.expectedGridEndMs);

    // Post-roll extras
    const extraAfterEnd = this.postRoll.some(e => e.t_ms > this.expectedGridEndMs);
    this.flags.extra_events_after_end = extraAfterEnd;

    // Extra bars heuristic: continued strumming significantly after end (beyond post-roll)
    // Here: if we see accepted events later than end+postRollMs, mark extra_bars.
    const extraBarCutoff = this.expectedGridEndMs + this.cfg.postRollMs;
    const ringAfter = this.ring.values().some(e => e.confidence >= this.cfg.minEventConfidence && e.t_ms > extraBarCutoff);
    this.flags.extra_bars = ringAfter;

    // Tempo mismatch (from in-window only)
    this.flags.tempo_mismatch = this.computeTempoMismatchFlag(inWin);

    const finalized: TakeFinalized = {
      type: "TakeFinalized",
      t_ms: nowMs,
      exercise_id: this.ctx!.exercise_id,
      take_id: this.takeId,
      timing: {
        take_start_ms: this.takeStartMs,
        count_in_start_ms: this.countInStartMs,
        play_start_ms: this.expectedGridStartMs,
        expected_grid_start_ms: this.expectedGridStartMs,
        expected_grid_end_ms: this.expectedGridEndMs,
        finalize_reason: reason,
      },
      context: {
        meter: this.ctx!.meter,
        bars: this.ctx!.bars,
        bpm_target: this.ctx!.bpm_target,
        bpm_tolerance: this.ctx!.bpm_tolerance,
        subdivision: this.ctx!.pattern.subdivision,
        count_in_beats: this.ctx!.count_in_beats,
        pattern_id: this.ctx!.pattern.pattern_id,
      },
      events: inWin.map(e => ({
        t_ms: e.t_ms,
        direction: e.direction,
        intensity: e.intensity,
        confidence: e.confidence,
        seq: e.seq,
      })),
      flags: {
        late_start: this.flags.late_start,
        missed_count_in: this.flags.missed_count_in,
        extra_events_after_end: this.flags.extra_events_after_end,
        extra_bars: this.flags.extra_bars,
        partial_take: this.flags.partial_take,
        tempo_mismatch: this.flags.tempo_mismatch,
        restart_detected: this.flags.restart_detected,
        low_confidence_events: this.flags.low_confidence_events,
      },
    };

    return finalized;
  }

  private makeStatus(nowMs: number, state: Exclude<TakeState, "IDLE">): TakeStatus {
    // Progress estimates (rough; enough for UI/debug)
    const doneCountInBeats = Math.max(0, Math.min(this.ctx!.count_in_beats,
      (nowMs - this.countInStartMs) / this.beatMs
    ));

    const barsDone = Math.max(0, Math.min(this.ctx!.bars,
      (nowMs - this.expectedGridStartMs) / (beatsPerBar(this.ctx!.meter) * this.beatMs)
    ));

    const lateStartSuspected =
      this.state === "PLAYING" &&
      this.inWindow.length === 0 &&
      nowMs > this.expectedGridStartMs + (this.cfg.lateStartGraceFracOfSlot * this.slotMs);

    const status: TakeStatus = {
      type: "TakeStatus",
      t_ms: nowMs,
      exercise_id: this.ctx!.exercise_id,
      take_id: this.takeId,
      state,
      progress: {
        count_in_beats_done: doneCountInBeats,
        bars_done: barsDone,
      },
      diagnostics: {
        late_start_suspected: lateStartSuspected,
        missed_count_in: this.flags.missed_count_in,
        extra_bars_detected: this.flags.extra_bars,
        tempo_mismatch: this.flags.tempo_mismatch,
        restart_detected: this.flags.restart_detected,
        partial_take: this.flags.partial_take,
      },
    };

    return status;
  }
}
```

```ts
/* take_segmenter_test_harness.ts
 * Tiny test harness with synthetic strum streams covering edge cases:
 * 1) Clean take
 * 2) Late start
 * 3) Missed count-in (early strums)
 * 4) Extra bars (strumming continues past 2 bars)
 * 5) Early stop mid-take
 * 6) Restart signature mid-take
 *
 * Run with: ts-node take_segmenter_test_harness.ts
 */

import {
  TakeSegmenter,
  defaultSegmenterConfig,
  StrumExerciseContext,
  StrumCandidate,
  SegmenterOutput,
} from "./take_segmenter";

function mkCtx(): StrumExerciseContext {
  return {
    exercise_id: "2bar_eighth_down",
    meter: "4/4",
    bars: 2,
    bpm_target: 80,
    bpm_tolerance: 6,
    count_in_beats: 2,
    pattern: {
      pattern_id: "2bar_eighth_down",
      subdivision: "8n",
      expected_hits: Array.from({ length: 16 }, (_, i) => i),
      directions: Array.from({ length: 16 }, () => "down"),
    },
  };
}

function beatMs(bpm: number) { return 60000 / bpm; }
function slotMs(bpm: number) { return beatMs(bpm) / 2; } // 8n

let seq = 1;
function ev(t: number, confidence = 0.9): StrumCandidate {
  return {
    type: "StrumCandidate",
    t_ms: t,
    confidence,
    direction: "down",
    intensity: 0.6,
    is_mute: false,
    source: "synthetic",
    seq: seq++,
  };
}

function runScenario(name: string, events: StrumCandidate[], ticks: number[], now0: number) {
  const ctx = mkCtx();
  const seg = new TakeSegmenter(defaultSegmenterConfig());

  const outputs: SegmenterOutput[] = [];
  outputs.push(...seg.startExercise(now0, ctx));

  // Feed events in chronological order; call tick at tick times
  const allTimes = [...ticks, ...events.map(e => e.t_ms)].sort((a, b) => a - b);
  let iEv = 0;

  for (const t of allTimes) {
    const batch: StrumCandidate[] = [];
    while (iEv < events.length && events[iEv].t_ms === t) {
      batch.push(events[iEv++]);
    }
    if (batch.length) outputs.push(...seg.ingest(t, batch));
    else outputs.push(...seg.tick(t));
  }

  // Final ticks to let post-roll finalize
  outputs.push(...seg.tick(allTimes[allTimes.length - 1] + 600));

  console.log("\n==============================");
  console.log(`SCENARIO: ${name}`);
  console.log("==============================");
  for (const o of outputs) {
    if (o.type === "TakeStatus") {
      // keep status logs short
      if (o.state === "COUNT_IN" || o.state === "PLAYING") continue;
      console.log(`[STATUS] t=${o.t_ms} take=${o.take_id} state=${o.state}`);
    } else {
      console.log(`[FINAL] t=${o.t_ms} take=${o.take_id} reason=${o.timing.finalize_reason}`);
      console.log(`  flags=${JSON.stringify(o.flags)}`);
      console.log(`  events_in_window=${o.events.length}`);
    }
  }
}

function buildCleanTake(now0: number): StrumCandidate[] {
  const ctx = mkCtx();
  const sMs = slotMs(ctx.bpm_target);
  const gridStart = now0 + ctx.count_in_beats * beatMs(ctx.bpm_target);

  const events: StrumCandidate[] = [];
  for (let k = 0; k < 16; k++) {
    // small jitter ±10ms
    const jitter = (k % 2 === 0) ? 8 : -7;
    events.push(ev(Math.round(gridStart + k * sMs + jitter)));
  }
  return events.sort((a, b) => a.t_ms - b.t_ms);
}

function buildLateStart(now0: number): StrumCandidate[] {
  const ctx = mkCtx();
  const sMs = slotMs(ctx.bpm_target);
  const gridStart = now0 + ctx.count_in_beats * beatMs(ctx.bpm_target);

  const events: StrumCandidate[] = [];
  // skip first 2 slots (late)
  for (let k = 2; k < 16; k++) {
    events.push(ev(Math.round(gridStart + k * sMs + 5)));
  }
  return events.sort((a, b) => a.t_ms - b.t_ms);
}

function buildMissedCountIn(now0: number): StrumCandidate[] {
  const ctx = mkCtx();
  const sMs = slotMs(ctx.bpm_target);
  const bMs = beatMs(ctx.bpm_target);
  const gridStart = now0 + ctx.count_in_beats * bMs;

  const events: StrumCandidate[] = [];
  // early strums during count-in last beat
  events.push(ev(Math.round(now0 + bMs * 1.2)));
  events.push(ev(Math.round(now0 + bMs * 1.6)));
  // then normal take
  for (let k = 0; k < 16; k++) events.push(ev(Math.round(gridStart + k * sMs)));
  return events.sort((a, b) => a.t_ms - b.t_ms);
}

function buildExtraBars(now0: number): StrumCandidate[] {
  const ctx = mkCtx();
  const sMs = slotMs(ctx.bpm_target);
  const gridStart = now0 + ctx.count_in_beats * beatMs(ctx.bpm_target);
  const gridEnd = gridStart + 2 * 4 * beatMs(ctx.bpm_target);

  const events: StrumCandidate[] = [];
  for (let k = 0; k < 16; k++) events.push(ev(Math.round(gridStart + k * sMs)));
  // continue strumming beyond end (extra bars)
  for (let k = 0; k < 8; k++) events.push(ev(Math.round(gridEnd + 800 + k * sMs)));
  return events.sort((a, b) => a.t_ms - b.t_ms);
}

function buildEarlyStop(now0: number): StrumCandidate[] {
  const ctx = mkCtx();
  const sMs = slotMs(ctx.bpm_target);
  const gridStart = now0 + ctx.count_in_beats * beatMs(ctx.bpm_target);

  const events: StrumCandidate[] = [];
  // only first bar (~8 strums), then stop
  for (let k = 0; k < 8; k++) events.push(ev(Math.round(gridStart + k * sMs)));
  return events.sort((a, b) => a.t_ms - b.t_ms);
}

function buildRestartSignature(now0: number): StrumCandidate[] {
  const ctx = mkCtx();
  const sMs = slotMs(ctx.bpm_target);
  const bMs = beatMs(ctx.bpm_target);
  const gridStart = now0 + ctx.count_in_beats * bMs;

  const events: StrumCandidate[] = [];
  // first few strums
  for (let k = 0; k < 4; k++) events.push(ev(Math.round(gridStart + k * sMs)));
  // then long-ish pause (simulate restart)
  const pauseStart = Math.round(gridStart + 4 * sMs);
  const restartAt = pauseStart + 1000; // > restartPauseMs
  // burst of 3 events quickly within 600ms
  events.push(ev(restartAt + 10));
  events.push(ev(restartAt + 180));
  events.push(ev(restartAt + 340));
  // then continue as if new attempt (not necessary; segmenter will finalize on RESTART)
  return events.sort((a, b) => a.t_ms - b.t_ms);
}

function main() {
  const now0 = 1_000_000; // arbitrary monotonic start
  const ctx = mkCtx();
  const bMs = beatMs(ctx.bpm_target);
  const gridEnd = now0 + ctx.count_in_beats * bMs + 2 * 4 * bMs;

  // tick times (coarse) to drive segmenter; include end+postroll
  const ticks = [
    now0,
    now0 + 200,
    now0 + 800,
    now0 + 1200,
    now0 + 2000,
    now0 + 3000,
    now0 + 4000,
    gridEnd + 100,
    gridEnd + 600,
    gridEnd + 1200,
  ];

  runScenario("Clean take", buildCleanTake(now0), ticks, now0);
  runScenario("Late start", buildLateStart(now0), ticks, now0 + 50_000);
  runScenario("Missed count-in", buildMissedCountIn(now0 + 100_000), ticks.map(t => t + 100_000), now0 + 100_000);
  runScenario("Extra bars", buildExtraBars(now0 + 150_000), ticks.map(t => t + 150_000), now0 + 150_000);
  runScenario("Early stop", buildEarlyStop(now0 + 200_000), ticks.map(t => t + 200_000), now0 + 200_000);
  runScenario("Restart signature", buildRestartSignature(now0 + 250_000), ticks.map(t => t + 250_000), now0 + 250_000);
}

main();
```

```json
{
  "contracts": {
    "segmenter_to_analyzer": {
      "TakeFinalized": {
        "required": [
          "type",
          "t_ms",
          "exercise_id",
          "take_id",
          "timing.expected_grid_start_ms",
          "timing.expected_grid_end_ms",
          "context.meter",
          "context.bars",
          "context.bpm_target",
          "context.subdivision",
          "context.count_in_beats",
          "context.pattern_id",
          "events"
        ],
        "notes": [
          "Analyzer aligns events to a grid where slot 0 occurs at expected_grid_start_ms.",
          "Analyzer should treat flags.partial_take and finalize_reason!=GRID_COMPLETE as low-confidence takes."
        ]
      }
    },
    "analyzer_to_coach": {
      "TakeAnalysis": {
        "required": [
          "type",
          "exercise_id",
          "take_id",
          "metrics.hit_rate",
          "metrics.p90_abs_offset_ms",
          "metrics.drift_ms_per_bar",
          "metrics.stability",
          "quality.analysis_confidence"
        ],
        "notes": [
          "Coach uses metrics + flags (late_start, missed_count_in, tempo_mismatch) to pick ONE highest leverage cue."
        ]
      }
    },
    "coach_to_policy_engine": {
      "GuidanceRequest": {
        "required": [
          "type",
          "t_ms",
          "mode",
          "backoff",
          "signals.timeSinceLastNoteOnMs",
          "signals.phraseBoundaryDetected",
          "signals.timeSincePhraseBoundaryMs",
          "signals.ignoreStreak",
          "signals.silencePreference",
          "signals.userExplicitQuiet",
          "decision.feedback_intent",
          "decision.cue_key",
          "constraints.max_cues"
        ],
        "notes": [
          "Policy engine decides whether to initiate now (token bucket + safe-window gating) and picks modality by weights + availability."
        ]
      }
    },
    "policy_engine_to_renderer": {
      "GuidanceEnvelope": {
        "required": [
          "type",
          "t_ms",
          "shouldInitiate",
          "reason",
          "selected.modality",
          "selected.tone",
          "selected.granularity",
          "selected.maxCues"
        ],
        "notes": [
          "Renderer should schedule delivery within timing.deliver_at_ms window if present; otherwise deliver ASAP at next safe window."
        ]
      }
    }
  }
}
```


The next step is **#2: Basic edge flags** — add (and verify) these flags in your segmenter output:

* `late_start`
* `missed_count_in`
* `extra_events_after_end`
* `partial_take`

### What to do concretely

1. **Emit flags on `TakeFinalized`** (even if false) so downstream logic can rely on them.
2. **Unit-test each flag** with synthetic streams:

   * Late start: skip first 1–2 expected slots.
   * Missed count-in: 2+ strums during the last count-in beat.
   * Extra after end: strums within `end_ms + post_roll_ms`.
   * Partial take: stop playing for `abort_pause_ms` before grid end.
3. **Plumb flags through contracts**

   * Segmenter → Analyzer: analyzer lowers confidence / adjusts interpretation for partial/missed count-in.
   * Analyzer → Coach: coach prefers “repeat / re-count-in” cues over timing critique when flags indicate take quality issues.

If you want the *very next artifact*, it’s a small test table: **scenario → input stream → expected flags** (so you can lock correctness before building more intelligence).


Below is the **lock-in test artifact** you want: a **scenario → input stream → expected flags** table for the **Take Segmenter**.

This is deliberately *boring and strict*. If these pass, you can trust everything upstream and safely build intelligence downstream.

---

# Take Segmenter Flag Test Table

*(Authoritative correctness spec)*

## Conventions (used in all tests)

* **Exercise**

  * 4/4, 2 bars
  * BPM = 80
  * Subdivision = 8th notes
  * Count-in = 2 beats

* **Derived**

  * `beat_ms = 750`
  * `slot_ms = 375`
  * `grid_start = T0 + 1500`
  * `grid_end = T0 + 1500 + 6000 = T0 + 7500`

* **Notation**

  * `E(t)` = strum event at `t_ms`
  * All events have `confidence ≥ minEventConfidence` unless stated
  * Streams are ordered by time

---

## Test 1 — Clean Take (Baseline)

### Scenario

Player waits for count-in and plays exactly 2 bars.

### Input stream

```
E(T0+1508), E(T0+1880), E(T0+2250), … 16 total, last ≈ T0+7350
(no events before grid_start, none after grid_end)
```

### Expected flags

| Flag                   | Value |
| ---------------------- | ----- |
| late_start             | false |
| missed_count_in        | false |
| extra_events_after_end | false |
| extra_bars             | false |
| partial_take           | false |
| tempo_mismatch         | false |
| restart_detected       | false |

**Purpose:** sanity check. This must pass before anything else.

---

## Test 2 — Late Start

### Scenario

Player misses the first beat, starts late but continues.

### Input stream

```
(no events until T0+1500+500)
E(T0+2000), E(T0+2375), … continues to end
```

### Expected flags

| Flag                   | Value |
| ---------------------- | ----- |
| late_start             | true  |
| missed_count_in        | false |
| extra_events_after_end | false |
| extra_bars             | false |
| partial_take           | false |
| tempo_mismatch         | false |
| restart_detected       | false |

**Key assertion**

* Segmenter **does not shift the grid**
* Late start is surfaced, not hidden

---

## Test 3 — Missed Count-In (Early Start)

### Scenario

Player starts strumming during the last beat of the count-in.

### Input stream

```
E(T0+900), E(T0+1200)   ← count-in beat 2
E(T0+1505), E(T0+1875), … full take
```

### Expected flags

| Flag                   | Value |
| ---------------------- | ----- |
| late_start             | false |
| missed_count_in        | true  |
| extra_events_after_end | false |
| extra_bars             | false |
| partial_take           | false |
| tempo_mismatch         | false |
| restart_detected       | false |

**Key assertion**

* Count-in strums are **not** graded
* Flag exists so coach can say “wait for count-in” instead of critiquing timing

---

## Test 4 — Early Stop (Partial Take)

### Scenario

Player stops halfway through bar 2.

### Input stream

```
E(T0+1500)…E(T0+4875)
(no events after; silence > abort_pause_ms before grid_end)
```

### Expected flags

| Flag                   | Value |
| ---------------------- | ----- |
| late_start             | false |
| missed_count_in        | false |
| extra_events_after_end | false |
| extra_bars             | false |
| partial_take           | true  |
| tempo_mismatch         | false |
| restart_detected       | false |

**Key assertion**

* Finalize reason = `USER_STOP`
* Analyzer/coach must treat as low-confidence

---

## Test 5 — Extra Events After End (Overrun)

### Scenario

Player completes 2 bars but keeps strumming slightly afterward.

### Input stream

```
E(T0+1500)…E(T0+7350)
E(T0+7700), E(T0+8050)
(no long continuation)
```

### Expected flags

| Flag                   | Value |
| ---------------------- | ----- |
| late_start             | false |
| missed_count_in        | false |
| extra_events_after_end | true  |
| extra_bars             | false |
| partial_take           | false |
| tempo_mismatch         | false |
| restart_detected       | false |

**Key assertion**

* Overrun is detected
* Take still finalized cleanly at grid end

---

## Test 6 — Extra Bars (Keeps Playing)

### Scenario

Player plays 4 bars straight through.

### Input stream

```
E(T0+1500)…E(T0+7350)
E(T0+8200)…E(T0+11200)
```

### Expected flags

| Flag                   | Value |
| ---------------------- | ----- |
| late_start             | false |
| missed_count_in        | false |
| extra_events_after_end | true  |
| extra_bars             | true  |
| partial_take           | false |
| tempo_mismatch         | false |
| restart_detected       | false |

**Key assertion**

* Segmenter **hard-stops** at 2 bars
* Extra bars are explicitly flagged

---

## Test 7 — Restart Mid-Take

### Scenario

Player starts, stops, then quickly restarts.

### Input stream

```
E(T0+1500), E(T0+1875), E(T0+2250)
(silence 1000ms)
E(T0+3500), E(T0+3680), E(T0+3850)
```

### Expected flags

| Flag                   | Value |
| ---------------------- | ----- |
| late_start             | false |
| missed_count_in        | false |
| extra_events_after_end | false |
| extra_bars             | false |
| partial_take           | false |
| tempo_mismatch         | false |
| restart_detected       | true  |

**Key assertion**

* First take finalized with reason = `RESTART`
* New take is armed immediately

---

## Test 8 — Tempo Mismatch (Too Fast or Slow)

### Scenario

Player consistently strums at ~60 BPM instead of 80 BPM.

### Input stream

```
Inter-event spacing ≈ 500ms (expected 375ms)
Enough events (≥ tempoMismatchMinPairs)
```

### Expected flags

| Flag                   | Value |
| ---------------------- | ----- |
| late_start             | false |
| missed_count_in        | false |
| extra_events_after_end | false |
| extra_bars             | false |
| partial_take           | false |
| tempo_mismatch         | true  |
| restart_detected       | false |

**Key assertion**

* Segmenter does *not* fix tempo
* Flag exists so coach can slow down / reinforce pulse

---

## Test 9 — Low-Confidence Noise Ignored

### Scenario

Mic noise generates weak detections.

### Input stream

```
E(T0+1600, confidence=0.3)
E(T0+1700, confidence=0.2)
(valid strums afterward)
```

### Expected flags

| Flag                  | Value |
| --------------------- | ----- |
| low_confidence_events | ≥ 2   |
| all other flags       | false |

**Key assertion**

* Noise does not create late_start / missed_count_in
* Noise count is surfaced for diagnostics only

---

## Test 10 — Ambiguous Count-In + Early Stop

### Scenario

Player strums during count-in, then stops early.

### Input stream

```
E(T0+1000), E(T0+1200)
E(T0+1500)…E(T0+3000)
(stop)
```

### Expected flags

| Flag             | Value |
| ---------------- | ----- |
| missed_count_in  | true  |
| partial_take     | true  |
| late_start       | false |
| restart_detected | false |

**Key assertion**

* Multiple flags can coexist
* Coach must prioritize **repeat / reset**, not critique

---

# Acceptance Criteria (Non-Negotiable)

A segmenter implementation is **correct** when:

1. Every scenario above produces **exactly** the expected flags
2. No additional flags are set
3. Grid start/end timestamps remain fixed
4. No test depends on downstream analysis logic

If this table passes, you can safely move on.

---

## What comes *after* this artifact (next real step)

Once these tests pass, the next artifact is:

> **Analyzer confidence downgrade rules**
> *(how flags + finalize_reason map to analysis_confidence and coaching suppression)*

That’s the bridge between *mechanics* and *musical intelligence*.

If you want, I’ll create that next.





Below is the **bridge spec** that turns segmenter mechanics into reliable “musical intelligence” behavior.

It defines:

1. how `TakeFinalized.flags` + `finalize_reason` map to **analysis confidence**
2. what the analyzer should still compute (and what it must not over-interpret)
3. how the coach converts low-confidence takes into **safe, non-annoying guidance**
4. how the policy engine clamps feedback when take quality is questionable

---

# Bridge Spec: Mechanics → Musical Intelligence

*(Segmenter → Analyzer confidence → Coach behavior → Policy clamps)*

## 1) Key Idea

A take can be “musically meaningful” **only if it’s mechanically trustworthy**.

So we explicitly separate:

* **Data quality** (was this take clean enough to grade?)
* **Performance quality** (how did they play?)

If data quality is low, the coach should **help the user produce a better take**, not critique the playing.

---

# 2) Analyzer Confidence Model

## 2.1 Inputs

From `TakeFinalized`:

* `finalize_reason ∈ {GRID_COMPLETE, USER_STOP, RESTART, CANCELLED}`
* flags:

  * `late_start`
  * `missed_count_in`
  * `extra_events_after_end`
  * `extra_bars`
  * `partial_take`
  * `tempo_mismatch`
  * `restart_detected`
  * `low_confidence_events` (count)
* additional optional signals (if available):

  * `event_confidence_mean`
  * `event_density` (events/sec)
  * `expected_event_count` (from pattern)

## 2.2 Outputs

Analyzer produces `TakeAnalysis.quality`:

* `analysis_confidence ∈ [0,1]`
* `gradeability ∈ {UNUSABLE, LOW, OK, HIGH}` (derived)
* `suppression_recommendation` (what types of coaching should be suppressed)

Example shape:

```json
{
  "quality": {
    "analysis_confidence": 0.62,
    "gradeability": "LOW",
    "suppression": {
      "suppress_timing_critique": true,
      "suppress_micro_feedback": true,
      "prefer_take_quality_prompt": true
    }
  }
}
```

---

# 3) Confidence Scoring (Deterministic, Testable)

## 3.1 Base confidence by finalize reason

Start with `c = base(finalize_reason)`:

* `GRID_COMPLETE` → `c = 0.95`
* `USER_STOP` → `c = 0.55`
* `RESTART` → `c = 0.45`
* `CANCELLED` → `c = 0.0` (UNUSABLE)

Rationale:

* If the take didn’t complete, timing metrics are still computable but are not representative.

## 3.2 Penalties by flags

Apply multiplicative penalties (stable, intuitive):

Let `penalty(f)` be:

* `missed_count_in`: `× 0.80`
* `late_start`: `× 0.85`
* `partial_take`: `× 0.70`
* `tempo_mismatch`: `× 0.85`
* `extra_events_after_end`: `× 0.95` (minor)
* `extra_bars`: `× 0.90` (minor for this take; more about exercise mismatch)
* `restart_detected`: `× 0.75`

Low-confidence event penalty:

* if `low_confidence_events >= 3` → `× 0.85`
* if `>= 10` → `× 0.70`

Then clamp `c` to `[0,1]`.

## 3.3 Gradeability thresholds

Map `c` to `gradeability`:

* `c < 0.20` → `UNUSABLE`
* `0.20 ≤ c < 0.55` → `LOW`
* `0.55 ≤ c < 0.80` → `OK`
* `c ≥ 0.80` → `HIGH`

---

# 4) Analyzer Rules: What to Compute vs What to Suppress

## 4.1 Always compute (even if LOW)

These are safe even when the take is messy:

* `hit_rate`, `miss_rate`, `extra_rate`
* `event_count`, `first_event_time`, `last_event_time`
* coarse timing stats (`p90_abs_offset_ms`) *but mark unreliable*
* `tempo mismatch indicator` (already flagged)

## 4.2 Compute but mark unreliable unless gradeability OK/HIGH

Only meaningful if the take has stable structure:

* `drift_ms_per_bar`
* fine-grain offset distribution interpretations (e.g., “consistently late”)
* direction adherence (if direction data exists)
* micro-level feedback triggers

## 4.3 Suppression recommendation logic

Set suppression booleans:

* If `gradeability == UNUSABLE`:

  * suppress everything except “reset take / count-in help”
* If `gradeability == LOW`:

  * suppress timing critique
  * suppress micro feedback
  * prefer take-quality guidance
* If `gradeability == OK`:

  * allow phrase-level feedback
  * avoid micro unless user opted-in
* If `gradeability == HIGH`:

  * allow standard coaching

Add specific suppressions:

* If `missed_count_in == true` → prefer “count-in clarity” cue
* If `partial_take == true` → prefer “finish 2 bars” cue
* If `tempo_mismatch == true` → prefer “tempo + pulse” cue over critique

---

# 5) Coach Behavior: Laddered Response by Gradeability

The coach chooses **exactly one** intent. The bridge tells it which category is appropriate.

## 5.1 Intent categories

1. **Take-quality intents** (fix the input)

* `wait_for_count_in`
* `start_on_downbeat`
* `finish_two_bars`
* `slow_down_enable_pulse`
* `reduce_false_triggers` (if lots of low-confidence noise)
* `clarify_exercise_length` (if extra bars)

2. **Musical-performance intents** (actual coaching)

* `subdivision_support`
* `backbeat_anchor`
* `reduce_motion`
* `increase_consistency`
* `raise_challenge`

## 5.2 Decision rule (bridge)

* If `UNUSABLE` → always take-quality intent
* If `LOW` → take-quality intent unless the user explicitly asked “grade me anyway”
* If `OK/HIGH` → musical-performance intent (normal)

## 5.3 Take-quality intent selection table

Choose based on which flag drove confidence down:

* `missed_count_in` → `wait_for_count_in` (or increase count-in beats)
* `late_start` → `start_on_downbeat`
* `partial_take` / `USER_STOP` → `finish_two_bars` (reduce tempo if needed)
* `tempo_mismatch` → `slow_down_enable_pulse`
* `extra_bars` → `clarify_exercise_length` (“we’re doing 2 bars—stop after 2”)
* high `low_confidence_events` → `reduce_false_triggers` (quiet environment / adjust detection)

## 5.4 Tone rules for take-quality intents

Take-quality feedback must feel like **setup for success**, not scolding:

* “Let’s do one more—wait for the count-in.”
* “Try starting exactly on the first click.”
* “Stop after 2 bars—then we’ll review.”

No judgment language.

---

# 6) Policy Engine Clamps Driven by Gradeability

Even if the coach wants to speak, the policy engine should treat low gradeability like “fragile moment.”

## 6.1 Clamp table

Given `gradeability`:

### UNUSABLE

* Force `BACKOFF >= L3` (summary only), unless user explicitly requests help
* No real-time prompts
* Offer one post-take card: “Want to try again?” + one hint

### LOW

* Clamp `max_cues = 1`
* Disallow `micro` granularity
* Prefer visual/haptic, avoid text/audio (less intrusive)
* Increase `min_pause_ms` by +800ms

### OK

* allow phrase-level
* micro only if user opted in and backoff ≤ L1

### HIGH

* normal policy

## 6.2 “Misread protection” for low gradeability

Low gradeability strongly correlates with frustration. So:

* decrease interrupt budget (IB) by 30–60%
* default to silence if ignore streak grows

---

# 7) End-to-End Examples (How It Should Feel)

## Example A: Missed count-in

Segmenter flags `missed_count_in=true`, reason `GRID_COMPLETE`.

* Analyzer: `c ~ 0.95 × 0.80 = 0.76` → gradeability OK
* But suppression: “prefer take-quality prompt” still true (because count-in error)
* Coach: “Wait for the count-in, then start on click”
* Policy: likely L1/L2, one cue, between phrases only

Outcome: user gets a gentle correction about *starting*, not a timing critique.

---

## Example B: Early stop

Reason `USER_STOP`, `partial_take=true`

* Analyzer: `c = 0.55 × 0.70 = 0.385` → gradeability LOW
* Coach: “Let’s try again—just 2 bars, slow it down to 76”
* Policy: clamps to summary-only or low-frequency cue

Outcome: no nitpicky feedback; just a clean retry path.

---

## Example C: Extra bars

Flags `extra_bars=true`, `extra_events_after_end=true`

* Analyzer: confidence slightly reduced, gradeability OK/HIGH
* Coach: “Stop after 2 bars—then I’ll show you one thing”
* Policy: minimal cue after take ends

Outcome: system keeps the exercise bounded without nagging.

---

# 8) Reference Implementation Snippet (Analyzer Confidence + Suppression)

```ts
export type Gradeability = "UNUSABLE" | "LOW" | "OK" | "HIGH";

export interface Suppression {
  suppressTimingCritique: boolean;
  suppressMicroFeedback: boolean;
  preferTakeQualityPrompt: boolean;
}

export function computeAnalysisQuality(tf: {
  timing: { finalize_reason: "GRID_COMPLETE"|"USER_STOP"|"RESTART"|"CANCELLED" };
  flags: {
    late_start: boolean;
    missed_count_in: boolean;
    extra_events_after_end: boolean;
    extra_bars: boolean;
    partial_take: boolean;
    tempo_mismatch: boolean;
    restart_detected: boolean;
    low_confidence_events: number;
  };
}): { analysis_confidence: number; gradeability: Gradeability; suppression: Suppression } {
  let c = 0;
  switch (tf.timing.finalize_reason) {
    case "GRID_COMPLETE": c = 0.95; break;
    case "USER_STOP": c = 0.55; break;
    case "RESTART": c = 0.45; break;
    case "CANCELLED": c = 0.0; break;
  }

  const f = tf.flags;
  if (f.missed_count_in) c *= 0.80;
  if (f.late_start) c *= 0.85;
  if (f.partial_take) c *= 0.70;
  if (f.tempo_mismatch) c *= 0.85;
  if (f.extra_events_after_end) c *= 0.95;
  if (f.extra_bars) c *= 0.90;
  if (f.restart_detected) c *= 0.75;

  if (f.low_confidence_events >= 10) c *= 0.70;
  else if (f.low_confidence_events >= 3) c *= 0.85;

  c = Math.max(0, Math.min(1, c));

  let gradeability: Gradeability = "UNUSABLE";
  if (c >= 0.80) gradeability = "HIGH";
  else if (c >= 0.55) gradeability = "OK";
  else if (c >= 0.20) gradeability = "LOW";

  const suppression: Suppression = {
    suppressTimingCritique: gradeability === "UNUSABLE" || gradeability === "LOW",
    suppressMicroFeedback: gradeability !== "HIGH",
    preferTakeQualityPrompt:
      gradeability === "UNUSABLE" ||
      gradeability === "LOW" ||
      f.missed_count_in ||
      f.partial_take ||
      f.tempo_mismatch ||
      f.late_start
  };

  return { analysis_confidence: c, gradeability, suppression };
}
```

---

# 9) What to Build Next After This Bridge

Once this bridge is implemented, the next step is straightforward and high leverage:

> **Coach intent router**:
> a deterministic mapping from `{gradeability + flags + key metrics}` → `one intent + bpm_next + verification`.

That router is where “musical intelligence” starts to feel like a teacher instead of a meter.

If you want, I’ll generate the **router table** (complete, deterministic) for the 2-bar strum slice.


You’re right to call that out. I treated “musical intelligence starts here” like a fact, when it’s really a **design choice**: the point where you stop emitting metrics and start choosing **one next teaching move**. That’s not guaranteed; it only becomes “teacher-like” if the router is well-designed and the policy engine keeps it respectful.

Here’s the **complete, deterministic router table** for the **2-bar strum slice**. No hype—just explicit mapping rules you can implement and test.

---

# 2-Bar Strum Coach Intent Router

Deterministic mapping from:

* `finalize_reason` + `flags`
* `gradeability` + `analysis_confidence`
* core metrics: `hit_rate`, `extra_rate`, `p90_abs_offset_ms`, `median_offset_ms`, `drift_ms_per_bar`, `tempo_mismatch`

to:

* `feedback_intent` (one)
* `cue_key` (one)
* `bpm_next`
* `next_take`
* `verification`

## A. Inputs

### Required input record (router)

```ts
type FinalizeReason = "GRID_COMPLETE" | "USER_STOP" | "RESTART" | "CANCELLED";
type Gradeability = "UNUSABLE" | "LOW" | "OK" | "HIGH";

type Flags = {
  late_start: boolean;
  missed_count_in: boolean;
  extra_events_after_end: boolean;
  extra_bars: boolean;
  partial_take: boolean;
  tempo_mismatch: boolean;
  restart_detected: boolean;
  low_confidence_events: number;
};

type Metrics = {
  hit_rate: number;            // 0..1
  extra_rate: number;          // extras / expected
  p90_abs_offset_ms: number;   // ms
  median_offset_ms: number;    // ms (negative = early, positive = late)
  drift_ms_per_bar: number;    // ms/bar (negative = rushing)
  stability: number;           // 0..1
};

type Quality = {
  analysis_confidence: number; // 0..1
  gradeability: Gradeability;
  suppression: {
    suppressTimingCritique: boolean;
    suppressMicroFeedback: boolean;
    preferTakeQualityPrompt: boolean;
  };
};
```

---

## B. Outputs

```ts
type FeedbackIntent =
  // take-quality (fix input)
  | "wait_for_count_in"
  | "start_on_downbeat"
  | "finish_two_bars"
  | "slow_down_enable_pulse"
  | "clarify_exercise_length"
  | "reduce_false_triggers"
  // performance coaching (fix playing)
  | "subdivision_support"
  | "backbeat_anchor"
  | "reduce_motion"
  | "timing_centering"
  | "raise_challenge"
  | "repeat_once";

type NextTake = "repeat_same" | "restart_with_count_in" | "switch_simpler";

type CoachDecision = {
  feedback_intent: FeedbackIntent;
  cue_key: string;            // content lookup key
  bpm_next: number;
  next_take: NextTake;
  count_in_beats_next?: number;
  max_cues: 1;                // always 1 for this slice
  verification: string;       // human-readable success criteria
};
```

---

## C. Constants (tunable but fixed for determinism)

Assume current exercise target:

* `bpm_target`
* `bpm_tolerance`

Thresholds:

* `PASS_hit = 0.85`

* `PASS_p90 = 45`

* `PASS_extra = 0.10`

* `ALMOST_hit = 0.75`

* `ALMOST_p90 = 65`

* drift threshold: `DRIFT_BAD = 30` ms/bar

* early/late bias: `BIAS_BAD = 20` ms median offset

* extras bad: `EXTRA_BAD = 0.15`

Tempo adjustment steps:

* `BPM_DOWN_SMALL = 3`
* `BPM_DOWN_MED = 6`
* `BPM_UP_SMALL = 3`

Count-in adjustment:

* if count-in problems repeat: bump to 4 beats

---

# D. Router Priority Order (first match wins)

This is the key: deterministic means **ordered rules**.

## D1) Hard stops

1. If `finalize_reason == "CANCELLED"`
   → no decision (or `repeat_same` with `cue_key="ready_when_you_are"`), but typically you’d drop it.

2. If `finalize_reason == "RESTART"` OR `flags.restart_detected == true`
   → **Decision:**

   * `feedback_intent="repeat_once"`
   * `cue_key="restart_detected_try_again"`
   * `bpm_next=bpm_target`
   * `next_take="restart_with_count_in"`
   * `verification="Complete 2 bars without restarting."`

> Rationale: don’t critique; the player already self-corrected.

---

## D2) Gradeability gates (take-quality overrides)

3. If `quality.gradeability == "UNUSABLE"`
   Choose based on flags (sub-order):

   * if `flags.low_confidence_events >= 10` → `reduce_false_triggers`
   * else → `repeat_once`

4. If `quality.gradeability == "LOW"`
   Choose based on flags (sub-order):

   * if `flags.partial_take || finalize_reason == "USER_STOP"` → `finish_two_bars`
   * else if `flags.missed_count_in` → `wait_for_count_in`
   * else if `flags.tempo_mismatch` → `slow_down_enable_pulse`
   * else if `flags.late_start` → `start_on_downbeat`
   * else → `repeat_once`

Output templates for these are in section E.

---

## D3) Special mechanical mismatches (still override musical critique)

5. If `flags.extra_bars == true`
   → `clarify_exercise_length` (keep bpm)

6. If `flags.missed_count_in == true` AND `quality.gradeability != "HIGH"`
   → `wait_for_count_in` (keep bpm or down small if also low hit-rate)

7. If `flags.late_start == true` AND `quality.gradeability != "HIGH"`
   → `start_on_downbeat`

---

## D4) Musical coaching (only if gradeability OK/HIGH and not suppressed)

From here down, we assume the take is clean enough to coach.

8. **Pass** condition:

* if `hit_rate ≥ PASS_hit` AND `p90_abs_offset_ms ≤ PASS_p90` AND `extra_rate ≤ PASS_extra`
  → `raise_challenge`

9. **Coverage failure** (misses):

* if `hit_rate < ALMOST_hit`
  → `slow_down_enable_pulse` (down medium)

10. **Extras problem**:

* if `extra_rate > EXTRA_BAD`
  → `reduce_motion` (down small)

11. **Drift problem**:

* if `abs(drift_ms_per_bar) > DRIFT_BAD`
  → `backbeat_anchor` (down small or keep)

12. **Consistently early/late (centering)**:

* if `abs(median_offset_ms) > BIAS_BAD`
  → `timing_centering` (keep bpm)

13. **Timing spread (needs subdivision support)**:

* if `p90_abs_offset_ms > PASS_p90`
  → `subdivision_support` (keep bpm)

14. Otherwise:
    → `repeat_once`

---

# E. Output Templates (exact decisions)

Below are the exact `CoachDecision` outputs per intent.
All return `max_cues: 1`.

### 1) wait_for_count_in

* `feedback_intent="wait_for_count_in"`
* `cue_key="wait_for_count_in_then_enter"`
* `bpm_next=bpm_target`
* `next_take="restart_with_count_in"`
* if this happens 2 takes in a row (track outside router): `count_in_beats_next=4`
* `verification="Start on the first click and play 2 bars."`

### 2) start_on_downbeat

* `cue_key="start_on_downbeat"`
* `bpm_next=bpm_target`
* `next_take="restart_with_count_in"`
* `verification="First strum lands within ±1 slot of the downbeat, then complete 2 bars."`

### 3) finish_two_bars

* `cue_key="finish_two_bars_slow_if_needed"`
* `bpm_next=max(bpm_target - BPM_DOWN_SMALL, 40)`
* `next_take="repeat_same"`
* `verification="Complete full 2 bars without stopping."`

### 4) slow_down_enable_pulse

* `cue_key="slow_down_and_use_pulse"`
* `bpm_next=max(bpm_target - BPM_DOWN_MED, 40)`
* `next_take="repeat_same"`
* `verification="Hit-rate ≥ 0.75 on the next take."`

### 5) clarify_exercise_length

* `cue_key="stop_after_two_bars"`
* `bpm_next=bpm_target`
* `next_take="repeat_same"`
* `verification="Stop after 2 bars; we’ll review right after."`

### 6) reduce_false_triggers

* `cue_key="detection_noise_reduce"`
* `bpm_next=bpm_target`
* `next_take="repeat_once"`
* `verification="Try again in a quieter moment; we need a clean signal."`

---

### 7) subdivision_support

* `cue_key="add_subdivision_pulse"`
* `bpm_next=bpm_target`
* `next_take="repeat_same"`
* `verification="p90 ≤ 45ms on 2 of next 3 takes."`

### 8) backbeat_anchor

* `cue_key="emphasize_2_and_4"`
* `bpm_next=max(bpm_target - BPM_DOWN_SMALL, 40)`
* `next_take="repeat_same"`
* `verification="Drift magnitude decreases next take (|drift| down), while hit-rate stays ≥ 0.75."`

### 9) reduce_motion

* `cue_key="smaller_strum_less_extra"`
* `bpm_next=max(bpm_target - BPM_DOWN_SMALL, 40)`
* `next_take="repeat_same"`
* `verification="extra_rate ≤ 0.10 next take."`

### 10) timing_centering

* `cue_key="aim_center_of_click"`
* `bpm_next=bpm_target`
* `next_take="repeat_same"`
* `verification="|median_offset_ms| ≤ 15ms on next take (or trending toward 0)."`

### 11) raise_challenge

* `cue_key="nice_lock_in_bump_tempo"`
* `bpm_next=bpm_target + BPM_UP_SMALL`
* `next_take="repeat_same"`
* `verification="Maintain pass criteria at +3 bpm for 2 takes."`

### 12) repeat_once

* `cue_key="one_more_take_same_tempo"`
* `bpm_next=bpm_target`
* `next_take="repeat_same"`
* `verification="Repeat once; we’ll pick the next focus after that."`

---

# F. Reference Implementation (Router)

```ts
export function routeCoachDecision(
  finalize_reason: "GRID_COMPLETE"|"USER_STOP"|"RESTART"|"CANCELLED",
  bpm_target: number,
  flags: Flags,
  metrics: Metrics,
  quality: Quality
): CoachDecision | null {

  const PASS_hit = 0.85, PASS_p90 = 45, PASS_extra = 0.10;
  const ALMOST_hit = 0.75, ALMOST_p90 = 65;
  const DRIFT_BAD = 30;
  const BIAS_BAD = 20;
  const EXTRA_BAD = 0.15;

  const BPM_DOWN_SMALL = 3, BPM_DOWN_MED = 6, BPM_UP_SMALL = 3;

  const mk = (feedback_intent: FeedbackIntent, cue_key: string, bpm_next: number, next_take: NextTake, verification: string, count_in_beats_next?: number): CoachDecision => ({
    feedback_intent,
    cue_key,
    bpm_next,
    next_take,
    count_in_beats_next,
    max_cues: 1,
    verification
  });

  // D1 Hard stops
  if (finalize_reason === "CANCELLED") return null;

  if (finalize_reason === "RESTART" || flags.restart_detected) {
    return mk("repeat_once","restart_detected_try_again",bpm_target,"restart_with_count_in","Complete 2 bars without restarting.");
  }

  // D2 Gradeability gates
  if (quality.gradeability === "UNUSABLE") {
    if (flags.low_confidence_events >= 10) {
      return mk("reduce_false_triggers","detection_noise_reduce",bpm_target,"repeat_once","Try again in a quieter moment; we need a clean signal.");
    }
    return mk("repeat_once","one_more_take_same_tempo",bpm_target,"repeat_once","Try again; let’s get a clean take.");
  }

  if (quality.gradeability === "LOW") {
    if (flags.partial_take || finalize_reason === "USER_STOP") {
      return mk("finish_two_bars","finish_two_bars_slow_if_needed",Math.max(bpm_target - BPM_DOWN_SMALL, 40),"repeat_same","Complete full 2 bars without stopping.");
    }
    if (flags.missed_count_in) {
      return mk("wait_for_count_in","wait_for_count_in_then_enter",bpm_target,"restart_with_count_in","Start on the first click and play 2 bars.");
    }
    if (flags.tempo_mismatch) {
      return mk("slow_down_enable_pulse","slow_down_and_use_pulse",Math.max(bpm_target - BPM_DOWN_MED, 40),"repeat_same","Hit-rate ≥ 0.75 on the next take.");
    }
    if (flags.late_start) {
      return mk("start_on_downbeat","start_on_downbeat",bpm_target,"restart_with_count_in","Start right on the downbeat, then complete 2 bars.");
    }
    return mk("repeat_once","one_more_take_same_tempo",bpm_target,"repeat_same","One more take; keep it simple and steady.");
  }

  // D3 Mechanical mismatch overrides
  if (flags.extra_bars) {
    return mk("clarify_exercise_length","stop_after_two_bars",bpm_target,"repeat_same","Stop after 2 bars; we’ll review right after.");
  }
  if (flags.missed_count_in && quality.gradeability !== "HIGH") {
    return mk("wait_for_count_in","wait_for_count_in_then_enter",bpm_target,"restart_with_count_in","Start on the first click and play 2 bars.");
  }
  if (flags.late_start && quality.gradeability !== "HIGH") {
    return mk("start_on_downbeat","start_on_downbeat",bpm_target,"restart_with_count_in","Start right on the downbeat, then complete 2 bars.");
  }

  // D4 Musical coaching
  const pass = metrics.hit_rate >= PASS_hit && metrics.p90_abs_offset_ms <= PASS_p90 && metrics.extra_rate <= PASS_extra;
  if (pass) {
    return mk("raise_challenge","nice_lock_in_bump_tempo",bpm_target + BPM_UP_SMALL,"repeat_same","Maintain pass criteria at +3 bpm for 2 takes.");
  }

  if (metrics.hit_rate < ALMOST_hit) {
    return mk("slow_down_enable_pulse","slow_down_and_use_pulse",Math.max(bpm_target - BPM_DOWN_MED, 40),"repeat_same","Hit-rate ≥ 0.75 on the next take.");
  }

  if (metrics.extra_rate > EXTRA_BAD) {
    return mk("reduce_motion","smaller_strum_less_extra",Math.max(bpm_target - BPM_DOWN_SMALL, 40),"repeat_same","extra_rate ≤ 0.10 next take.");
  }

  if (Math.abs(metrics.drift_ms_per_bar) > DRIFT_BAD) {
    return mk("backbeat_anchor","emphasize_2_and_4",Math.max(bpm_target - BPM_DOWN_SMALL, 40),"repeat_same","Drift reduces next take while hit-rate stays ≥ 0.75.");
  }

  if (Math.abs(metrics.median_offset_ms) > BIAS_BAD) {
    return mk("timing_centering","aim_center_of_click",bpm_target,"repeat_same","|median_offset_ms| trends toward 0 (≤ 15ms ideal).");
  }

  if (metrics.p90_abs_offset_ms > PASS_p90) {
    return mk("subdivision_support","add_subdivision_pulse",bpm_target,"repeat_same","p90 ≤ 45ms on 2 of next 3 takes.");
  }

  return mk("repeat_once","one_more_take_same_tempo",bpm_target,"repeat_same","Repeat once; we’ll pick the next focus after that.");
}
```

---

## What you can test next (to prove this isn’t hand-wavy)

Create unit tests that assert:

* given a flag combination + metric set → router returns exactly one intent (and correct bpm delta)
* ordering is respected (e.g., `LOW gradeability` always overrides “pass” metrics if both present due to weird inputs)
* no output ever has `max_cues != 1`

If you want, paste your current `TakeAnalysis` shape and I’ll align the router exactly to your actual fields (names/types) so you can drop it in without adapters.





