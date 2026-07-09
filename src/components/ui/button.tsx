import Link from "next/link";
import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from "react";

type ButtonSize = "sm" | "md" | "lg" | "icon";
type ButtonVariant = "default" | "secondary" | "ghost";

type SharedProps = {
  children: ReactNode;
  className?: string;
  size?: ButtonSize;
  variant?: ButtonVariant;
};

type NativeButtonProps = SharedProps &
  ButtonHTMLAttributes<HTMLButtonElement> & {
    asChild?: false;
  };

type LinkButtonProps = SharedProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & {
    asChild: true;
  };

const sizes: Record<ButtonSize, string> = {
  sm: "h-10 px-4 text-sm",
  md: "h-12 px-5 text-sm",
  lg: "h-14 px-6 text-base",
  icon: "h-11 w-11 p-0"
};

const variants: Record<ButtonVariant, string> = {
  default:
    "bg-[var(--copper)] text-white hover:bg-[var(--copper-dark)] shadow-[0_12px_30px_rgba(168,102,61,0.26)]",
  secondary:
    "bg-white/92 text-[var(--ink)] hover:bg-white shadow-[0_12px_30px_rgba(0,0,0,0.12)]",
  ghost: "bg-transparent text-current hover:bg-black/5"
};

export function Button(props: NativeButtonProps | LinkButtonProps) {
  const {
    asChild,
    children,
    className = "",
    size = "md",
    variant = "default",
    ...rest
  } = props;

  const classes = `inline-flex shrink-0 items-center justify-center gap-2 rounded-lg font-semibold transition disabled:pointer-events-none disabled:opacity-55 ${sizes[size]} ${variants[variant]} ${className}`;

  if (asChild) {
    const anchorProps = rest as AnchorHTMLAttributes<HTMLAnchorElement>;
    const href = anchorProps.href ?? "#";

    if (typeof href === "string" && href.startsWith("/")) {
      return (
        <Link {...anchorProps} href={href} className={classes}>
          {children}
        </Link>
      );
    }

    return (
      <a {...anchorProps} href={href} className={classes}>
        {children}
      </a>
    );
  }

  return (
    <button {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)} className={classes}>
      {children}
    </button>
  );
}
