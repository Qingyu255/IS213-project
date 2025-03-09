import Image from "next/image"
import Link from "next/link"
import { Calendar, MapPin, Clock, Ticket } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { BookingStatus } from "@/types/booking"

interface Event {
  id: string
  title: string
  date: Date
  location: string
  status: BookingStatus
  imageUrl: string
  tickets: Array<{ ticket_id: string; booking_id: string }>
}

interface EventTimelineProps {
  events: Event[]
  type: "attending" | "hosting"
}

export function EventTimeline({ events, type }: EventTimelineProps) {
  // Group events by month
  const groupedEvents = events.reduce(
    (groups: { [key: string]: Event[] }, event) => {
      const monthYear = event.date.toLocaleString("default", {
        month: "long",
        year: "numeric",
      })
      if (!groups[monthYear]) {
        groups[monthYear] = []
      }
      groups[monthYear].push(event)
      return groups
    },
    {}
  )

  if (events.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium mb-2">
          {type === "attending"
            ? "No events to attend yet"
            : "No events hosted yet"}
        </h3>
        <p className="text-muted-foreground mb-4">
          {type === "attending"
            ? "Browse upcoming events and join the ones you're interested in."
            : "Start creating your own events and invite others to join."}
        </p>
        <Button asChild>
          <Link href={type === "attending" ? "/events" : "/create"}>
            {type === "attending" ? "Browse Events" : "Create Event"}
          </Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-12">
      {Object.entries(groupedEvents).map(([monthYear, monthEvents]) => (
        <div key={monthYear} className="relative">
          <div className="sticky top-0 bg-background/95 backdrop-blur-sm z-10 py-2">
            <h2 className="text-xl font-semibold">{monthYear}</h2>
          </div>

          <div className="mt-4 space-y-4">
            {monthEvents.map((event) => (
              <Card
                key={event.id}
                className="p-4 hover:shadow-lg transition-shadow"
              >
                <div className="flex gap-4">
                  <div className="relative w-24 h-24 flex-shrink-0">
                    <Image
                      src={event.imageUrl}
                      alt={event.title}
                      fill
                      className="object-cover rounded-lg"
                    />
                  </div>

                  <div className="flex-grow">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-lg mb-1">
                          {event.title}
                        </h3>
                        <div className="flex items-center text-muted-foreground text-sm mb-1">
                          <Calendar className="w-4 h-4 mr-1" />
                          <span>
                            {event.date.toLocaleDateString("default", {
                              weekday: "long",
                              month: "long",
                              day: "numeric",
                            })}
                          </span>
                        </div>
                        <div className="flex items-center text-muted-foreground text-sm">
                          <Clock className="w-4 h-4 mr-1" />
                          <span>
                            {event.date.toLocaleTimeString("default", {
                              timeStyle: "short",
                            })}
                          </span>
                          <MapPin className="w-4 h-4 ml-3 mr-1" />
                          <span>{event.location}</span>
                          <Ticket className="w-4 h-4 ml-3 mr-1" />
                          <span>{event.tickets.length} tickets</span>
                        </div>
                      </div>

                      <div className="flex items-start gap-2">
                        <Badge
                          variant={
                            event.status === "confirmed"
                              ? "default"
                              : "secondary"
                          }
                          className="capitalize"
                        >
                          {event.status}
                        </Badge>
                        <Button variant="outline" asChild>
                          <Link href={`/events/${event.id}`}>
                            {type === "hosting" ? "Manage" : "View"}
                          </Link>
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
