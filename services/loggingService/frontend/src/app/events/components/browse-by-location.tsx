import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { MapPin } from "lucide-react";

export function BrowseByLocation() {
  // to fetch locations
  const locations = ["New York", "San Francisco", "London", "Tokyo", "Berlin"];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">
        Browse by Location
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {locations.map((location) => (
          <Link href={`/events?location=${location}`} key={location}>
            <Card className="hover:shadow-md transition-shadow duration-300">
              <CardContent className="flex flex-col items-center justify-center p-6">
                <MapPin className="h-8 w-8 mb-2 text-primary" />
                <span className="text-center font-medium">{location}</span>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
