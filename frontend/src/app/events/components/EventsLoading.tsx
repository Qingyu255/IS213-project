import { Skeleton } from "@/components/ui/skeleton";

export default function EventsLoading() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8">
        {/* Header skeleton */}
        <div className="mb-8 text-center">
          <div className="flex justify-center mb-4">
            <Skeleton className="h-6 w-40" />
          </div>
          <Skeleton className="h-12 w-3/4 max-w-xl mx-auto mb-4" />
          <Skeleton className="h-20 w-full max-w-2xl mx-auto" />
        </div>

        {/* Events grid skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {Array.from({ length: 9 }).map((_, i) => (
            <div
              key={`event-${i}`}
              className="bg-card rounded-lg overflow-hidden"
            >
              {/* Event image skeleton */}
              <Skeleton className="h-48 w-full" />

              {/* Event content skeleton */}
              <div className="p-4">
                <Skeleton className="h-6 w-3/4 mb-4" />
                <Skeleton className="h-4 w-1/2 mb-2" />
                <Skeleton className="h-4 w-2/3 mb-2" />
                <Skeleton className="h-4 w-1/3 mb-4" />
                <Skeleton className="h-10 w-full" />
              </div>
            </div>
          ))}
        </div>

        {/* Pagination skeleton */}
        <div className="flex justify-center">
          <Skeleton className="h-10 w-64" />
        </div>
      </div>
    </div>
  );
}
