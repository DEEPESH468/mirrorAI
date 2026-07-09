import { NextResponse } from "next/server";
import { experienceProducts } from "@/lib/styles";
import { requestYouCamExperience } from "@/lib/youcam";
import type { ExperienceCategory } from "@/types/try-on";

type RouteContext = {
  params: Promise<{
    product: string;
  }>;
};

function isExperienceCategory(value: string): value is ExperienceCategory {
  return experienceProducts.some((product) => product.id === value);
}

export async function POST(request: Request, context: RouteContext) {
  const { product } = await context.params;

  if (!isExperienceCategory(product)) {
    return NextResponse.json(
      { message: "Unsupported YouCam product." },
      { status: 404 }
    );
  }

  try {
    const formData = await request.formData();
    const result = await requestYouCamExperience(product, formData);

    return NextResponse.json(result);
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Unable to process the YouCam request.";

    return NextResponse.json({ message }, { status: 502 });
  }
}
