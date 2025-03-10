import Link from "next/link"
import { Calendar, Ticket, ChevronDown } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { BookingStatus } from "@/types/booking"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

interface Event {
  id: string
  eventId: string
  title: string
  date: Date
  status: BookingStatus
  tickets: Array<{ ticket_id: string; booking_id: string }>
  onAction?: (action: "confirm" | "cancel" | "refund") => void
}

interface EventTimelineProps {
  events: Event[]
  type: "attending" | "hosting"
}

export function EventTimeline({ events, type }: EventTimelineProps) {
  // Group events by month
  const groupedEvents = events.reduce(
    (groups: { [key: string]: Event[] }, event) => {
      const date = event.date
      const monthYear = date.toLocaleString("default", {
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

  // Sort events within each month by date
  Object.values(groupedEvents).forEach((monthEvents) => {
    monthEvents.sort((a, b) => b.date.getTime() - a.date.getTime())
  })

  if (events.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No events found</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {Object.entries(groupedEvents).map(([monthYear, monthEvents]) => (
        <div key={monthYear} className="relative">
          <div className="sticky top-0 z-20 mb-4 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <h3 className="text-xl font-semibold">{monthYear}</h3>
          </div>
          <div className="space-y-4">
            {monthEvents.map((event) => (
              <Card key={event.id} className="p-4">
                <div className="space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold">{event.title}</h4>
                      <div className="flex items-center text-sm text-muted-foreground mt-1">
                        <Calendar className="mr-2 h-4 w-4" />
                        {event.date.toLocaleDateString()}
                      </div>
                    </div>
                    <Badge
                      variant={
                        event.status === "confirmed" ? "default" : "secondary"
                      }
                      className="capitalize"
                    >
                      {event.status}
                    </Badge>
                  </div>

                  <Accordion type="single" collapsible className="w-full">
                    <AccordionItem value="tickets">
                      <AccordionTrigger>
                        <div className="flex items-center">
                          <Ticket className="mr-2 h-4 w-4" />
                          {event.tickets.length} ticket
                          {event.tickets.length !== 1 ? "s" : ""}
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="space-y-2">
                          {event.tickets.map((ticket) => (
                            <div
                              key={ticket.ticket_id}
                              className="p-2 rounded-lg border flex justify-between items-center"
                            >
                              <span className="text-sm">
                                Ticket #{ticket.ticket_id.slice(-8)}
                              </span>
                              <Button variant="outline" size="sm" asChild>
                                <Link href={`/tickets/${ticket.ticket_id}`}>
                                  View Ticket
                                </Link>
                              </Button>
                            </div>
                          ))}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>

                  <div className="flex justify-end gap-2">
                    <Button variant="outline" asChild>
                      <Link href={`/events/${event.eventId}`}>View Event</Link>
                    </Button>
                    {event.onAction && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="outline">
                            Actions <ChevronDown className="ml-2 h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {event.status === "pending" && (
                            <>
                              <DropdownMenuItem
                                onClick={() => event.onAction?.("confirm")}
                              >
                                Confirm Booking
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => event.onAction?.("cancel")}
                              >
                                Cancel Booking
                              </DropdownMenuItem>
                            </>
                          )}
                          {event.status === "confirmed" && (
                            <DropdownMenuItem
                              onClick={() => event.onAction?.("refund")}
                            >
                              Request Refund
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
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
