"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import {
  Calendar,
  Clock,
  MapPin,
  Users,
  Globe,
  Share2,
  Ticket,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { EventMap } from "./components/event-map";
import { EventDetails } from "@/types/event";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { getBearerIdToken } from "@/utils/auth";
import { ErrorMessageCallout } from "@/components/error-message-callout";
import { Spinner } from "@/components/ui/spinner";
import { useParams, useRouter } from "next/navigation";
import useAuthUser from "@/hooks/use-auth-user";
import { getAvailableTickets } from "@/lib/api/tickets";

export default function EventPage() {
  const { id } = useParams();
  const [event, setEvent] = useState<EventDetails | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { getUserId } = useAuthUser();
  const userId = getUserId();
  const [ticketInfo, setTicketInfo] = useState<{
    availableTickets: number;
  } | null>(null);

  const handleBooking = async () => {
    if (!userId) {
      router.push("/auth/login");
      return;
    }
    router.push(`/book/${id}`);
  };

  // Fetch ticket availability
  useEffect(() => {
    async function fetchTicketAvailability() {
      if (!userId) {
        return;
      }

      try {
        const ticketData = await getAvailableTickets(id as string);
        setTicketInfo({
          availableTickets: ticketData.available_tickets,
        });
      } catch (err) {
        console.error("Failed to fetch ticket availability:", err);
        // Don't set error state here as it would override the main event fetch error
      }
    }

    fetchTicketAvailability();
  }, [id, userId]);

  // Fetch event details on component mount
  useEffect(() => {
    async function fetchEvent() {
      try {
        const res = await fetch(
          `${BACKEND_ROUTES.eventsService}/api/v1/events/${id}`,
          {
            headers: {
              Accept: "application/json",
              Authorization: await getBearerIdToken(),
            },
          }
        );
        if (!res.ok) {
          throw new Error(`Failed to fetch event details: ${res.statusText}`);
        }
        const data: EventDetails = await res.json();
        console.log(data);
        setEvent(data);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        setError(err.message || "An error occurred");
      } finally {
        setIsLoading(false);
      }
    }
    fetchEvent();
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-5">
        <Spinner size="sm" className="bg-black dark:bg-white" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-5">
        <ErrorMessageCallout errorMessage={error} />
      </div>
    );
  }

  if (!event) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>No event found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative h-[300px] md:h-[400px]">
        <Image
          src={event.imageUrl || "/placeholder.svg"}
          alt={event.title}
          fill
          className="object-cover opacity-90"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background to-transparent" />
      </div>

      <div className="container mx-auto px-4 -mt-16 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Event Header */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <>
                {event.categories.map((category, i) => {
                  return (
                    <Badge
                      key={i}
                      className="mb-4 bg-primary/10 text-primary hover:bg-primary/20 border-0"
                    >
                      {category as string}
                    </Badge>
                  );
                })}
              </>
              <h1 className="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">
                {event.title}
              </h1>
              <div className="flex flex-wrap gap-4 text-muted-foreground">
                <div className="flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  <>{event.startDateTime}</>
                  {new Date(event.startDateTime).toLocaleDateString()}
                </div>
                <div className="flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  End Date:{" "}
                  {event.endDateTime
                    ? new Date(event.endDateTime).toLocaleTimeString()
                    : "No end date"}
                </div>
                <div className="flex items-center">
                  <MapPin className="w-5 h-5 mr-2" />
                  {event.venue.address}
                </div>
              </div>
            </div>

            {/* About Section */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">About Event</h2>
              <p className="text-muted-foreground mb-6">{event.description}</p>
              <Image
                src={event.imageUrl || "/placeholder.svg?height=400&width=800"}
                alt="Event preview"
                width={800}
                height={400}
                className="rounded-lg"
              />
            </div>

            {/* Location Section */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">Location</h2>
              <p className="text-muted-foreground mb-4">
                {event.venue.address}
              </p>
              <h3 className="text-base font-bold mb-2">Additional Details</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {event.venue.additionalDetails}
              </p>
              <div className="h-[300px] rounded-lg overflow-hidden">
                <EventMap
                  center={event.venue.coordinates}
                  zoom={15}
                  marker={event.venue.coordinates}
                />
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Registration Card */}
            <div className="bg-card rounded-lg p-6 shadow-lg sticky top-6">
              <div className="flex justify-between items-center mb-6">
                <div className="text-2xl font-bold">
                  {event.price > 0 ? `${event.price} SGD` : "Free"}
                </div>
                <Button
                  onClick={handleBooking}
                  disabled={
                    isLoading ||
                    (ticketInfo != null && ticketInfo.availableTickets <= 0)
                  }
                  className="w-full md:w-auto"
                >
                  {isLoading
                    ? "Processing..."
                    : ticketInfo && ticketInfo.availableTickets <= 0
                    ? "Sold Out"
                    : "Book Now"}
                </Button>
              </div>
              <Separator className="my-4" />
              <div className="space-y-4">
                {event.capacity !== 0 && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-muted-foreground">
                      <Ticket className="w-5 h-5 mr-2" />
                      <span>Available Tickets</span>
                    </div>
                    <span
                      className={
                        ticketInfo && ticketInfo.availableTickets <= 5
                          ? "text-red-500 font-bold"
                          : ""
                      }
                    >
                      {/* where ticketInfo == null suggests that the user is not signed in */}
                      {ticketInfo != null
                        ? ticketInfo.availableTickets
                        : "Sign in to view"}
                    </span>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div className="flex items-center text-muted-foreground">
                    <Users className="w-5 h-5 mr-2" />
                    <span>Total Capacity</span>
                  </div>
                  <span>
                    {event.capacity == 0 ? "No Capacity" : event.capacity}
                  </span>
                </div>
              </div>
              <Separator className="my-4" />
              <div className="space-y-4">
                <h3 className="font-medium">Share Event</h3>
                <div className="flex gap-2">
                  <Button variant="outline" size="icon">
                    <Globe className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="icon">
                    <Share2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <Separator className="my-4"/>
              {/* Organizer Details */}
              <h3 className="font-bold mb-4">Organized by</h3>
              <div className="flex items-center gap-4">
                <Avatar className="w-12 h-12">
                  <AvatarFallback>
                    {event.organizer.username.slice(0, 3)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-medium">{event.organizer.username}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
