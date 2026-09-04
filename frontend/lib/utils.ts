/** Lightweight classname merger — avoids adding a full clsx/tailwind-merge dep */
export function cn(...classes: (string | undefined | false | null)[]): string {
  return classes.filter(Boolean).join(" ");
}
