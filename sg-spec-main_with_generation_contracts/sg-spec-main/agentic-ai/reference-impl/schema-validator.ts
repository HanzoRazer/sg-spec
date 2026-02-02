/**
 * Schema Validator
 *
 * Pre-flight validation of pipeline inputs against JSON schemas.
 * Catches drift immediately when schemas change.
 *
 * @see ../schemas/take-events.schema.json
 * @see ../schemas/coach-decision.schema.json
 * @see ../schemas/renderer-payloads.schema.json
 * @see ../schemas/guidance-policy.schema.json
 */

import Ajv2020, { type ValidateFunction, type ErrorObject } from "ajv/dist/2020";
import addFormats from "ajv-formats";
import fs from "node:fs";
import path from "node:path";

// ============================================================================
// Types
// ============================================================================

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

export interface ValidationError {
  path: string;
  message: string;
  keyword: string;
  params: Record<string, unknown>;
}

export type SchemaName =
  | "TakeAnalysis"
  | "TakeFinalized"
  | "SegmenterFlags"
  | "RendererEnvelope"
  | "PulsePayload"
  | "MusicalContext";

// ============================================================================
// Schema Loading
// ============================================================================

const SCHEMAS_DIR = path.join(__dirname, "..", "schemas");

function loadSchema(filename: string): object {
  const filePath = path.join(SCHEMAS_DIR, filename);
  const content = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(content);
}

// Lazy-load schemas
let takeEventsSchema: object | null = null;
let coachDecisionSchema: object | null = null;
let rendererPayloadsSchema: object | null = null;
let guidancePolicySchema: object | null = null;

function getTakeEventsSchema(): object {
  if (!takeEventsSchema) {
    takeEventsSchema = loadSchema("take-events.schema.json");
  }
  return takeEventsSchema;
}

function getCoachDecisionSchema(): object {
  if (!coachDecisionSchema) {
    coachDecisionSchema = loadSchema("coach-decision.schema.json");
  }
  return coachDecisionSchema;
}

function getRendererPayloadsSchema(): object {
  if (!rendererPayloadsSchema) {
    rendererPayloadsSchema = loadSchema("renderer-payloads.schema.json");
  }
  return rendererPayloadsSchema;
}

function getGuidancePolicySchema(): object {
  if (!guidancePolicySchema) {
    guidancePolicySchema = loadSchema("guidance-policy.schema.json");
  }
  return guidancePolicySchema;
}

// ============================================================================
// Ajv Instance
// ============================================================================

let ajvInstance: Ajv2020 | null = null;

function getAjv(): Ajv2020 {
  if (!ajvInstance) {
    ajvInstance = new Ajv2020({
      allErrors: true,
      strict: false,
      validateFormats: true,
    });
    addFormats(ajvInstance);

    // Add all schemas
    ajvInstance.addSchema(getTakeEventsSchema(), "take-events");
    ajvInstance.addSchema(getCoachDecisionSchema(), "coach-decision");
    ajvInstance.addSchema(getRendererPayloadsSchema(), "renderer-payloads");
    ajvInstance.addSchema(getGuidancePolicySchema(), "guidance-policy");
  }
  return ajvInstance;
}

// ============================================================================
// Compiled Validators (cached)
// ============================================================================

const validatorCache = new Map<string, ValidateFunction>();

function getValidator(schemaId: string, defPath: string): ValidateFunction {
  const cacheKey = `${schemaId}#${defPath}`;
  let validator = validatorCache.get(cacheKey);

  if (!validator) {
    const ajv = getAjv();
    const refUri = `${schemaId}#/$defs/${defPath}`;
    validator = ajv.getSchema(refUri);

    if (!validator) {
      throw new Error(`Schema definition not found: ${refUri}`);
    }

    validatorCache.set(cacheKey, validator);
  }

  return validator;
}

// ============================================================================
// Error Formatting
// ============================================================================

function formatErrors(errors: ErrorObject[] | null | undefined): ValidationError[] {
  if (!errors) return [];

  return errors.map((err) => ({
    path: err.instancePath || "/",
    message: err.message || "Unknown error",
    keyword: err.keyword,
    params: err.params as Record<string, unknown>,
  }));
}

// ============================================================================
// Public Validation Functions
// ============================================================================

/**
 * Validate TakeAnalysis object against schema.
 */
export function validateTakeAnalysis(data: unknown): ValidationResult {
  const validator = getValidator("take-events", "TakeAnalysis");
  const valid = validator(data);
  return { valid: !!valid, errors: formatErrors(validator.errors) };
}

/**
 * Validate TakeFinalized object against schema.
 */
export function validateTakeFinalized(data: unknown): ValidationResult {
  const validator = getValidator("take-events", "TakeFinalized");
  const valid = validator(data);
  return { valid: !!valid, errors: formatErrors(validator.errors) };
}

/**
 * Validate SegmenterFlags-like object.
 * Note: SegmenterFlags is defined inline in TakeFinalized, so we validate structure manually.
 */
