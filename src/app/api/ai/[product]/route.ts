import { NextResponse } from "next/server";
import {
  isAiProduct,
  normalizeLocalAiResult,
  postLocalAiExperience
} from "@/lib/ai/consultation";

type RouteContext = {
  params: Promise<{
    product: string;
  }>;
};

export async function POST(request: Request, context: RouteContext) {
  const { product } = await context.params;

  if (!isAiProduct(product)) {
    return NextResponse.json(
      { message: "Unsupported MirrorAI product." },
      { status: 404 }
    );
  }

  try {
    const formData = await request.formData();
    const controller = new AbortController();
    const timeoutMs = Number(process.env.MIRRORAI_AI_TIMEOUT_MS ?? 120000);
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    const response = await postLocalAiExperience(product, formData, {
      signal: controller.signal
    }).finally(() => clearTimeout(timer));

    const payload = (await response.json()) as unknown;

    if (!response.ok) {
      const message =
        payload && typeof payload === "object" && "message" in payload
          ? String((payload as { message: unknown }).message)
          : payload && typeof payload === "object" && "detail" in payload
            ? String((payload as { detail: unknown }).detail)
          : "The local AI backend could not process this image.";
      return NextResponse.json({ message }, { status: response.status });
    }

    return NextResponse.json(normalizeLocalAiResult(payload));
  } catch (error) {
    const message =
      error instanceof Error && error.name === "AbortError"
        ? "The local AI backend timed out while processing this image."
        : "Start the local FastAPI backend with `uvicorn python.main:app --reload --port 8000` and try again.";

    return NextResponse.json({ message }, { status: 502 });
  }
}
