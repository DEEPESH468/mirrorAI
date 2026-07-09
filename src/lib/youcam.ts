import type { ExperienceCategory } from "@/types/try-on";
import { getProductByCategory } from "@/lib/styles";

export type YouCamProxyResult = {
  imageUrl?: string;
  imageBase64?: string;
  providerResponse: unknown;
};

function getConfig(category: ExperienceCategory) {
  const product = getProductByCategory(category);
  const apiKey = process.env.YOUCAM_API_KEY;
  const baseUrl = process.env.YOUCAM_API_BASE_URL;
  const endpoint = product ? process.env[product.endpointEnv] : undefined;

  if (!apiKey || !baseUrl || !endpoint) {
    throw new Error(
      `YouCam API is not configured for ${category}. Set YOUCAM_API_KEY, YOUCAM_API_BASE_URL, and the matching endpoint variable.`
    );
  }

  return {
    apiKey,
    url: new URL(endpoint, baseUrl).toString(),
    timeoutMs: Number(process.env.YOUCAM_API_TIMEOUT_MS ?? 60000)
  };
}

function normalizeProviderResponse(payload: unknown): YouCamProxyResult {
  const record = payload && typeof payload === "object" ? (payload as Record<string, unknown>) : {};
  const imageUrl =
    typeof record.result_url === "string"
      ? record.result_url
      : typeof record.image_url === "string"
        ? record.image_url
        : typeof record.url === "string"
          ? record.url
          : undefined;
  const imageBase64 =
    typeof record.result_image === "string"
      ? record.result_image
      : typeof record.image_base64 === "string"
        ? record.image_base64
        : undefined;

  return {
    imageUrl,
    imageBase64,
    providerResponse: payload
  };
}

export async function requestYouCamExperience(
  category: ExperienceCategory,
  formData: FormData
): Promise<YouCamProxyResult> {
  const config = getConfig(category);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), config.timeoutMs);

  try {
    const response = await fetch(config.url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${config.apiKey}`,
        "X-API-Key": config.apiKey
      },
      body: formData,
      signal: controller.signal
    });

    const contentType = response.headers.get("content-type") ?? "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : { result_url: await response.text() };

    if (!response.ok) {
      const message =
        payload && typeof payload === "object" && "message" in payload
          ? String((payload as { message: unknown }).message)
          : "YouCam API request failed.";
      throw new Error(message);
    }

    return normalizeProviderResponse(payload);
  } finally {
    clearTimeout(timer);
  }
}
