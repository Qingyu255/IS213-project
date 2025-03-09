import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header image skeleton */}
          <div className="mb-8 space-y-4">
            <Skeleton className="relative min-h-[400px] w-full rounded-lg" />
            <div className="flex flex-row gap-2 overflow-x-auto pb-2">
              {Array(4)
                .fill(0)
                .map((_, i) => (
                  <Skeleton
                    key={i}
                    className="h-20 w-20 flex-shrink-0 rounded-md"
                  />
                ))}
            </div>
          </div>

          {/* Form fields skeleton */}
          <div className="space-y-6">
            {/* Event Name */}
            <Skeleton className="h-16 w-full" />

            {/* Description */}
            <div className="space-y-2">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-[100px] w-full" />
            </div>

            {/* Date / Time */}
            <div className="space-y-2">
              <Skeleton className="h-5 w-32" />
              <div className="flex flex-col sm:flex-row gap-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            </div>

            <div className="space-y-2">
              <Skeleton className="h-5 w-40" />
              <div className="flex flex-col sm:flex-row gap-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            </div>

            {/* Timezone */}
            <Skeleton className="h-10 w-full" />

            {/* Event Category */}
            <div className="space-y-2">
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-10 w-full" />
            </div>

            {/* Visibility */}
            <div className="space-y-2">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-10 w-full" />
            </div>

            {/* Venue */}
            <div className="space-y-2">
              <Skeleton className="h-5 w-16" />
              <Skeleton className="h-10 w-full" />
            </div>

            {/* Price & Options */}
            <div className="space-y-4 mt-8">
              <Skeleton className="h-7 w-40" />
              <div className="space-y-4 border rounded-lg p-4">
                {/* Price */}
                <div className="flex items-center justify-between">
                  <Skeleton className="h-5 w-16" />
                  <Skeleton className="h-5 w-24" />
                </div>

                {/* Capacity */}
                <div className="flex items-center justify-between">
                  <Skeleton className="h-5 w-20" />
                  <Skeleton className="h-5 w-24" />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <Skeleton className="h-10 w-full" />
          </div>
        </div>
      </div>
    </div>
  );
}
