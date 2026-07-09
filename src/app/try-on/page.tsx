import type { Metadata } from "next";
import { TryOnExperience } from "@/components/try-on/try-on-experience";
import { Footer } from "@/components/site/footer";
import { Header } from "@/components/site/header";

export const metadata: Metadata = {
  title: "AI Salon Suite",
  description:
    "Upload or capture a portrait and access AI salon previews, analysis, and consultation reports with MirrorAI."
};

export default function TryOnPage() {
  return (
    <main className="min-h-screen bg-[var(--bone)]">
      <Header compact />
      <TryOnExperience />
      <Footer />
    </main>
  );
}
