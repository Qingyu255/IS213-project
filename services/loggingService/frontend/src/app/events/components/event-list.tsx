import Image from "next/image"
import Link from "next/link"
import { Calendar, MapPin, Users } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

type Event = {
  id: string
  name: string
  image: string
  date: string
  location: string
  attendees: number
  category: string
}

export function EventList({ events }: { events: Event[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {events.map((event) => (
        <Card
          key={event.id}
          className="bg-card text-card-foreground overflow-hidden hover:shadow-lg transition-shadow duration-300"
        >
          <div className="relative h-48">
            <Image
              src={event.image || "/placeholder.svg"}
              alt={event.name}
              layout="fill"
              objectFit="cover"
              className="transition-transform duration-300 hover:scale-105"
            />
            <Badge className="absolute top-2 left-2 bg-primary text-primary-foreground">{event.category}</Badge>
          </div>
          <CardContent className="p-4">
            <h3 className="text-xl font-bold mb-2">{event.name}</h3>
            <div className="flex items-center text-muted-foreground text-sm mb-2">
              <Calendar className="w-4 h-4 mr-2" />
              <span>{event.date}</span>
            </div>
            <div className="flex items-center text-muted-foreground text-sm mb-2">
              <MapPin className="w-4 h-4 mr-2" />
              <span>{event.location}</span>
            </div>
            <div className="flex items-center text-muted-foreground text-sm mb-4">
              <Users className="w-4 h-4 mr-2" />
              <span>{event.attendees} attending</span>
            </div>
            <Link href={`/events/${event.id}`} passHref>
              <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90">View Details</Button>
            </Link>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
