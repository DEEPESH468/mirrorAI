import type {
  ExperienceCategory,
  ExperienceOption,
  ExperienceProduct
} from "@/types/try-on";

export const experienceProducts: ExperienceProduct[] = [
  {
    id: "skin-analysis",
    mode: "analysis",
    name: "AI Skin Analysis",
    shortName: "Skin",
    eyebrow: "Skin intelligence",
    description:
      "Scan a face image for skin concerns and turn the results into consultation-ready recommendations."
  },
  {
    id: "makeup",
    mode: "try-on",
    name: "Virtual Makeup Try-On",
    shortName: "Makeup",
    eyebrow: "Makeup artistry",
    description:
      "Preview lipstick, foundation, eye makeup, blush, contour, or complete salon looks before a service.",
    optionLabel: "Select a makeup look"
  },
  {
    id: "hair-color",
    mode: "try-on",
    name: "Hair Color Simulation",
    shortName: "Color",
    eyebrow: "Color preview",
    description:
      "Try refined salon shades before committing to color, gloss, highlights, or transformation work.",
    optionLabel: "Select a shade"
  },
  {
    id: "hairstyle",
    mode: "try-on",
    name: "Hairstyle Try-On",
    shortName: "Haircut",
    eyebrow: "Cut preview",
    description:
      "Preview cuts and silhouettes for all clients, then refine the final direction with a stylist.",
    optionLabel: "Select a hairstyle"
  },
  {
    id: "beard",
    mode: "try-on",
    name: "Beard Style Simulation",
    shortName: "Beard",
    eyebrow: "Grooming preview",
    description:
      "Preview beard and moustache styles for grooming, shaping, and consultation services.",
    optionLabel: "Select a beard style"
  },
  {
    id: "face-shape",
    mode: "analysis",
    name: "Face Shape Analysis",
    shortName: "Face Shape",
    eyebrow: "Facial mapping",
    description:
      "Analyze face shape and attributes to guide haircuts, contouring, makeup, and grooming direction."
  },
  {
    id: "hair-analysis",
    mode: "analysis",
    name: "Hair Density and Hair-Type Analysis",
    shortName: "Hair Health",
    eyebrow: "Hair diagnostics",
    description:
      "Analyze hair type, density, length, and frizziness using local computer vision."
  }
];

export const experienceOptions: ExperienceOption[] = [
  {
    id: "soft-glam",
    category: "makeup",
    name: "Soft Glam",
    description: "Polished skin, gentle contour, neutral eyes, and an elegant lip.",
    accent: "#9f5f56",
    localField: "look_id"
  },
  {
    id: "bridal-radiance",
    category: "makeup",
    name: "Bridal Radiance",
    description: "Luminous complexion, defined eyes, and long-wear event finish.",
    accent: "#b87b63",
    localField: "look_id"
  },
  {
    id: "editorial-evening",
    category: "makeup",
    name: "Evening Definition",
    description: "Sculpted features, richer eye depth, and a refined statement lip.",
    accent: "#744c64",
    localField: "look_id"
  },
  {
    id: "black",
    category: "hair-color",
    name: "Black",
    description: "A deep natural black with a clean salon gloss.",
    accent: "#191715",
    localField: "color_id"
  },
  {
    id: "brown",
    category: "hair-color",
    name: "Brown",
    description: "A dimensional brunette tone for a polished everyday finish.",
    accent: "#5c3824",
    localField: "color_id"
  },
  {
    id: "golden",
    category: "hair-color",
    name: "Golden",
    description: "Warm golden depth with a luminous salon effect.",
    accent: "#bf8e34",
    localField: "color_id"
  },
  {
    id: "blonde",
    category: "hair-color",
    name: "Blonde",
    description: "Soft blonde brightness with a premium diffused tone.",
    accent: "#dabf7b",
    localField: "color_id"
  },
  {
    id: "silver",
    category: "hair-color",
    name: "Silver",
    description: "Cool silver dimension for a refined statement finish.",
    accent: "#bec2c6",
    localField: "color_id"
  },
  {
    id: "red",
    category: "hair-color",
    name: "Red",
    description: "Rich red warmth for a confident color transformation.",
    accent: "#9c2d26",
    localField: "color_id"
  },
  {
    id: "blue",
    category: "hair-color",
    name: "Blue",
    description: "Cool blue tone for a vivid creative salon preview.",
    accent: "#2a52a8",
    localField: "color_id"
  },
  {
    id: "buzzcut",
    category: "hairstyle",
    name: "Buzzcut",
    description: "Crisp, minimal, and strong for a clean modern profile.",
    accent: "#a8663d",
    localField: "style_id"
  },
  {
    id: "crewcut",
    category: "hairstyle",
    name: "Crewcut",
    description: "Classic short structure with enough length for salon texture.",
    accent: "#586f5c",
    localField: "style_id"
  },
  {
    id: "curtain",
    category: "hairstyle",
    name: "Curtain",
    description: "A softer center-parted shape with movement through the front.",
    accent: "#315b78",
    localField: "style_id"
  },
  {
    id: "goatee",
    category: "beard",
    name: "Goatee",
    description: "Focused chin and moustache definition with a sharper mouth frame.",
    accent: "#7f4329",
    localField: "template_id"
  },
  {
    id: "bandholz",
    category: "beard",
    name: "Bandholz",
    description: "Fuller beard volume for a confident, statement grooming look.",
    accent: "#3f4b42",
    localField: "template_id"
  },
  {
    id: "anchor",
    category: "beard",
    name: "Anchor Beard",
    description: "Sculpted chin and moustache balance with precise edges.",
    accent: "#6b5a48",
    localField: "template_id"
  }
];

export function getProductByCategory(category: ExperienceCategory) {
  return experienceProducts.find((product) => product.id === category);
}

export function getOptionsByCategory(category: ExperienceCategory) {
  return experienceOptions.filter((option) => option.category === category);
}