export function validateSegmenterFlags(data: unknown): ValidationResult {
  const errors: ValidationError[] = [];

  if (typeof data !== "object" || data === null) {
    return { valid: false, errors: [{ path: "/", message: "Expected object", keyword: "type", params: {} }] };
  }

  const flags = data as Record<string, unknown>;
  const requiredBooleans = [
    "late_start",
    "missed_count_in",
    "extra_events_after_end",
    "extra_bars",
    "partial_take",
    "tempo_mismatch",
    "restart_detected",
  ];

  for (const field of requiredBooleans) {
    if (typeof flags[field] !== "boolean") {
      errors.push({
        path: `/${field}`,
        message: `Expected boolean`,
        keyword: "type",
        params: { expected: "boolean", actual: typeof flags[field] },
      });
    }
  }

  if (typeof flags.low_confidence_events !== "number") {
    errors.push({
      path: "/low_confidence_events",
      message: "Expected number",
      keyword: "type",
      params: { expected: "number", actual: typeof flags.low_confidence_events },
    });
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Validate RendererEnvelope object against schema.
 */
export function validateRendererEnvelope(data: unknown): ValidationResult {
  const validator = getValidator("renderer-payloads", "RendererEnvelope");
  const valid = validator(data);
  return { valid: !!valid, errors: formatErrors(validator.errors) };
}

/**
 * Validate PulsePayload object against schema.
 */
export function validatePulsePayload(data: unknown): ValidationResult {
  const validator = getValidator("renderer-payloads", "PulsePayload");
  const valid = validator(data);
  return { valid: !!valid, errors: formatErrors(validator.errors) };
}

/**
 * Validate MusicalContext object against schema.
 */
export function validateMusicalContext(data: unknown): ValidationResult {
  const validator = getValidator("renderer-payloads", "MusicalContext");
  const valid = validator(data);
  return { valid: !!valid, errors: formatErrors(validator.errors) };
}

// ============================================================================
// Aggregate Validation for Golden Runner Input
// ============================================================================

export interface GoldenInputValidationResult {
  valid: boolean;
  takeAnalysis: ValidationResult;
  segmenterFlags: ValidationResult;
  musical: ValidationResult;
}

/**
 * Validate all inputs for golden-runner pipeline.
 * Returns detailed results for each component.
 */
export function validateGoldenInput(input: {
  takeAnalysis: unknown;
  segmenterFlags: unknown;
  musical: unknown;
}): GoldenInputValidationResult {
  const takeAnalysis = validateTakeAnalysis(input.takeAnalysis);
  const segmenterFlags = validateSegmenterFlags(input.segmenterFlags);
  const musical = validateMusicalContext(input.musical);

  return {
    valid: takeAnalysis.valid && segmenterFlags.valid && musical.valid,
    takeAnalysis,
    segmenterFlags,
    musical,
  };
}

/**
 * Validate golden-runner output envelope.
 */
export function validateGoldenOutput(envelope: unknown): ValidationResult {
  if (envelope === null) {
    return { valid: true, errors: [] }; // null is valid (no envelope produced)
  }
  return validateRendererEnvelope(envelope);
}

// ============================================================================
// Convenience: Throw on Invalid
// ============================================================================

export class SchemaValidationError extends Error {
  constructor(
    public readonly schemaName: string,
    public readonly errors: ValidationError[]
  ) {
    const messages = errors.map((e) => `${e.path}: ${e.message}`).join("; ");
    super(`Schema validation failed for ${schemaName}: ${messages}`);
    this.name = "SchemaValidationError";
  }
}

/**
 * Validate and throw if invalid.
 */
export function assertValidTakeAnalysis(data: unknown): void {
  const result = validateTakeAnalysis(data);
  if (!result.valid) {
    throw new SchemaValidationError("TakeAnalysis", result.errors);
  }
}

/**
 * Validate and throw if invalid.
 */
export function assertValidSegmenterFlags(data: unknown): void {
  const result = validateSegmenterFlags(data);
  if (!result.valid) {
    throw new SchemaValidationError("SegmenterFlags", result.errors);
  }
}

/**
 * Validate and throw if invalid.
 */
export function assertValidMusicalContext(data: unknown): void {
  const result = validateMusicalContext(data);
  if (!result.valid) {
    throw new SchemaValidationError("MusicalContext", result.errors);
  }
}

/**
 * Validate and throw if invalid.
 */
export function assertValidRendererEnvelope(data: unknown): void {
  if (data === null) return; // null is valid
  const result = validateRendererEnvelope(data);
  if (!result.valid) {
    throw new SchemaValidationError("RendererEnvelope", result.errors);
  }
}

/**
 * Validate all golden-runner inputs and throw if any are invalid.
 */
export function assertValidGoldenInput(input: {
  takeAnalysis: unknown;
  segmenterFlags: unknown;
  musical: unknown;
}): void {
  assertValidTakeAnalysis(input.takeAnalysis);
  assertValidSegmenterFlags(input.segmenterFlags);
  assertValidMusicalContext(input.musical);
}
