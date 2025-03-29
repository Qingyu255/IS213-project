import Image from "next/image";
import Link from "next/link";
import { Calendar, MapPin } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EventDetails } from "@/types/event";


export function EventList({ events }: { events: EventDetails[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {events.map((event) => (
        <Card
          key={event.id}
          className="bg-card text-card-foreground overflow-hidden hover:shadow-lg transition-shadow duration-300"
        >
          <div className="relative h-48">
            <Image
              src={event.imageUrl || "/placeholder.svg"}
              alt={event.title}
              layout="fill"
              objectFit="cover"
              className="transition-transform duration-300 hover:scale-105"
            />
            <>
              {event.categories.map((category, i) => {
                return (
                  <Badge key={i} className="mb-4 bg-primary/10 text-primary hover:bg-primary/20 border-0">
                    {category as string}
                  </Badge>
                );
              })}
            </>
          </div>
          <CardContent className="p-4">
            <h3 className="text-xl font-bold mb-2">{event.title}</h3>
            <div className="flex items-center text-muted-foreground text-sm mb-2">
              <Calendar className="w-4 h-4 mr-2" />
              <span>{event.startDateTime}</span>
            </div>
            <div className="flex items-center text-muted-foreground text-sm mb-2">
              <MapPin className="w-4 h-4 mr-2" />
              <span>{event.venue.address || event.venue.name}</span>
            </div>
            <Link href={`/events/${event.id}`} passHref>
              <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90">View Event</Button>
            </Link>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
