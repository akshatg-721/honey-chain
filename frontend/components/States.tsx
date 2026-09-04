export function LoadingSpinner({ message = "Loading…" }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20">
      <div className="relative h-12 w-12">
        <div className="absolute inset-0 rounded-full border-2 border-stone-800" />
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-amber-500 animate-spin" />
      </div>
      <p className="text-sm text-stone-500 animate-pulse">{message}</p>
    </div>
  );
}

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
}: {
  title?: string;
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-500/10 border border-red-500/20">
        <span className="text-2xl">⚠️</span>
      </div>
      <div>
        <h3 className="text-base font-semibold text-white mb-1">{title}</h3>
        <p className="text-sm text-stone-500 max-w-sm">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded-lg bg-amber-500/10 border border-amber-500/20 px-4 py-2 text-sm font-semibold text-amber-400 hover:bg-amber-500/20 transition-colors"
        >
          Try again
        </button>
      )}
    </div>
  );
}
