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
  date: string
  location: string
}

export default function BookingPage() {
  const router = useRouter()
  const params = useParams()
  const [formData, setFormData] = useState<BookingFormData>({
    quantity: 1,
    name: "",
    email: "",
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [event, setEvent] = useState<EventDetails | null>(null)

  useEffect(() => {
    async function fetchEvent() {
      if (!params?.id) return

      try {
        const bearerToken = await getBearerIdToken()
        if (!bearerToken) {
          throw new Error("Please sign in to view event details")
        }

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!event || !params?.id) return

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
      console.log("Booking data:", bookingData)

      if (!bookingData.booking_id) {
        throw new Error("No booking ID in response")
      }

      // 2. Then create the Stripe session
      const stripeResponse = await fetch("/api/stripe/booking", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bookingId: bookingData.booking_id,
          amount: event.price * formData.quantity * 100, // Convert to cents
          eventTitle: event.title,
          quantity: formData.quantity,
          successUrl: `${window.location.origin}/book/${bookingData.booking_id}/success?session_id={CHECKOUT_SESSION_ID}`,
        }),
      })

      if (!stripeResponse.ok) {
        const errorData = await stripeResponse.json()
        throw new Error(errorData.error || "Failed to create payment session")
      }

      const { url } = await stripeResponse.json()
      router.push(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setLoading(false)
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
            <div className="space-y-2">
              <p className="text-gray-600">{event.description}</p>
              <div className="flex justify-between">
                <span className="font-medium">Date:</span>
                <span>{new Date(event.date).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Location:</span>
                <span>{event.location}</span>
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

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? (
              <Spinner />
            ) : (
              `Proceed to Payment - $${totalPrice.toFixed(2)}`
            )}
          </Button>
        </form>
      </div>
    </div>
  )
}
