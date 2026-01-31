/**
 * Smart Guitar Guidance Engine
 * Reference implementation for the policy matrix + token bucket + safe-window gating.
 *
 * Drop-in: provide config (JSON validated against guidance-policy.schema.json),
 * feed it updates, and call decide() each tick or when you consider initiating
 * an intervention.
 *
 * @see ../schemas/guidance-policy.schema.json
 * @see ../schemas/coach-decision.schema.json
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
    const cooldownMs = this.config.runtime.tokenBucket.cooldownAfterInterventionMs;
    if (!this.bucket.canSpend(signals.nowMs, cooldownMs)) {
      // Stochastic path if enabled and cooldown passed
      if (this.config.runtime.tokenBucket.stochasticRounding) {
        const tokens = this.bucket.getTokens();
        if (tokens > 0 && tokens < 1) {
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

  /** Call when you actually executed an intervention to keep timing consistent. */
  recordInterventionExecuted(nowMs: number) {
    void nowMs;
  }

  /** Compute effective policy after applying global clamps. */
  private effectivePolicy(mode: Mode, backoff: Backoff, signals: SessionSignals): GuidancePolicy {
    const base = structuredClone(this.config.matrix[mode][backoff]) as GuidancePolicy;

    // Normalize weights against availability
    base.modalityWeights = normalizeWeights(base.modalityWeights, this.config.runtime.modalityAvailability);

    // Global: backoff >= L2 forces between-phrase-only (if enabled)
    if (this.config.runtime.globalRules.backoffAtOrAboveL2ForcesBetweenPhraseOnly) {
      if (backoffRank(backoff) >= backoffRank("L2")) base.betweenPhraseOnly = true;
    }

    // Ignore streak clamp
    const clampRules = this.config.runtime.globalRules.ignoreStreakClamp;
    if (signals.ignoreStreak >= clampRules.ignoreStreakThreshold) {
      base.interruptBudgetPerMin = Math.min(base.interruptBudgetPerMin, clampRules.maxInterruptBudgetPerMin);
      base.minPauseMs = (base.minPauseMs ?? 0) + clampRules.extraPauseMs;
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
      const scale = Math.max(0, (conf - 0.4) / 0.3);
      base.interruptBudgetPerMin *= clamp01(scale);
      base.minPauseMs = (base.minPauseMs ?? 0) + Math.floor((1 - scale) * 800);
    }

    // PERFORMANCE global constraints
    if (mode === "PERFORMANCE") {
      if (this.config.runtime.globalRules.performanceNeverInstructive && base.tone === "instructive") {
        base.tone = "supportive";
      }
      if (this.config.runtime.globalRules.performanceNoMicroGranularity && base.granularity === "micro") {
        base.granularity = "summary";
      }
      base.interruptBudgetPerMin = Math.min(base.interruptBudgetPerMin, 0.5);
    }

    // Backoff L3/L4 override: no real-time
    if (backoff === "L3") {
      base.realTimeEnabled = false;
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
    const baseMinPause = policy.minPauseMs ?? 0;
    const backoffMinPause = this.config.runtime.safeWindow.minPauseMsByBackoff[backoff];
    const requiredPause = Math.max(baseMinPause, backoffMinPause);

    if (signals.timeSinceLastNoteOnMs < requiredPause) {
      return { ok: false, reason: "insufficient_pause" };
    }

    const pbForceAt = this.config.runtime.safeWindow.phraseBoundaryRequiredAtOrAboveBackoff;
    const forced = backoffRank(backoff) >= backoffRank(pbForceAt);
    const requirePhraseBoundary = policy.betweenPhraseOnly || forced;

    if (requirePhraseBoundary) {
      if (!signals.phraseBoundaryDetected) return { ok: false, reason: "no_phrase_boundary" };
      if (signals.timeSincePhraseBoundaryMs < this.config.runtime.safeWindow.phraseBoundaryDebounceMs) {
        return { ok: false, reason: "phrase_boundary_debounce" };
      }
    }

    if (mode === "PERFORMANCE") {
      if (signals.timeSinceLastNoteOnMs < Math.max(requiredPause, 2000)) {
        return { ok: false, reason: "performance_extra_pause" };
      }
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
    (this.bucket as any).tokens = 0;
    (this.bucket as any).lastInterventionMs = nowMs;
  }
}
