import type { ExperienceCategory } from "@/types/try-on";
import { createAiModule } from "@/lib/ai/consultation";
import type { AiModuleContract } from "@/lib/ai/consultation";

export const faceModule: AiModuleContract = createAiModule({
  id: "face",
  product: "face-shape",
  status: "completed"
});

export type FaceShape =
  | "oval"
  | "round"
  | "square"
  | "rectangle"
  | "diamond"
  | "heart"
  | "triangle";

export type FaceCoreEndpoint = "detect" | "mesh" | "shape" | "analyze";

export function getFaceCoreUrl(endpoint: FaceCoreEndpoint) {
  const baseUrl = process.env.MIRRORAI_AI_BACKEND_URL ?? "http://127.0.0.1:8000";
  return new URL(`/api/face/${endpoint}`, baseUrl).toString();
}

export type { AiModuleContract, ExperienceCategory };
