import { createAiModule } from "@/lib/ai/consultation";

export type ConsultationRecommendation = {
  title: string;
  reason: string;
  confidence: number;
};

export const recommendationModule = createAiModule({
  id: "recommendation",
  status: "not_implemented"
});
