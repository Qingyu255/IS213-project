import Link from "next/link";
import { Calendar, Ticket, ChevronDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { BookingStatus } from "@/types/booking";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Spinner } from "@/components/ui/spinner";
import { useState } from "react";
import { UserEventTicketsResponse } from "@/lib/api/tickets";

interface Booking {
  id: string
  status: BookingStatus
  tickets: Array<{ ticket_id: string; booking_id: string; status: string }>
  created_at: Date
  onAction?: (action: "cancel" | "refund") => Promise<void>
}

interface Event {
  id: string
  eventId: string
  title: string
  date: Date
  bookings: Booking[]
  ticketDetails: UserEventTicketsResponse
}

interface EventTimelineProps {
  events: Event[]
  type: "attending" | "hosting"
}

export function EventTimeline({ events }: EventTimelineProps) {
  const [processingBookingId, setProcessingBookingId] = useState<string | null>(
    null
  );

  // Group events by month
  const groupedEvents = events.reduce(
    (groups: { [key: string]: Event[] }, event) => {
      const date = event.date;
      const monthYear = date.toLocaleString("default", {
        month: "long",
        year: "numeric",
      });

      if (!groups[monthYear]) {
        groups[monthYear] = [];
      }
      groups[monthYear].push(event);
      return groups;
    },
    {}
  );

  // Sort events within each month by date
  Object.values(groupedEvents).forEach((monthEvents) => {
    monthEvents.sort((a, b) => b.date.getTime() - a.date.getTime());
  });

  const getStatusBadgeVariant = (
    status: BookingStatus
  ): "default" | "destructive" | "secondary" | "outline" => {
    switch (status) {
      case BookingStatus.PENDING:
        return "secondary";
      case BookingStatus.CONFIRMED:
        return "default";
      case BookingStatus.CANCELED:
        return "destructive";
      case BookingStatus.REFUNDED:
        return "secondary";
      default:
        return "default";
    }
  };

  const handleAction = async (
    booking: Booking,
    action: "cancel" | "refund"
  ) => {
    setProcessingBookingId(booking.id);
    try {
      await booking.onAction?.(action);
    } finally {
      setProcessingBookingId(null);
    }
  };

  if (events.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No events found</p>
      </div>
    );
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
                  </div>

                  <Accordion type="multiple" className="w-full">
                    <AccordionItem value="bookings">
                      <AccordionTrigger>
                        <div className="flex items-center">
                          <Ticket className="mr-2 h-4 w-4" />
                          {event.bookings.length} booking
                          {event.bookings.length !== 1 ? "s" : ""}
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="space-y-4">
                          {event.bookings.map((booking) => (
                            <div
                              key={booking.id}
                              className="p-3 rounded-lg border"
                            >
                              <div className="flex justify-between items-center mb-3">
                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-medium">
                                    Booking #{booking.id.slice(-8)}
                                  </span>
                                  <Badge
                                    variant={getStatusBadgeVariant(
                                      booking.status
                                    )}
                                  >
                                    {booking.status.toLowerCase()}
                                  </Badge>
                                </div>
                                {booking.onAction && (
                                  <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        disabled={
                                          processingBookingId === booking.id
                                        }
                                      >
                                        {processingBookingId === booking.id ? (
                                          <Spinner className="mr-2 h-4 w-4" />
                                        ) : null}
                                        Actions{" "}
                                        <ChevronDown className="ml-2 h-4 w-4" />
                                      </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                      {booking.status ===
                                        BookingStatus.PENDING && (
                                        <DropdownMenuItem
                                          onClick={() =>
                                            handleAction(booking, "cancel")
                                          }
                                        >
                                          Cancel Booking
                                        </DropdownMenuItem>
                                      )}
                                      {booking.status ===
                                        BookingStatus.CONFIRMED && (
                                        <DropdownMenuItem
                                          onClick={() =>
                                            handleAction(booking, "refund")
                                          }
                                        >
                                          Request Refund
                                        </DropdownMenuItem>
                                      )}
                                    </DropdownMenuContent>
                                  </DropdownMenu>
                                )}
                              </div>
                              <div className="space-y-2">
                                {booking.tickets.map((ticket) => (
                                  <div
                                    key={ticket.ticket_id}
                                    className="p-2 rounded-lg border flex justify-between items-center"
                                  >
                                    <div className="flex items-center gap-2">
                                      <span className="text-sm">
                                        Ticket #{ticket.ticket_id.slice(-8)}
                                      </span>
                                      <Badge
                                        variant={
                                          ticket.status === "VALID"
                                            ? "default"
                                            : "destructive"
                                        }
                                      >
                                        {ticket.status}
                                      </Badge>
                                    </div>
                                    <Button variant="outline" size="sm" asChild>
                                      <Link
                                        href={`/tickets/${ticket.ticket_id}`}
                                      >
                                        View Ticket
                                      </Link>
                                    </Button>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>

                  <div className="flex justify-end">
                    <Button variant="outline" asChild>
                      <Link href={`/events/${event.eventId}`}>View Event</Link>
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
