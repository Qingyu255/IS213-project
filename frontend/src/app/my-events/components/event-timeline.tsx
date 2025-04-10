"use client";

import Link from "next/link";
import Image from "next/image";
import {
  Calendar,
  Ticket,
  ChevronDown,
  ChevronUp,
  MapPin,
  Clock,
  XCircle,
  RefreshCcw,
  ExternalLink,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { BookingStatus } from "@/types/booking";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Spinner } from "@/components/ui/spinner";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

// Define the interfaces to match your existing data structure
interface TicketType {
  ticket_id: string
  booking_id: string
  status: string
}

interface BookingType {
  booking_id: string
  user_id: string
  event_id: string
  status: BookingStatus
  created_at: string | Date
  updated_at: string
  tickets: TicketType[]
  total_amount: number
  onAction?: (action: "cancel" | "refund" | "complete") => Promise<void>
}

interface EventType {
  id: string
  eventId: string
  title: string
  date: Date
  bookings: BookingType[]
  ticketDetails: any
}

interface EventTimelineProps {
  events: EventType[]
  type: "attending" | "hosting"
}

export function EventTimeline({ events, type }: EventTimelineProps) {
  const router = useRouter();
  const [processingBookingId, setProcessingBookingId] = useState<string | null>(
    null
  );
  const [openEvent, setOpenEvent] = useState<string | null>(
    events.length > 0 ? events[0].id : null
  );
  const [openBooking, setOpenBooking] = useState<string | null>(null);

  // Group events by month
  const groupedEvents = events.reduce<Record<string, EventType[]>>(
    (groups, event) => {
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

  const getStatusInfo = (status: BookingStatus) => {
    switch (status) {
      case BookingStatus.CONFIRMED:
        return {
          label: "Confirmed",
          badge: (
            <Badge className="bg-[hsl(var(--status-confirmed))] text-[hsl(var(--background))]">
              Confirmed
            </Badge>
          ),
          icon: (
            <Ticket className="h-5 w-5 text-[hsl(var(--status-confirmed))]" />
          ),
          bgColor: "bg-[hsl(var(--status-confirmed-bg))]",
          borderColor: "border-[hsl(var(--status-confirmed-border))]",
          textColor: "text-[hsl(var(--status-confirmed))]",
          iconBg: "bg-[hsl(var(--status-confirmed-bg))]",
        };
      case BookingStatus.PENDING:
        return {
          label: "Pending",
          badge: (
            <Badge className="bg-[hsl(var(--status-pending))] text-[hsl(var(--background))]">
              Pending
            </Badge>
          ),
          icon: <Clock className="h-5 w-5 text-[hsl(var(--status-pending))]" />,
          bgColor: "bg-[hsl(var(--status-pending-bg))]",
          borderColor: "border-[hsl(var(--status-pending-border))]",
          textColor: "text-[hsl(var(--status-pending))]",
          iconBg: "bg-[hsl(var(--status-pending-bg))]",
        };
      case BookingStatus.CANCELED:
        return {
          label: "Canceled",
          badge: (
            <Badge className="bg-[hsl(var(--status-cancelled))] text-[hsl(var(--background))]">
              Canceled
            </Badge>
          ),
          icon: (
            <XCircle className="h-5 w-5 text-[hsl(var(--status-cancelled))]" />
          ),
          bgColor: "bg-[hsl(var(--status-cancelled-bg))]",
          borderColor: "border-[hsl(var(--status-cancelled-border))]",
          textColor: "text-[hsl(var(--status-cancelled))]",
          iconBg: "bg-[hsl(var(--status-cancelled-bg))]",
        };
      case BookingStatus.REFUNDED:
        return {
          label: "Refunded",
          badge: (
            <Badge className="bg-[hsl(var(--status-refunded))] text-[hsl(var(--background))]">
              Refunded
            </Badge>
          ),
          icon: (
            <RefreshCcw className="h-5 w-5 text-[hsl(var(--status-refunded))]" />
          ),
          bgColor: "bg-[hsl(var(--status-refunded-bg))]",
          borderColor: "border-[hsl(var(--status-refunded-border))]",
          textColor: "text-[hsl(var(--status-refunded))]",
          iconBg: "bg-[hsl(var(--status-refunded-bg))]",
        };
      default:
        return {
          label: status,
          badge: <Badge>{status}</Badge>,
          icon: <Ticket className="h-5 w-5" />,
          bgColor: "bg-gray-50",
          borderColor: "border-gray-200",
          textColor: "text-gray-700",
          iconBg: "bg-gray-100",
        };
    }
  };

  const handleAction = async (
    booking: BookingType,
    action: "cancel" | "refund" | "complete"
  ) => {
    setProcessingBookingId(booking.booking_id);
    try {
      if (booking.onAction) {
        if (action === "refund") {
          // Redirect to dynamic refund page route
          router.push(`/refund/${booking.booking_id}`);
        } else {
          // For other actions, use the existing onAction handler
          await booking.onAction(action);
        }
      }
    } finally {
      setProcessingBookingId(null);
    }
  };

  const toggleEvent = (eventId: string) => {
    setOpenEvent(openEvent === eventId ? null : eventId);
  };

  const toggleBooking = (bookingId: string) => {
    setOpenBooking(openBooking === bookingId ? null : bookingId);
  };

  // Count bookings by status for an event
  const countBookingsByStatus = (event: EventType) => {
    const confirmed = event.bookings.filter(
      (b) => b.status === BookingStatus.CONFIRMED
    ).length;
    const pending = event.bookings.filter(
      (b) => b.status === BookingStatus.PENDING
    ).length;
    const canceled = event.bookings.filter(
      (b) => b.status === BookingStatus.CANCELED
    ).length;
    const refunded = event.bookings.filter(
      (b) => b.status === BookingStatus.REFUNDED
    ).length;

    return {
      confirmed,
      pending,
      canceled,
      refunded,
      total: event.bookings.length,
    };
  };

  if (events.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-24 w-24 rounded-full bg-[hsl(var(--purple-100))] flex items-center justify-center mb-4">
          <Ticket className="h-12 w-12 text-[hsl(var(--purple-600))]" />
        </div>
        <h2 className="text-xl font-semibold mb-2">No events found</h2>
        <p className="text-muted-foreground mb-6">
          When you book events, they'll appear here.
        </p>
        <Button
          asChild
          className="bg-[hsl(var(--purple-600))] hover:bg-[hsl(var(--purple-700))]"
        >
          <Link href="/events">Explore Events</Link>
        </Button>
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
            {monthEvents.map((event) => {
              const counts = countBookingsByStatus(event);

              return (
                <Card
                  key={event.id}
                  className="mb-6 overflow-hidden rounded-lg border shadow-sm"
                >
                  <Collapsible
                    open={openEvent === event.id}
                    onOpenChange={() => toggleEvent(event.id)}
                  >
                    <CollapsibleTrigger className="w-full text-left">
                      <div className="flex items-center p-4 bg-[hsl(var(--background))] hover:bg-[hsl(var(--accent))] transition-colors">
                        <div className="relative h-16 w-16 rounded-md overflow-hidden mr-4 flex-shrink-0">
                          <Image
                            src={
                              event.ticketDetails?.event_details?.imageUrl ||
                              "/eventplaceholder.png"
                            }
                            alt={event.title}
                            fill
                            sizes="(max-width: 64px) 100vw, 64px"
                            className="object-cover"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.src = "/eventplaceholder.png";
                            }}
                            priority
                          />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex gap-1">
                              {counts.confirmed > 0 && (
                                <Badge
                                  variant="outline"
                                  className="bg-[hsl(var(--status-confirmed-bg))] text-[hsl(var(--status-confirmed))]"
                                >
                                  {counts.confirmed} Confirmed
                                </Badge>
                              )}
                              {counts.pending > 0 && (
                                <Badge
                                  variant="outline"
                                  className="bg-[hsl(var(--status-pending-bg))] text-[hsl(var(--status-pending))]"
                                >
                                  {counts.pending} Pending
                                </Badge>
                              )}
                              {counts.canceled > 0 && (
                                <Badge
                                  variant="outline"
                                  className="bg-[hsl(var(--status-cancelled-bg))] text-[hsl(var(--status-cancelled))]"
                                >
                                  {counts.canceled} Canceled
                                </Badge>
                              )}
                              {counts.refunded > 0 && (
                                <Badge
                                  variant="outline"
                                  className="bg-[hsl(var(--status-refunded-bg))] text-[hsl(var(--status-refunded))]"
                                >
                                  {counts.refunded} Refunded
                                </Badge>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <h2 className="text-xl font-semibold">
                              {event.title}
                            </h2>
                            <Link
                              href={`/events/${event.eventId}`}
                              className="text-muted-foreground hover:text-[hsl(var(--purple-600))] transition-colors"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </Link>
                          </div>
                          <div className="flex items-center justify-between mt-2">
                            <p className="text-sm text-muted-foreground">
                              {event.date.toLocaleDateString()} at{" "}
                              {event.date.toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </p>
                            {openEvent === event.id ? (
                              <ChevronUp className="h-5 w-5 text-muted-foreground" />
                            ) : (
                              <ChevronDown className="h-5 w-5 text-muted-foreground" />
                            )}
                          </div>
                        </div>
                      </div>
                    </CollapsibleTrigger>

                    <CollapsibleContent>
                      <div className="p-4 pt-0">
                        {event.ticketDetails?.event_details?.venue && (
                          <>
                            <div className="flex items-start gap-3 py-4 px-2 border-b border-[hsl(var(--border))]">
                              <div className="h-10 w-10 rounded-full bg-[hsl(var(--purple-100))] flex items-center justify-center">
                                <MapPin className="h-5 w-5 text-[hsl(var(--purple-600))]" />
                              </div>
                              <div>
                                <p className="font-medium">Event Location</p>
                                <p className="text-sm text-muted-foreground">
                                  {event.ticketDetails.event_details.venue.name}
                                  ,{" "}
                                  {
                                    event.ticketDetails.event_details.venue
                                      .address
                                  }
                                </p>
                              </div>
                            </div>
                            <div className="flex items-start gap-3 py-4 px-2 border-b border-[hsl(var(--border))]">
                              <div className="h-10 w-10 rounded-full bg-[hsl(var(--purple-100))] flex items-center justify-center">
                                <Calendar className="h-5 w-5 text-[hsl(var(--purple-600))]" />
                              </div>
                              <div>
                                <p className="font-medium">Event Date & Time</p>
                                <p className="text-sm text-muted-foreground">
                                  {event.date.toLocaleDateString()} at{" "}
                                  {event.date.toLocaleTimeString([], {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  })}
                                </p>
                              </div>
                            </div>
                          </>
                        )}

                        <div className="space-y-4 mt-4">
                          {event.bookings.map((booking) => {
                            const statusInfo = getStatusInfo(booking.status);
                            const bookingDate =
                              booking.created_at instanceof Date
                                ? booking.created_at.toLocaleDateString()
                                : new Date(
                                    booking.created_at
                                  ).toLocaleDateString();

                            return (
                              <Card
                                key={booking.booking_id}
                                className={cn(
                                  "border-l-4 rounded-lg overflow-hidden",
                                  booking.status === BookingStatus.CONFIRMED &&
                                    "border-l-[hsl(var(--status-confirmed))] bg-[hsl(var(--status-confirmed-bg))]",
                                  booking.status === BookingStatus.PENDING &&
                                    "border-l-[hsl(var(--status-pending))] bg-[hsl(var(--status-pending-bg))]",
                                  booking.status === BookingStatus.CANCELED &&
                                    "border-l-[hsl(var(--status-cancelled))] bg-[hsl(var(--status-cancelled-bg))]",
                                  booking.status === BookingStatus.REFUNDED &&
                                    "border-l-[hsl(var(--status-refunded))] bg-[hsl(var(--status-refunded-bg))]"
                                )}
                              >
                                <Collapsible
                                  open={openBooking === booking.booking_id}
                                  onOpenChange={() =>
                                    toggleBooking(booking.booking_id)
                                  }
                                >
                                  <CollapsibleTrigger className="w-full text-left">
                                    <CardHeader
                                      className={cn(
                                        "py-3 px-4 flex flex-row items-center justify-between",
                                        statusInfo.bgColor
                                      )}
                                    >
                                      <div className="flex items-center gap-3">
                                        <div
                                          className={cn(
                                            "h-10 w-10 rounded-full flex items-center justify-center",
                                            statusInfo.iconBg
                                          )}
                                        >
                                          {statusInfo.icon}
                                        </div>
                                        <div>
                                          <div className="flex items-center gap-2 mb-0.5">
                                            <p className="font-medium">
                                              Booking #
                                              {booking.booking_id.slice(-8)}
                                            </p>
                                            {statusInfo.badge}
                                          </div>
                                          <p className="text-sm text-muted-foreground">
                                            {bookingDate}
                                          </p>
                                        </div>
                                      </div>
                                      {openBooking === booking.booking_id ? (
                                        <ChevronUp className="h-5 w-5 text-muted-foreground" />
                                      ) : (
                                        <ChevronDown className="h-5 w-5 text-muted-foreground" />
                                      )}
                                    </CardHeader>
                                  </CollapsibleTrigger>

                                  <CollapsibleContent>
                                    <CardContent
                                      className={cn("p-4", statusInfo.bgColor)}
                                    >
                                      <div className="grid gap-6 md:grid-cols-2">
                                        <div className="space-y-4">
                                          {/* Tickets Section */}
                                          <h3 className="font-semibold mb-3">
                                            Ticket Details
                                          </h3>
                                          <div className="space-y-2">
                                            {booking.tickets.map((ticket) => (
                                              <div
                                                key={ticket.ticket_id}
                                                className="flex items-center gap-2"
                                              >
                                                <Ticket className="h-4 w-4 text-[hsl(var(--purple-600))]" />
                                                <span className="text-sm font-medium">
                                                  Ticket #
                                                  {ticket.ticket_id.slice(-8)}
                                                </span>
                                              </div>
                                            ))}
                                          </div>
                                        </div>

                                        <div>
                                          {/* Payment Details Section - Only show for non-cancelled/refunded bookings */}
                                          {booking.status !==
                                            BookingStatus.CANCELED &&
                                            booking.status !==
                                              BookingStatus.REFUNDED && (
                                              <div>
                                                <h3 className="font-semibold mb-3">
                                                  Payment Details
                                                </h3>
                                                <div className="rounded-md border border-[hsl(var(--border))] p-3 bg-[hsl(var(--background))]">
                                                  <div className="flex justify-between mb-1">
                                                    <span className="text-sm">
                                                      Ticket Price
                                                    </span>
                                                    <span className="font-medium">
                                                      $
                                                      {event.ticketDetails?.event_details?.price?.toFixed(
                                                        2
                                                      ) || "0.00"}
                                                    </span>
                                                  </div>

                                                  {/* Add quantity line item */}
                                                  <div className="flex justify-between mb-1">
                                                    <span className="text-sm">
                                                      Quantity
                                                    </span>
                                                    <span className="font-medium">
                                                      {booking.tickets.length}
                                                    </span>
                                                  </div>

                                                  <div className="flex justify-between mt-2 pt-2 border-t border-[hsl(var(--border))]">
                                                    <span className="font-medium">
                                                      Total
                                                    </span>
                                                    <span className="font-bold">
                                                      $
                                                      {(
                                                        event.ticketDetails
                                                          ?.event_details
                                                          ?.price *
                                                        booking.tickets.length
                                                      )?.toFixed(2) || "0.00"}
                                                    </span>
                                                  </div>
                                                </div>
                                              </div>
                                            )}

                                          {/* Cancellation Details */}
                                          {booking.status ===
                                            BookingStatus.CANCELED && (
                                            <div>
                                              <h3 className="font-semibold mb-3">
                                                Cancelation Details
                                              </h3>
                                              <div className="rounded-md border border-[hsl(var(--status-cancelled-border))] p-3 bg-[hsl(var(--background))]">
                                                <p className="text-sm text-[hsl(var(--status-cancelled))]">
                                                  This booking has been
                                                  canceled. No payment was
                                                  processed.
                                                </p>
                                              </div>
                                            </div>
                                          )}

                                          {/* Refund Details */}
                                          {booking.status ===
                                            BookingStatus.REFUNDED && (
                                            <div>
                                              <h3 className="font-semibold mb-3">
                                                Refund Details
                                              </h3>
                                              <div className="rounded-md border border-[hsl(var(--status-refunded-border))] p-3 bg-[hsl(var(--background))]">
                                                <div className="flex justify-between mb-1">
                                                  <span className="text-sm">
                                                    Original Total
                                                  </span>
                                                  <span className="font-medium">
                                                    $
                                                    {(
                                                      event.ticketDetails
                                                        ?.event_details?.price *
                                                      booking.tickets.length
                                                    )?.toFixed(2) || "0.00"}
                                                  </span>
                                                </div>
                                                <div className="flex justify-between">
                                                  <span className="text-sm">
                                                    Refunded Amount
                                                  </span>
                                                  <span className="font-medium text-[hsl(var(--status-refunded))]">
                                                    -$
                                                    {(
                                                      event.ticketDetails
                                                        ?.event_details?.price *
                                                      booking.tickets.length
                                                    )?.toFixed(2) || "0.00"}
                                                  </span>
                                                </div>
                                                <div className="flex justify-between mt-2 pt-2 border-t border-[hsl(var(--status-refunded-border))]">
                                                  <span className="font-medium">
                                                    Balance
                                                  </span>
                                                  <span className="font-bold">
                                                    $0.00
                                                  </span>
                                                </div>
                                              </div>
                                            </div>
                                          )}
                                        </div>
                                      </div>

                                      {/* Action Buttons */}
                                      <div className="flex justify-end gap-2 mt-6">
                                        {booking.status ===
                                          BookingStatus.PENDING && (
                                          <>
                                            <Button
                                              size="sm"
                                              className={cn(
                                                "bg-[hsl(var(--status-pending))] hover:bg-[hsl(var(--status-pending))] text-[hsl(var(--background))]",
                                                "min-w-[120px] justify-center"
                                              )}
                                              onClick={() =>
                                                handleAction(
                                                  booking,
                                                  "complete"
                                                )
                                              }
                                              disabled={
                                                processingBookingId ===
                                                booking.booking_id
                                              }
                                            >
                                              {processingBookingId ===
                                              booking.booking_id ? (
                                                <Spinner className="mr-2 h-4 w-4" />
                                              ) : null}
                                              Complete Payment
                                            </Button>
                                            <Button
                                              size="sm"
                                              className={cn(
                                                "bg-[hsl(var(--status-cancelled))] hover:bg-[hsl(var(--status-cancelled))] text-[hsl(var(--background))]",
                                                "min-w-[120px] justify-center"
                                              )}
                                              onClick={() =>
                                                handleAction(booking, "cancel")
                                              }
                                              disabled={
                                                processingBookingId ===
                                                booking.booking_id
                                              }
                                            >
                                              {processingBookingId ===
                                              booking.booking_id ? (
                                                <Spinner className="mr-2 h-4 w-4" />
                                              ) : null}
                                              Cancel Booking
                                            </Button>
                                          </>
                                        )}
                                        {booking.status ===
                                          BookingStatus.CONFIRMED && (
                                          <Button
                                            size="sm"
                                            className={cn(
                                              event.ticketDetails?.event_details
                                                ?.price > 0
                                                ? "bg-[hsl(var(--status-refunded))] hover:bg-[hsl(var(--status-refunded))] text-[hsl(var(--background))]" // Blue for refund
                                                : "bg-[hsl(var(--status-cancelled))] hover:bg-[hsl(var(--status-cancelled))] text-[hsl(var(--background))]", // Black for cancel
                                              "min-w-[120px] justify-center" // Add fixed minimum width and center justify
                                            )}
                                            onClick={() =>
                                              handleAction(
                                                booking,
                                                event.ticketDetails
                                                  ?.event_details?.price > 0
                                                  ? "refund"
                                                  : "cancel"
                                              )
                                            }
                                            disabled={
                                              processingBookingId ===
                                              booking.booking_id
                                            }
                                          >
                                            {processingBookingId ===
                                            booking.booking_id ? (
                                              <Spinner className="mr-2 h-4 w-4" />
                                            ) : null}
                                            {event.ticketDetails?.event_details
                                              ?.price > 0
                                              ? "Request Refund"
                                              : "Cancel Booking"}
                                          </Button>
                                        )}
                                      </div>
                                    </CardContent>
                                  </CollapsibleContent>
                                </Collapsible>
                              </Card>
                            );
                          })}
                        </div>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
                </Card>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
