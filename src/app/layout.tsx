import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "MirrorAI | Premium AI Salon Consultation",
    template: "%s | MirrorAI"
  },
  description:
    "Upload or capture a portrait for premium AI salon previews and analysis across skin, makeup, hair, face shape, and grooming.",
  keywords: [
    "unisex salon",
    "AI salon consultation",
    "virtual makeup try-on",
    "hair color simulation",
    "skin analysis",
    "face shape analysis",
    "virtual grooming",
    "MirrorAI"
  ],
  openGraph: {
    title: "MirrorAI",
    description:
      "AI-powered virtual consultation for a premium unisex salon.",
    type: "website"
  }
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#171514"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
