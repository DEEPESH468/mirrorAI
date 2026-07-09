import type { ExperienceCategory } from "@/types/try-on";
import { createAiModule } from "@/lib/ai/consultation";
import type { AiModuleContract } from "@/lib/ai/consultation";

export const faceModule: AiModuleContract = createAiModule({
  id: "face",
  product: "face-shape",
  status: "not_implemented"
});

export type { AiModuleContract, ExperienceCategory };
