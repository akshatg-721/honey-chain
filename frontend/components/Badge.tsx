import { ShieldCheck, ShieldX } from "lucide-react";
import { cn } from "@/lib/utils";

type BadgeVariant = "verified" | "unverified" | "status";

interface BadgeProps {
  variant: BadgeVariant;
  label?: string;
  className?: string;
  large?: boolean;
}

export default function Badge({ variant, label, className, large = false }: BadgeProps) {
  const base = cn(
    "inline-flex items-center gap-1.5 rounded-full font-semibold",
    large ? "px-4 py-2 text-base" : "px-2.5 py-0.5 text-xs"
  );

  if (variant === "verified") {
    return (
      <span className={cn(base, "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30", className)}>
        <ShieldCheck className={large ? "h-5 w-5" : "h-3 w-3"} />
        {label ?? "Chain Verified"}
      </span>
    );
  }

  if (variant === "unverified") {
    return (
      <span className={cn(base, "bg-red-500/15 text-red-400 border border-red-500/30", className)}>
        <ShieldX className={large ? "h-5 w-5" : "h-3 w-3"} />
        {label ?? "Verification Failed"}
      </span>
    );
  }

  // generic status badge
  return (
    <span className={cn(base, "bg-amber-500/15 text-amber-400 border border-amber-500/30", className)}>
      {label}
    </span>
  );
}
