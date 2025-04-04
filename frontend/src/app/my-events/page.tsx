/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import { useEffect, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EventTimeline } from "./components/event-timeline";
import { Badge } from "@/components/ui/badge";
import {
  getUserBookings,
  BookingResponse,
  updateBookingStatus,
  getUserEventTickets,
  UserEventTicketsResponse,
} from "@/lib/api/tickets";
import useAuthUser from "@/hooks/use-auth-user";
import { toast } from "sonner";
import { Spinner } from "@/components/ui/spinner";
import { ErrorMessageCallout } from "@/components/error-message-callout";
import { BookingStatus } from "@/types/booking";
import { HostingEvents } from "./components/hosting-events";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { getBearerIdToken } from "@/utils/auth";
import { EventDetails } from "@/types/event";
import { fetchAuthSession } from "@aws-amplify/core";
import { Route } from "@/enums/Route";
import { useRouter as useNextRouter } from "next/navigation";
import { getUserHostedEvents } from "@/lib/api/events";

interface EventWithBookings {
  eventId: string;
  bookings: BookingResponse[];
  ticketDetails: UserEventTicketsResponse;
}

export default function MyEventsPage() {
  const router = useNextRouter();
  const [activeTab, setActiveTab] = useState("attending");
  const [hostedEvents, setHostedEvents] = useState<EventDetails[]>([]);
  const [hostingCount, setHostingCount] = useState(0);
  const [eventBookings, setEventBookings] = useState<EventWithBookings[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, getUserId, getUsername } = useAuthUser();
  const userId = getUserId();
  const username = getUsername();

  // -----------------------
  // Auth check on mount (DO NOT MODIFY)
  // -----------------------
  useEffect(() => {
    async function checkSession() {
      try {
        const session = await fetchAuthSession();
        const token = session.tokens?.accessToken;
        if (!token) {
          router.replace(Route.Login);
        } else {
          setIsLoading(false);
        }
      } catch (err) {
        console.error("Session check failed:", err);
        router.replace(Route.Login);
      }
    }
    checkSession();
  }, [router]);

  useEffect(() => {
    async function fetchBookingsAndTickets() {
      if (!userId) {
        console.log("No user ID (custom:id) available, skipping fetch");
        setIsLoading(false);
        setError(
          "Unable to find your user ID (custom:id). This could be because:\n" +
            "1. You are not logged in\n" +
            "2. Your account was not properly set up in the user management service\n" +
            "3. The custom:id attribute was not properly set in your Cognito user\n\n" +
            "Please try:\n" +
            "1. Logging out and logging in again\n" +
            "2. If the issue persists, contact support to verify your account setup"
        );
        return;
      }

      console.log("=== Debug Info ===");
      console.log("User object:", user);
      console.log("Fetching bookings for user ID (custom:id):", userId);
      console.log("Username:", username);

      try {
        setIsLoading(true);
        setError(null);

        // Add a delay to ensure the component is mounted
        await new Promise((resolve) => setTimeout(resolve, 500));

        console.log("Making API call to get user bookings...");
        const bookings = await getUserBookings(userId);
        console.log("Bookings API Response:", bookings);

        // Group bookings by event ID
        const bookingsByEvent = bookings.reduce(
          (acc: { [key: string]: BookingResponse[] }, booking) => {
            const eventId = booking.event_id;
            if (!acc[eventId]) {
              acc[eventId] = [];
            }
            acc[eventId].push(booking);
            return acc;
          },
          {}
        );

        // Create event objects with their bookings and ticket details
        const eventBookingsData: EventWithBookings[] = [];
        for (const [eventId, eventBookings] of Object.entries(
          bookingsByEvent
        )) {
          try {
            console.log(`Fetching tickets for event ${eventId}`);
            const eventTickets = await getUserEventTickets(userId, eventId);
            eventBookingsData.push({
              eventId,
              bookings: eventBookings,
              ticketDetails: eventTickets,
            });
          } catch (eventError) {
            console.error("Error fetching event tickets:", eventError);
            // Continue with other events even if one fails
          }
        }

        setEventBookings(eventBookingsData);
      } catch (error) {
        console.error("Error fetching bookings and tickets:", error);
        setError("Failed to load your events. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    }

    async function fetchHostedEvents() {
      if (!userId) {
        setIsLoading(false);
        return;
      }

      try {
        // Get events where user is the organizer
        const eventsUserIsHosting = await getUserHostedEvents(userId);
        setHostedEvents(eventsUserIsHosting);
      } catch (err) {
        console.error("Error fetching hosted events:", err);
        setError("Failed to load your hosted events");
      } finally {
        setIsLoading(false);
      }
    }
    fetchBookingsAndTickets();
    fetchHostedEvents();
  }, [userId]);

  // Update hostedEvents count when first loaded or after changes
  useEffect(() => {
    setHostingCount(hostedEvents.length);
  }, [hostedEvents]);

  const handleBookingAction = async (
    bookingId: string,
    action: "cancel" | "refund"
  ) => {
    try {
      await updateBookingStatus(bookingId, action);
      // Refresh bookings after action
      if (userId) {
        const updatedBookings = await getUserBookings(userId);
        // Re-group the updated bookings
        const bookingsByEvent = updatedBookings.reduce(
          (acc: { [key: string]: BookingResponse[] }, booking) => {
            const eventId = booking.event_id;
            if (!acc[eventId]) {
              acc[eventId] = [];
            }
            acc[eventId].push(booking);
            return acc;
          },
          {}
        );

        const updatedEventBookings: EventWithBookings[] = [];
        for (const [eventId, eventBookings] of Object.entries(
          bookingsByEvent
        )) {
          try {
            const eventTickets = await getUserEventTickets(userId, eventId);
            updatedEventBookings.push({
              eventId,
              bookings: eventBookings,
              ticketDetails: eventTickets,
            });
          } catch (eventError) {
            console.error("Error fetching event tickets:", eventError);
          }
        }

        setEventBookings(updatedEventBookings);
      }
      toast.success("Success", {
        description: `Booking ${action}ed successfully`,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : `Failed to ${action} booking`;
      toast.error("Error", {
        description: errorMessage,
      });
      throw err;
    }
  };

  // Convert events to the format expected by EventTimeline
  const attendingEvents = eventBookings.map((eventWithBookings) => ({
    id: eventWithBookings.eventId,
    eventId: eventWithBookings.eventId,
    title: `Event ${eventWithBookings.eventId}`,
    date: new Date(eventWithBookings.bookings[0]?.created_at || Date.now()),
    bookings: eventWithBookings.bookings.map((booking) => ({
      id: booking.booking_id,
      status: booking.status as BookingStatus,
      tickets: booking.tickets,
      created_at: new Date(booking.created_at),
      onAction: (action: "cancel" | "refund") =>
        handleBookingAction(booking.booking_id, action),
    })),
    ticketDetails: eventWithBookings.ticketDetails,
  }));

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!userId) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner size="lg" className="bg-black dark:bg-white" />;
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-4">
        <ErrorMessageCallout errorMessage={error} />
      </div>
    );
  }

  if (!user?.isLoggedIn) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <p>Please log in to view your events.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">My Events</h1>
        <Tabs defaultValue={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="attending">
              Attending{" "}
              <Badge variant="secondary" className="ml-2">
                {attendingEvents.length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="hosting">
              Hosting{" "}
              <Badge variant="secondary" className="ml-2">
                {hostedEvents.length}
              </Badge>
            </TabsTrigger>
          </TabsList>
          <TabsContent value="attending">
            <EventTimeline events={attendingEvents} type="attending" />
          </TabsContent>
          <TabsContent value="hosting">
            <HostingEvents events={hostedEvents} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
