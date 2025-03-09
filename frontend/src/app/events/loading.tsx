import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";

export default function Loading() {
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

        {/* Browse sections skeleton */}
        <div className="flex flex-col md:flex-row gap-5">
          {/* Browse by Category */}
          <div className="flex-1">
            <Skeleton className="h-8 w-48 mb-4" />
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton
                  key={`category-${i}`}
                  className="h-24 w-full rounded-lg"
                />
              ))}
            </div>
          </div>

          {/* Browse by Location */}
          <div className="flex-1">
            <Skeleton className="h-8 w-48 mb-4" />
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton
                  key={`location-${i}`}
                  className="h-24 w-full rounded-lg"
                />
              ))}
            </div>
          </div>
        </div>

        <Separator className="my-4" />

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
