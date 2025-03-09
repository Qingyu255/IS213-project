"use client"

import { useEffect, useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { EventTimeline } from "./components/event-timeline"
import { Badge } from "@/components/ui/badge"
import { getUserBookings, type Booking } from "@/lib/api/tickets"
import useAuthUser from "@/hooks/use-auth-user"

export default function MyEventsPage() {
  const [activeTab, setActiveTab] = useState("attending")
  const [bookings, setBookings] = useState<Booking[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user, getUserId } = useAuthUser()
  const userId = getUserId()

  useEffect(() => {
    async function fetchBookings() {
      if (!userId) return

      try {
        const data = await getUserBookings(userId)
        setBookings(data)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch bookings"
        )
      } finally {
        setIsLoading(false)
      }
    }

    fetchBookings()
  }, [userId])

  // Convert bookings to event format
  const attendingEvents = bookings.map((booking) => ({
    id: booking.booking_id,
    title: `Event ${booking.event_id}`, // TODO: Fetch event details
    date: new Date(booking.created_at),
    location: "TBD", // TODO: Fetch event location
    status: booking.status,
    imageUrl: "/placeholder.svg",
    tickets: booking.tickets,
  }))

  if (!user) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <p>Loading your events...</p>
        </div>
      </div>
    )
  }

  if (!user.isLoggedIn) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <p>Please log in to view your events.</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <p className="text-destructive">Error: {error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">My Events</h1>
          <p className="text-muted-foreground">
            Manage your events and see what&apos;s coming up
          </p>
        </div>

        <Tabs
          defaultValue="attending"
          value={activeTab}
          onValueChange={setActiveTab}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <TabsList className="bg-muted/50">
              <TabsTrigger value="attending" className="relative">
                Attending
                <Badge className="ml-2 bg-primary/10 text-primary hover:bg-primary/20">
                  {attendingEvents.length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="hosting">
                Hosting
                <Badge className="ml-2 bg-primary/10 text-primary hover:bg-primary/20">
                  0
                </Badge>
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="attending" className="space-y-8">
            <EventTimeline events={attendingEvents} type="attending" />
          </TabsContent>

          <TabsContent value="hosting" className="space-y-8">
            <EventTimeline events={[]} type="hosting" />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
