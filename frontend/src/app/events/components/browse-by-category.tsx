import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { InterestCategoryArr, InterestCategoryIcons } from "@/constants/common";

export function BrowseByCategory() {
  const capitalizeFirstLetter = (str: string) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">
        Browse by Category
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {InterestCategoryArr.map((category) => {
          const Icon = InterestCategoryIcons[category.toLowerCase()];
          return (
            <Link href={`/events?category=${category}`} key={category}>
              <Card className="hover:shadow-md transition-shadow duration-300">
                <CardContent className="flex flex-col items-center justify-center p-6">
                  {Icon && <Icon className="h-8 w-8 mb-2 text-primary" />}
                  <span className="text-center font-medium">
                    {capitalizeFirstLetter(category)}
                  </span>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
