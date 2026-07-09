export type ExperienceCategory =
  | "skin-analysis"
  | "makeup"
  | "hair-color"
  | "hairstyle"
  | "beard"
  | "face-shape"
  | "hair-analysis";

export type ExperienceMode = "analysis" | "try-on";

export type ExperienceOption = {
  id: string;
  category: ExperienceCategory;
  name: string;
  description: string;
  accent: string;
  localField?: string;
};

export type ExperienceProduct = {
  id: ExperienceCategory;
  mode: ExperienceMode;
  name: string;
  shortName: string;
  description: string;
  eyebrow: string;
  optionLabel?: string;
};

export type ExperienceResult = {
  imageUrl?: string;
  imageBase64?: string;
  aiResponse: unknown;
  report?: Record<string, unknown>;
};
