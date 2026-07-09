import {
  Activity,
  ArrowRight,
  Brush,
  Droplets,
  FileText,
  Images,
  Palette,
  ScanFace,
  Scissors,
  WandSparkles
} from "lucide-react";
import Image from "next/image";
import { Footer } from "@/components/site/footer";
import { Header } from "@/components/site/header";
import { Button } from "@/components/ui/button";

const services = [
  {
    icon: Droplets,
    title: "Skin Analysis",
    copy: "AI skin scan outputs that help shape facials, skincare rituals, and consultation notes."
  },
  {
    icon: Brush,
    title: "Makeup Try-On",
    copy: "Preview soft glam, bridal, evening, and cosmetic looks before service selection."
  },
  {
    icon: Palette,
    title: "Hair Color",
    copy: "Test refined salon shades, glosses, and color directions before the appointment."
  },
  {
    icon: Scissors,
    title: "Hairstyle Preview",
    copy: "Try cuts and silhouettes for every guest, then refine the final brief with a stylist."
  },
  {
    icon: WandSparkles,
    title: "Beard Styling",
    copy: "Preview beard and moustache shapes for grooming and face-framing consultations."
  },
  {
    icon: ScanFace,
    title: "Face Shape",
    copy: "Map facial attributes to guide haircuts, contouring, makeup, and grooming choices."
  },
  {
    icon: Activity,
    title: "Hair Analysis",
    copy: "Use supported outputs for hair type, density, length, and frizz-aware recommendations."
  },
  {
    icon: FileText,
    title: "Consultation Report",
    copy: "Turn AI outputs into a polished salon-facing summary for premium guest care."
  }
];

const experiences = [
  "Skin Analysis",
  "Virtual Makeup",
  "Hair Color",
  "Hairstyles",
  "Beard Styles",
  "Face Shape",
  "Hair Diagnostics",
  "Consultation Reports"
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[var(--bone)]">
      <Header />
      <section className="grain relative isolate min-h-[92svh] overflow-hidden bg-[var(--charcoal)] text-white">
        <Image
          src="https://images.unsplash.com/photo-1622287162716-f311baa1a2b8?auto=format&fit=crop&w=1800&q=85"
          alt="Premium unisex salon chair and styling station"
          fill
          priority
          sizes="100vw"
          className="object-cover opacity-[.58]"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/[.82] via-black/[.48] to-black/20" />
        <div className="relative mx-auto flex min-h-[92svh] max-w-7xl items-center px-5 py-24 sm:px-8 lg:px-12">
          <div className="max-w-3xl">
            <p className="mb-5 inline-flex rounded-full border border-white/[.22] bg-white/10 px-4 py-2 text-sm font-medium text-white/[.88] backdrop-blur">
              Premium salon intelligence, previewed with AI
            </p>
            <h1 className="max-w-4xl text-5xl font-semibold leading-[0.98] tracking-normal sm:text-7xl lg:text-8xl">
              MirrorAI
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-white/[.82] sm:text-xl">
              A refined AI consultation suite for skin, makeup, hair color,
              hairstyles, beard styling, face shape, and hair analysis inside
              one elegant unisex salon journey.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Button asChild href="/try-on" size="lg">
                Start AI Suite
                <ArrowRight aria-hidden="true" className="h-5 w-5" />
              </Button>
              <Button asChild href="#experience" variant="secondary" size="lg">
                Explore the Experience
              </Button>
            </div>
          </div>
        </div>
      </section>

      <section
        id="experience"
        className="mx-auto grid max-w-7xl gap-10 px-5 py-16 sm:px-8 lg:grid-cols-[0.85fr_1.15fr] lg:px-12 lg:py-24"
      >
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--copper-dark)]">
            Private salon consultation
          </p>
          <h2 className="mt-4 text-3xl font-semibold text-[var(--ink)] sm:text-5xl">
            Built for one premium unisex salon, not a marketplace.
          </h2>
          <p className="mt-5 text-base leading-7 text-neutral-700">
            MirrorAI keeps the journey loyal to a single salon brand: curated
            services, elegant guest flow, AI outputs, and consultation-ready
            recommendations without accounts, checkout, or operational clutter.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {services.map((service) => (
            <article
              key={service.title}
              className="rounded-lg border border-[var(--line)] bg-[var(--paper)] p-5"
            >
              <service.icon
                aria-hidden="true"
                className="h-6 w-6 text-[var(--copper)]"
              />
              <h3 className="mt-5 text-lg font-semibold text-[var(--ink)]">
                {service.title}
              </h3>
              <p className="mt-3 text-sm leading-6 text-neutral-700">
                {service.copy}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="bg-[var(--ink)] px-5 py-16 text-white sm:px-8 lg:px-12 lg:py-24">
        <div className="mx-auto grid max-w-7xl items-center gap-10 lg:grid-cols-2">
          <div className="relative aspect-[4/5] overflow-hidden rounded-lg premium-shadow sm:aspect-[16/11] lg:aspect-[4/5]">
            <Image
              src="https://images.unsplash.com/photo-1517832606299-7ae9b720a186?auto=format&fit=crop&w=1400&q=85"
              alt="Stylist preparing a premium salon consultation"
              fill
              sizes="(min-width: 1024px) 50vw, 100vw"
              className="object-cover"
            />
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[#d8a06f]">
              Curated AI suite
            </p>
            <h2 className="mt-4 text-3xl font-semibold sm:text-5xl">
              Preview the look. Understand the face. Personalize the service.
            </h2>
            <div className="mt-8 flex flex-wrap gap-3">
              {experiences.map((style) => (
                <span
                  key={style}
                  className="rounded-full border border-white/[.18] bg-white/[.08] px-4 py-2 text-sm text-white/[.86]"
                >
                  {style}
                </span>
              ))}
            </div>
            <Button asChild className="mt-9" href="/try-on" size="lg">
              Open AI Suite
              <Images aria-hidden="true" className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
