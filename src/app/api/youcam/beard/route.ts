import { NextResponse } from "next/server";
import { requestYouCamExperience } from "@/lib/youcam";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const result = await requestYouCamExperience("beard", formData);

    return NextResponse.json(result);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unable to process beard try-on.";

    return NextResponse.json({ message }, { status: 502 });
  }
}
