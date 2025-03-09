import { Skeleton } from "@/components/ui/skeleton";
import { InterestCategoryArr } from "@/constants/common";

export default function Loading() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 my-4">
      {InterestCategoryArr.map((_, i) => (
        <div key={i} className="flex flex-col items-center justify-center p-4 border rounded-lg">
          {/* Icon placeholder */}
          <Skeleton className="w-8 h-8 mb-2 rounded-full" />
          {/* Text placeholder */}
          <Skeleton className="h-4 w-16 rounded" />
        </div>
      ))}
    </div>
  );
}
