import type { ExperienceCategory, ExperienceResult } from "@/types/try-on";

export const aiProducts = [
  "skin-analysis",
  "makeup",
  "hair-color",
  "hairstyle",
  "beard",
  "face-shape",
  "hair-analysis"
] as const satisfies readonly ExperienceCategory[];

export type AiModuleStatus = "completed" | "not_implemented" | "skipped";

export type AiModuleContract = {
  id: string;
  product?: ExperienceCategory;
  status: AiModuleStatus;
};

export type LocalAiResult = ExperienceResult & {
  report?: Record<string, unknown>;
};

export function createAiModule(
  module: AiModuleContract
): AiModuleContract {
  return module;
}

export function isAiProduct(value: string): value is ExperienceCategory {
  return (aiProducts as readonly string[]).includes(value);
}

export function normalizeLocalAiResult(payload: unknown): LocalAiResult {
  const record = payload && typeof payload === "object" ? (payload as Record<string, unknown>) : {};

  return {
    imageUrl: typeof record.imageUrl === "string" ? record.imageUrl : undefined,
    imageBase64: typeof record.imageBase64 === "string" ? record.imageBase64 : undefined,
    aiResponse: record.aiResponse ?? record,
    report:
      record.report && typeof record.report === "object"
        ? (record.report as Record<string, unknown>)
        : undefined
  };
}

export function getLocalAiUrl(product: ExperienceCategory) {
  const baseUrl = process.env.MIRRORAI_AI_BACKEND_URL ?? "http://127.0.0.1:8000";
  return new URL(`/api/${product}`, baseUrl).toString();
}

export async function postLocalAiExperience(
  product: ExperienceCategory,
  formData: FormData,
  init?: Pick<RequestInit, "signal">
): Promise<Response> {
  return fetch(getLocalAiUrl(product), {
    method: "POST",
    body: formData,
    signal: init?.signal
  });
}
