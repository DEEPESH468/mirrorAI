import { NextResponse } from "next/server";
import { requestYouCamExperience } from "@/lib/youcam";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const result = await requestYouCamExperience("hairstyle", formData);

    return NextResponse.json(result);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unable to process hairstyle try-on.";

    return NextResponse.json({ message }, { status: 502 });
  }
}
