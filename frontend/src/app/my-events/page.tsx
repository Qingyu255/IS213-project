"use client"

import { useEffect, useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { EventTimeline } from "./components/event-timeline"
import { Badge } from "@/components/ui/badge"
import {
  getUserBookings,
  getUserEventTickets,
  type BookingResponse,
  updateBookingStatus,
} from "@/lib/api/tickets"
import useAuthUser from "@/hooks/use-auth-user"
import { Spinner } from "@/components/ui/spinner"
import { ErrorMessageCallout } from "@/components/error-message-callout"
import { HostingEvents } from "./components/hosting-events"
import { fetchAuthSession } from "@aws-amplify/core"
import { Route } from "@/enums/Route"
import { useRouter } from "next/navigation"
import { getEventById, getUserHostedEvents } from "@/lib/api/events"
import { toast } from "sonner"
import type { EventDetails } from "@/types/event"

interface EventBooking {
  eventId: string
  bookings: BookingResponse[]
  ticketDetails: {
    event_id: string
    event_details: Omit<EventDetails, "id">
    tickets: Array<{
      ticket_id: string
      booking_id: string
      status: string
    }>
    count: number
    ticket_ids: string[]
  }
}

interface TimelineEvent {
  id: string
  eventId: string
  title: string
  date: Date
  bookings: Array<
    BookingResponse & {
      created_at: string
      onAction?: (action: "cancel" | "refund") => Promise<void>
    }
  >
  ticketDetails: EventBooking["ticketDetails"]
}

export default function MyEventsPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState("attending")
  const [activeStatusTab, setActiveStatusTab] = useState("all")
  const [hostedEvents, setHostedEvents] = useState<EventDetails[]>([])
  const [eventBookings, setEventBookings] = useState<EventBooking[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user, getUserId, getUsername } = useAuthUser()
  const userId = getUserId()
  const username = getUsername()

  const [hostingCount, setHostingCount] = useState(0)

  useEffect(() => {
    setHostingCount(hostedEvents.length)
  }, [hostedEvents])

  // -----------------------
  // Auth check on mount (DO NOT MODIFY)
  // -----------------------
  useEffect(() => {
    async function checkSession() {
      try {
        const session = await fetchAuthSession()
        const token = session.tokens?.accessToken
        if (!token) {
          router.replace(Route.Login)
        } else {
          setIsLoading(false)
        }
      } catch (err) {
        console.error("Session check failed:", err)
        router.replace(Route.Login)
      }
    }
    checkSession()
  }, [router])

  useEffect(() => {
    async function fetchBookingsAndTickets() {
      if (!userId) {
        console.log("No user ID (custom:id) available, skipping fetch")
        setIsLoading(false)
        setError(
          "Unable to find your user ID (custom:id). This could be because:\n" +
            "1. You are not logged in\n" +
            "2. Your account was not properly set up in the user management service\n" +
            "3. The custom:id attribute was not properly set in your Cognito user\n\n" +
            "Please try:\n" +
            "1. Logging out and logging in again\n" +
            "2. If the issue persists, contact support to verify your account setup"
        )
        return
      }

      console.log("=== Debug Info ===")
      console.log("User object:", user)
      console.log("Fetching bookings for user ID (custom:id):", userId)
      console.log("Username:", username)

      try {
        setIsLoading(true)
        setError(null)

        // Add a delay to ensure the component is mounted
        await new Promise((resolve) => setTimeout(resolve, 500))

        console.log("Making API call to get user bookings...")
        const bookings = await getUserBookings(userId)
        console.log("Bookings API Response:", bookings)

        // Group bookings by event ID
        const bookingsByEvent: Record<string, BookingResponse[]> = {}

        bookings.forEach((booking) => {
          const eventId = booking.event_id
          if (!bookingsByEvent[eventId]) {
            bookingsByEvent[eventId] = []
          }
          bookingsByEvent[eventId].push(booking)
        })

        // Create event objects with their bookings and ticket details
        const eventBookingsData: EventBooking[] = []
        for (const [eventId, eventBookings] of Object.entries(
          bookingsByEvent
        )) {
          try {
            const eventTickets = await getUserEventTickets(userId, eventId)
            const eventDetails = await getEventById(eventId)
            eventBookingsData.push({
              eventId,
              bookings: eventBookings,
              ticketDetails: {
                event_id: eventId,
                event_details: eventDetails,
                ...eventTickets,
              },
            })
          } catch (eventError) {
            console.error("Error fetching event tickets:", eventError)
            // Continue with other events even if one fails
          }
        }

        setEventBookings(eventBookingsData)
      } catch (error) {
        console.error("Error fetching bookings and tickets:", error)
        setError("Failed to load your events. Please try again later.")
      } finally {
        setIsLoading(false)
      }
    }

    async function fetchHostedEvents() {
      if (!userId) {
        setIsLoading(false)
        return
      }

      try {
        // Get events where user is the organizer
        const eventsUserIsHosting = await getUserHostedEvents(userId)
        setHostedEvents(eventsUserIsHosting)
      } catch (err) {
        console.error("Error fetching hosted events:", err)
        setError("Failed to load your hosted events")
      } finally {
        setIsLoading(false)
      }
    }

    fetchBookingsAndTickets()
    fetchHostedEvents()
  }, [userId, user, username])

  const handleBookingAction = async (
    bookingId: string,
    action: "cancel" | "refund"
  ) => {
    try {
      await updateBookingStatus(bookingId, action)
      // Refresh bookings after action
      if (userId) {
        const updatedBookings = await getUserBookings(userId)

        const bookingsByEvent: Record<string, BookingResponse[]> = {}
        updatedBookings.forEach((booking) => {
          const eventId = booking.event_id
          if (!bookingsByEvent[eventId]) {
            bookingsByEvent[eventId] = []
          }
          bookingsByEvent[eventId].push(booking)
        })

        const updatedEventBookings: EventBooking[] = []
        for (const [eventId, eventBookings] of Object.entries(
          bookingsByEvent
        )) {
          try {
            const eventTickets = await getUserEventTickets(userId, eventId)
            const eventDetails = await getEventById(eventId)
            updatedEventBookings.push({
              eventId,
              bookings: eventBookings,
              ticketDetails: {
                event_id: eventId,
                event_details: eventDetails,
                ...eventTickets,
              },
            })
          } catch (eventError) {
            console.error("Error fetching event tickets:", eventError)
          }
        }

        setEventBookings(updatedEventBookings)
      }
      toast.success("Success", {
        description: `Booking ${action}ed successfully`,
      })
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : `Failed to ${action} booking`
      toast.error("Error", {
        description: errorMessage,
      })
      throw err
    }
  }

  // Filter events based on active status tab
  const filterEventsByStatus = (events: TimelineEvent[]) => {
    if (activeStatusTab === "all") return events

    return events.filter((event) =>
      event.bookings.some((booking) => {
        if (activeStatusTab === "confirmed")
          return booking.status === "CONFIRMED"
        if (activeStatusTab === "pending") return booking.status === "PENDING"
        if (activeStatusTab === "cancelled")
          return booking.status === "CANCELED"
        if (activeStatusTab === "refunded") return booking.status === "REFUNDED"
        return false
      })
    )
  }

  // Convert events to the format expected by EventTimeline
  const attendingEvents: TimelineEvent[] = eventBookings.map(
    (eventWithBookings) => ({
      id: eventWithBookings.eventId,
      eventId: eventWithBookings.eventId,
      title:
        eventWithBookings.ticketDetails.event_details?.title ||
        `Event ${eventWithBookings.eventId}`,
      date: new Date(eventWithBookings.bookings[0]?.created_at || Date.now()),
      bookings: eventWithBookings.bookings.map((booking) => ({
        ...booking,
        created_at: booking.created_at,
        onAction: (action: "cancel" | "refund") =>
          handleBookingAction(booking.booking_id, action),
      })),
      ticketDetails: eventWithBookings.ticketDetails,
    })
  )

  // Filter events based on status tab
  const filteredAttendingEvents = filterEventsByStatus(attendingEvents)

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!userId) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner size="lg" className="bg-black dark:bg-white" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-4">
        <ErrorMessageCallout errorMessage={error} />
      </div>
    )
  }

  if (!user?.isLoggedIn) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <p>Please log in to view your events.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-4xl mx-auto py-8 px-4 md:px-0">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <h1 className="text-3xl font-bold">My Events</h1>
        </div>

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
                {hostingCount}
              </Badge>
            </TabsTrigger>
          </TabsList>

          <div className="mt-6 mb-4">
            {activeTab === "attending" && (
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <Tabs
                  value={activeStatusTab}
                  onValueChange={setActiveStatusTab}
                  className="w-full sm:w-auto"
                >
                  <TabsList className="grid grid-cols-5 sm:flex">
                    <TabsTrigger value="all" className="text-xs sm:text-sm">
                      All
                    </TabsTrigger>
                    <TabsTrigger
                      value="confirmed"
                      className="text-xs sm:text-sm"
                    >
                      Confirmed
                    </TabsTrigger>
                    <TabsTrigger value="pending" className="text-xs sm:text-sm">
                      Pending
                    </TabsTrigger>
                    <TabsTrigger
                      value="cancelled"
                      className="text-xs sm:text-sm"
                    >
                      Cancelled
                    </TabsTrigger>
                    <TabsTrigger
                      value="refunded"
                      className="text-xs sm:text-sm"
                    >
                      Refunded
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>
            )}
          </div>

          <TabsContent value="attending">
            <EventTimeline events={filteredAttendingEvents} type="attending" />
          </TabsContent>
          <TabsContent value="hosting">
            <HostingEvents events={hostedEvents} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
