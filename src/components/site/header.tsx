import { Menu, Scissors } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

type HeaderProps = {
  compact?: boolean;
};

export function Header({ compact = false }: HeaderProps) {
  return (
    <header className="absolute left-0 right-0 top-0 z-30">
      <div
        className={`mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8 lg:px-12 ${
          compact ? "text-[var(--ink)]" : "text-white"
        }`}
      >
        <Link href="/" className="inline-flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-lg bg-[var(--copper)] text-white">
            <Scissors aria-hidden="true" className="h-5 w-5" />
          </span>
          <span className="text-lg font-semibold tracking-normal">MirrorAI</span>
        </Link>
        <nav className="hidden items-center gap-7 text-sm font-medium md:flex">
          <Link href="/#experience" className="opacity-[.82] transition hover:opacity-100">
            Experience
          </Link>
          <Link href="/try-on" className="opacity-[.82] transition hover:opacity-100">
            AI Suite
          </Link>
          <Button asChild href="/try-on" size="sm" variant={compact ? "default" : "secondary"}>
            Begin
          </Button>
        </nav>
        <Button aria-label="Open menu" className="md:hidden" size="icon" variant="secondary">
          <Menu aria-hidden="true" className="h-5 w-5" />
        </Button>
      </div>
    </header>
  );
}
