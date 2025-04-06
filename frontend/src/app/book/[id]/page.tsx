"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { getCurrentUser } from "aws-amplify/auth"
import { getBearerIdToken } from "@/utils/auth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ErrorMessageCallout } from "@/components/error-message-callout"
import { Spinner } from "@/components/ui/spinner"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BACKEND_ROUTES } from "@/constants/backend-routes"
import { MapPin, Calendar } from "lucide-react"
import useAuthUser from "@/hooks/use-auth-user"
import { getAvailableTickets } from "@/lib/api/tickets"

interface BookingFormData {
  quantity: number
  name: string
  email: string
}

interface EventDetails {
  id: string
  title: string
  price: number
  description: string
  startDateTime: string
  endDateTime: string
  venue: {
    name: string
    address: string
    city: string
    state: string
  }
  name: string
}

function formatDateTime(dateStr: string) {
  const date = new Date(dateStr)
  return {
    date: date.toLocaleDateString(),
    time: date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  }
}

export default function BookingPage() {
  const router = useRouter()
  const params = useParams()
  const [isRedirecting, setIsRedirecting] = useState(false)
  const [formData, setFormData] = useState<BookingFormData>({
    quantity: 1,
    name: "",
    email: "",
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [event, setEvent] = useState<EventDetails | null>(null)
  const { getUserId } = useAuthUser()
  const userId = getUserId()
  const [ticketInfo, setTicketInfo] = useState<{
    availableTickets: number
  } | null>(null)

  useEffect(() => {
    async function fetchEvent() {
      if (!params?.id) return

      try {
        const bearerToken = await getBearerIdToken()

        const response = await fetch(
          `${BACKEND_ROUTES.eventsService}/api/v1/events/${params.id}`,
          {
            headers: {
              Accept: "application/json",
              Authorization: bearerToken,
            },
          }
        )
        if (!response.ok) {
          throw new Error("Failed to fetch event details")
        }
        const data = await response.json()
        setEvent(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load event")
      }
    }

    fetchEvent()
  }, [params?.id])

  // Fetch ticket availability
  useEffect(() => {
    async function fetchTicketAvailability() {
      if (!userId) {
        setTicketInfo(null) // Set to null when not logged in
        return
      }

      try {
        const ticketData = await getAvailableTickets(params.id as string)
        setTicketInfo({
          availableTickets: ticketData.available_tickets,
        })
      } catch (err) {
        console.error("Failed to fetch ticket availability:", err)
        setTicketInfo(null)
      }
    }

    fetchTicketAvailability()
  }, [params.id, userId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!userId) {
      router.push("/auth/login")
      return
    }
    if (!event || !params?.id) return
    if (loading || isRedirecting) return // Prevent double submission

    setLoading(true)
    setError(null)

    try {
      // Get the current user and bearer token
      const user = await getCurrentUser()
      const bearerToken = await getBearerIdToken()

      if (!bearerToken) {
        throw new Error("Please sign in to make a booking")
      }

      // 1. First create the booking record
      const bookingResponse = await fetch(
        `${BACKEND_ROUTES.bookingService}/api/v1/bookings`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: bearerToken,
          },
          body: JSON.stringify({
            event_id: params.id,
            user_id: user.userId,
            ticket_quantity: formData.quantity,
            email: formData.email,
          }),
        }
      )

      if (!bookingResponse.ok) {
        const errorData = await bookingResponse.json()
        throw new Error(errorData.detail || "Failed to create booking")
      }

      const bookingData = await bookingResponse.json()

      // If booking is confirmed (free event), go to confirmation
      if (bookingData.status === "CONFIRMED") {
        setIsRedirecting(true)
        // Use replace instead of push to prevent back navigation
        await router.replace(
          `/book/${bookingData.booking_id}/success?session_id=${bookingData.session_id}`
        )
        return
      }

      // Otherwise continue with payment flow
      const stripeResponse = await fetch("/api/stripe/booking", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bookingId: bookingData.booking_id,
          amount: event.price * formData.quantity * 100, // Convert to cents
          eventId: params.id,
          userId: user.userId,
          quantity: formData.quantity,
        }),
      })

      if (!stripeResponse.ok) {
        const errorData = await stripeResponse.json()
        throw new Error(errorData.error || "Failed to create payment session")
      }

      const { url } = await stripeResponse.json()
      setIsRedirecting(true)
      window.location.href = url // Use direct navigation for Stripe
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
      setLoading(false)
      setIsRedirecting(false)
    }
  }

  if (!event) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
      </div>
    )
  }

  const totalPrice = event.price * formData.quantity

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Book {event.title}</h1>

        <Card className="p-6 mb-6">
          <CardHeader>
            <CardTitle>Event Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4 mb-6">
              <p className="text-gray-600">{event.description}</p>

              {/* Date & Time Section */}
              <div className="flex items-start gap-3 py-4 px-2 border-b border-[hsl(var(--border))]">
                <div className="h-10 w-10 rounded-full bg-[hsl(var(--purple-100))] flex items-center justify-center">
                  <Calendar className="h-5 w-5 text-[hsl(var(--purple-600))]" />
                </div>
                <div>
                  <p className="font-medium">Event Date & Time</p>
                  <div className="text-sm text-muted-foreground">
                    <p>
                      Start: {formatDateTime(event.startDateTime).date} at{" "}
                      {formatDateTime(event.startDateTime).time}
                    </p>
                    {event.endDateTime && (
                      <p>
                        End: {formatDateTime(event.endDateTime).date} at{" "}
                        {formatDateTime(event.endDateTime).time}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Location Section */}
              <div className="flex items-start gap-3 pt-4 px-2">
                <div className="h-10 w-10 rounded-full bg-[hsl(var(--purple-100))] flex items-center justify-center">
                  <MapPin className="h-5 w-5 text-[hsl(var(--purple-600))]" />
                </div>
                <div>
                  <p className="font-medium">Event Location</p>
                  <p className="text-sm text-muted-foreground">
                    {event.venue.name}, {event.venue.address}
                    {event.venue.city && `, ${event.venue.city}`}
                    {event.venue.state && `, ${event.venue.state}`}
                  </p>
                </div>
              </div>
            </div>

            <div className="border-t pt-4 space-y-2">
              <div className="flex justify-between">
                <span className="font-medium">Price per ticket:</span>
                <span>${event.price.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Quantity:</span>
                <span>{formData.quantity}</span>
              </div>
              <div className="border-t pt-2">
                <div className="flex justify-between font-bold">
                  <span>Total:</span>
                  <span>${totalPrice.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <span className="font-medium">Available Tickets:</span>
              <span>
                {ticketInfo != null
                  ? ticketInfo.availableTickets === -1
                    ? "Unlimited"
                    : ticketInfo.availableTickets
                  : "Sign in to view"}
              </span>
            </div>
          </CardContent>
        </Card>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              placeholder="Enter your name"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="quantity">Number of Tickets</Label>
            <Input
              id="quantity"
              type="number"
              min="1"
              value={formData.quantity}
              onChange={(e) =>
                setFormData({ ...formData, quantity: parseInt(e.target.value) })
              }
              required
            />
          </div>

          {error && <ErrorMessageCallout errorMessage={error} />}

          <Button
            type="submit"
            disabled={loading || isRedirecting}
            className="w-full"
          >
            {loading || isRedirecting ? (
              <div className="flex items-center">
                <Spinner className="mr-2" />
                {isRedirecting ? "Booking..." : "Processing..."}
              </div>
            ) : event?.price === 0 ? (
              "Book for Free"
            ) : (
              "Proceed to Payment"
            )}
          </Button>
        </form>
      </div>
    </div>
  )
}
