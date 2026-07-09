import { Scissors } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-[var(--line)] bg-[var(--paper)] px-5 py-10 sm:px-8 lg:px-12">
      <div className="mx-auto flex max-w-7xl flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="inline-flex items-center gap-3">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-[var(--ink)] text-white">
            <Scissors aria-hidden="true" className="h-4 w-4" />
          </span>
          <div>
            <p className="font-semibold text-[var(--ink)]">MirrorAI</p>
            <p className="text-sm text-neutral-600">Premium unisex salon intelligence</p>
          </div>
        </div>
        <p className="text-sm text-neutral-600">
          Results are AI previews and analysis guides for professional consultation.
        </p>
      </div>
    </footer>
  );
}
