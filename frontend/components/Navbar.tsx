import Link from "next/link";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-amber-900/20 bg-stone-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="text-2xl">🍯</span>
          <span className="text-lg font-bold tracking-tight text-white group-hover:text-amber-400 transition-colors">
            Honey<span className="text-amber-400 group-hover:text-white transition-colors">Chain</span>
          </span>
        </Link>
        <nav className="flex items-center gap-6">
          <Link
            href="/admin"
            className="text-sm font-medium text-stone-400 hover:text-amber-400 transition-colors"
          >
            Admin
          </Link>
          <Link
            href="/"
            className="rounded-full bg-amber-500 px-4 py-1.5 text-sm font-semibold text-stone-950 hover:bg-amber-400 transition-colors"
          >
            Verify Batch
          </Link>
        </nav>
      </div>
    </header>
  );
}
