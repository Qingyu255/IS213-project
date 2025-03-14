"use client"

import { useEffect, useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { EventTimeline } from "./components/event-timeline"
import { Badge } from "@/components/ui/badge"
import {
  getUserBookings,
  BookingResponse,
  updateBookingStatus,
  getEventTickets,
} from "@/lib/api/tickets"
import useAuthUser from "@/hooks/use-auth-user"
import { toast } from "sonner"
import { Spinner } from "@/components/ui/spinner"
import { ErrorMessageCallout } from "@/components/error-message-callout"
import { BookingStatus } from "@/types/booking"

export default function MyEventsPage() {
  const [activeTab, setActiveTab] = useState("attending")
  const [bookings, setBookings] = useState<BookingResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user, getUserId } = useAuthUser()
  const userId = getUserId()

  useEffect(() => {
    async function fetchBookings() {
      if (!userId) return

      try {
        setIsLoading(true)
        const data = await getUserBookings(userId)
        setBookings(data)
        setError(null)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch bookings"
        )
        toast.error("Error", {
          description: "Failed to fetch your bookings",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchBookings()
  }, [userId])

  const handleBookingAction = async (
    bookingId: string,
    action: "cancel" | "refund"
  ) => {
    try {
      await updateBookingStatus(bookingId, action)
      // Refresh bookings after action
      if (userId) {
        const updatedBookings = await getUserBookings(userId)
        setBookings(updatedBookings)
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
      throw err // Re-throw to be handled by the component
    }
  }

  // Convert bookings to event format
  const attendingEvents = bookings.map((booking) => ({
    id: booking.booking_id,
    eventId: booking.event_id,
    title: `Event ${booking.event_id}`,
    date: new Date(booking.created_at),
    status: booking.status as BookingStatus,
    tickets: booking.tickets,
    onAction: (action: "cancel" | "refund") =>
      handleBookingAction(booking.booking_id, action),
  }))

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Spinner size="lg" />
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
          </TabsList>
          <TabsContent value="attending">
            <EventTimeline events={attendingEvents} type="attending" />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
