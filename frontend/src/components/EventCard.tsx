import Image from "next/image"
import Link from "next/link"
import { Calendar, Clock, MapPin, Users } from "lucide-react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { EventDetails, EventWithTickets } from "@/types/event"

type EventCardProps = {
  event: EventWithTickets
  variant?: "default" | "featured" | "compact"
  showCapacity?: boolean
  showTime?: boolean
}

export function EventCard({
  event,
  variant = "default",
  showCapacity = false,
  showTime = false,
}: EventCardProps) {
  const isFeatured = variant === "featured"

  return (
    <Card
      className={`
        overflow-hidden transition-all duration-300 group
        ${
          isFeatured
            ? "bg-white/5 border-white/10 hover:shadow-[0_0_15px_rgba(149,128,255,0.3)]"
            : "bg-card text-card-foreground hover:shadow-lg"
        }
      `}
    >
      <div className="relative">
        <Image
          src={event.imageUrl || "/placeholder.svg"}
          alt={event.title}
          width={600}
          height={400}
          className={`
            w-full object-cover
            ${
              isFeatured
                ? "h-60 transition-transform duration-500 group-hover:scale-110"
                : "h-48"
            }
          `}
        />

        {isFeatured && (
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
        )}

        {/* Category Badge */}
        <Badge className="absolute top-4 left-4 bg-purple-500 hover:bg-purple-500 border-0">
          {event.categories && event.categories.length > 0
            ? event.categories[0].charAt(0).toUpperCase() +
              event.categories[0].substring(1)
            : "Event"}
        </Badge>

        {/* Title and Date (for featured variant) */}
        {isFeatured && (
          <div className="absolute bottom-4 left-4 right-4">
            <h3 className="text-xl font-bold mb-2">{event.title}</h3>
            <div className="flex items-center /70 text-sm">
              <Calendar className="h-4 w-4 mr-2" />
              <span>{new Date(event.startDateTime).toLocaleDateString()}</span>
            </div>
          </div>
        )}
      </div>

      <CardContent
        className="p-4 flex flex-col h-[calc(100%-var(--image-height))]"
        style={
          {
            "--image-height": isFeatured ? "15rem" : "12rem",
          } as React.CSSProperties
        }
      >
        {/* Title (for default variant) */}
        {!isFeatured && (
          <div>
            <h3 className="text-xl font-bold mb-2">{event.title}</h3>
            <div className="flex items-center text-muted-foreground text-sm mb-4">
              <Calendar className="w-4 h-4 mr-2" />
              <span>{new Date(event.startDateTime).toLocaleDateString()}</span>
            </div>
          </div>
        )}

        <div className="flex flex-col flex-grow justify-between">
          <div className="space-y-3">
            {/* Time */}
            {showTime && (
              <div className="flex items-center text-muted-foreground text-sm">
                <Clock className="h-4 w-4 mr-2" />
                <span>
                  {new Date(event.startDateTime).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                  {event.endDateTime &&
                    ` - ${new Date(event.endDateTime).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}`}
                </span>
              </div>
            )}

            {/* Venue */}
            {event.venue && (
              <div className="flex items-center text-muted-foreground text-sm">
                <MapPin className="h-4 w-4 mr-2" />
                <span>
                  {event.venue.name
                    ? `${event.venue.name}, ${event.venue.city}`
                    : event.venue.address}
                </span>
              </div>
            )}

            {/* Capacity */}
            {showCapacity && (
              <div className="flex items-center text-muted-foreground text-sm">
                <Users className="h-4 w-4 mr-2" />
                <span>{event.capacity} capacity</span>
              </div>
            )}
          </div>

          {/* Add ticket information */}
          <CardFooter className="flex justify-between pt-4">
            <div className="text-sm text-muted-foreground">
              {event.ticketInfo
                ? event.ticketInfo.availableTickets === null
                  ? "Sign in to View Availability"
                  : event.ticketInfo.availableTickets === "Unlimited"
                  ? "No Capacity Limit"
                  : `${event.ticketInfo.availableTickets}/${event.ticketInfo.totalCapacity} Available`
                : "Tickets loading..."}
            </div>
            <div className="text-sm">
              {event.ticketInfo?.availableTickets != null &&
                (event.ticketInfo.availableTickets === 0 &&
                event.ticketInfo.totalCapacity !== "Unlimited" ? (
                  <Badge variant="destructive">Sold Out</Badge>
                ) : typeof event.ticketInfo.availableTickets === "number" &&
                  event.ticketInfo.availableTickets <= 5 ? (
                  <Badge
                    variant="secondary"
                    className="bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20"
                  >
                    Few Left
                  </Badge>
                ) : null)}
            </div>
          </CardFooter>

          {/* Action Button */}
          <div
            className={`w-full mt-4 ${
              isFeatured ? "pt-3 border-t border-white/10" : ""
            }`}
          >
            <Link href={`/events/${event.id}`} className="w-full block">
              <Button
                variant={isFeatured ? "ghost" : "default"}
                className={`
                  ${
                    isFeatured
                      ? "bg-white/5 hover:bg-white/10 float-right"
                      : "w-full bg-primary text-primary-foreground hover:bg-primary/90"
                  }
                `}
              >
                {isFeatured ? "View Details" : "View Event"}
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
