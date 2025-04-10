"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { getBearerIdToken } from "@/utils/auth"
import { Button } from "@/components/ui/button"
import { ErrorMessageCallout } from "@/components/error-message-callout"
import { Spinner } from "@/components/ui/spinner"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BACKEND_ROUTES } from "@/constants/backend-routes"
import Image from "next/image"
import { MapPin, Calendar } from "lucide-react"
import { Separator } from "@/components/ui/separator"

// Define interfaces based on your API response
interface TicketResponse {
  ticket_id: string
  booking_id: string
  status: string
  created_at: string
  updated_at?: string
}

interface BookingResponse {
  booking_id: string
  user_id: string
  event_id: string
  ticket_quantity: number
  total_amount: number
  status: string
  created_at: string
  updated_at?: string
  tickets: TicketResponse[]
}

// Updated event interface to match the provided structure
interface Venue {
  address: string
  name: string
  city: string
  state: string
  additionalDetails: string
  coordinates: {
    lat: number
    lng: number
  }
}

interface Organizer {
  id: string
  username: string
}

interface EventDetails {
  id: string
  title: string
  description: string
  startDateTime: string
  endDateTime: string
  imageUrl: string
  venue: Venue
  price: number
  capacity: number
  createdAt: string
  updatedAt: string
  categories: string[]
  organizer: Organizer
}

export default function RefundPage() {
  const router = useRouter()
  const params = useParams()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [booking, setBooking] = useState<BookingResponse | null>(null)
  const [event, setEvent] = useState<EventDetails | null>(null)

  useEffect(() => {
    async function fetchBookingAndEvent() {
      if (!params?.id) return

      try {
        setLoading(true)
        const bearerToken = await getBearerIdToken()
        if (!bearerToken) {
          throw new Error("Please sign in to view booking details")
        }

        // Fetch booking details
        const bookingResponse = await fetch(
          `${BACKEND_ROUTES.bookingService}/api/v1/bookings/${params.id}`,
          {
            headers: {
              Accept: "application/json",
              Authorization: bearerToken,
            },
          }
        )

        if (!bookingResponse.ok) {
          throw new Error("Failed to fetch booking details")
        }

        const bookingData = await bookingResponse.json()
        setBooking(bookingData)

        // Fetch event details using the event_id from the booking
        if (bookingData.event_id) {
          const eventResponse = await fetch(
            `${BACKEND_ROUTES.eventsService}/api/v1/events/${bookingData.event_id}`,
            {
              headers: {
                Accept: "application/json",
                Authorization: bearerToken,
              },
            }
          )

          if (eventResponse.ok) {
            const eventData = await eventResponse.json()
            setEvent(eventData)
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load booking")
      } finally {
        setLoading(false)
      }
    }

    fetchBookingAndEvent()
  }, [params?.id])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!booking || !params?.id) return

    setLoading(true)
    setError(null)

    try {
      // Get the current user and bearer token
      const bearerToken = await getBearerIdToken()

      if (!bearerToken) {
        throw new Error("Please sign in to request a refund")
      }

      // Submit the refund request with hardcoded reason
      const refundResponse = await fetch(
        `${BACKEND_ROUTES.refundService}/api/v1/booking-refund`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: bearerToken,
          },
          body: JSON.stringify({
            booking_id: params.id,
            reason: "requested_by_customer",
          }),
        }
      )

      if (!refundResponse.ok) {
        const errorData = await refundResponse.json()
        throw new Error(errorData.detail || "Failed to process refund request")
      }

      // Redirect to success page
      router.push(`/refund/${params.id}/success`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setLoading(false)
    }
  }

  // Format date and time
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  if (loading && !booking) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
      </div>
    )
  }

  // Calculate total amount from price and quantity
  const totalAmount =
    event && booking ? event.price * booking.ticket_quantity : 0

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Request a Refund</h1>

        {booking && event ? (
          <Card className="overflow-hidden">
            <div className="w-full">
              <Image
                src={event.imageUrl || "/eventplaceholder.png"}
                alt={event.title}
                width={800}
                height={400}
                className="w-full object-cover rounded-t-lg"
              />
            </div>
            <CardHeader>
              <CardTitle>{event.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Event description */}
              <div className="text-muted-foreground">{event.description}</div>

              {/* Event date and time */}
              <div className="space-y-2">
                <div className="flex items-start gap-2">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="font-medium">
                      {formatDate(event.startDateTime)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {formatTime(event.startDateTime)} -{" "}
                      {formatTime(event.endDateTime)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Venue information */}
              <div className="space-y-2">
                <div className="flex items-start gap-2">
                  <MapPin className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="font-medium">{event.venue.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {event.venue.address}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {event.venue.city}
                      {event.venue.state ? `, ${event.venue.state}` : ""}
                    </p>
                  </div>
                </div>
              </div>

              {/* Booking details */}
              <div className="border-t pt-4 space-y-2">
                <div className="flex justify-between">
                  <span className="font-medium">Price per ticket:</span>
                  <span>${event.price.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Quantity:</span>
                  <span>{booking.ticket_quantity}</span>
                </div>
                <div className="border-t pt-2">
                  <div className="flex justify-between font-bold">
                    <span>Total:</span>
                    <span>${totalAmount.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Refund request section */}
              <div>
                <p className="mb-6">
                  We're sorry to hear you'd like a refund for this event. By
                  clicking the button below, you confirm that you want to
                  request a refund for this booking.
                </p>

                {error && <ErrorMessageCallout errorMessage={error} />}
                <div className="mt-4" />

                <div className="flex gap-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => router.back()}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="flex-1"
                  >
                    {loading ? <Spinner /> : "Confirm Refund Request"}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : error ? (
          <Card>
            <CardContent className="py-6">
              <ErrorMessageCallout errorMessage={error} />
              <Button onClick={() => router.back()} className="mt-4">
                Go Back
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="py-6 text-center">
              <p>Loading booking details...</p>
              <Spinner className="mt-4" />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
