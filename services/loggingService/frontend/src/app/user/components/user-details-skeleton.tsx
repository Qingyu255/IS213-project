import { Skeleton } from "@/components/ui/skeleton";

export function UserDetailsSkeleton() {
  return (
    <div className="container mx-auto p-4 space-y-4">
      <Skeleton className="h-8 w-1/4" />
      <div className="space-y-4">
        {Array(6)
          .fill(0)
          .map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-4 w-1/6" />
              <Skeleton className="h-10 w-full" />
            </div>
          ))}
      </div>
      <div className="flex justify-end space-x-2">
        <Skeleton className="h-10 w-20" />
        <Skeleton className="h-10 w-20" />
      </div>
    </div>
  );
}
