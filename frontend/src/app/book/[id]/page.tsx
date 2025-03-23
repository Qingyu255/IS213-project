"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ErrorMessageCallout } from "@/components/error-message-callout"
import { BACKEND_ROUTES } from "@/constants/backend-routes"
import { getBearerToken } from "@/utils/auth"
import { EventDetails } from "@/types/event"

export default function BookingPage() {
  const params = useParams()
  const router = useRouter()
  const [event, setEvent] = useState<EventDetails | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    ticketQuantity: 1,
    customerName: "",
    customerEmail: "",
    customerPhone: "",
  })

  useEffect(() => {
    async function fetchEvent() {
      try {
        const res = await fetch(
          `${BACKEND_ROUTES.eventsService}/api/v1/events/${params.id}`,
          {
            headers: {
              Accept: "application/json",
              Authorization: await getBearerToken(),
            },
          }
        )

        if (!res.ok) {
          throw new Error(`Failed to fetch event: ${res.statusText}`)
        }

        const data = await res.json()
        setEvent(data)
      } catch (err: any) {
        setError(err.message || "An unknown error occurred")
      } finally {
        setIsLoading(false)
      }
    }
    fetchEvent()
  }, [params.id])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === "ticketQuantity"
          ? Math.min(Math.max(1, parseInt(value) || 1), 10)
          : value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!event) return

    setIsSubmitting(true)
    try {
      const res = await fetch(
        `${BACKEND_ROUTES.bookingService}/api/v1/bookings/book`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: await getBearerToken(),
          },
          body: JSON.stringify({
            event_id: params.id,
            ticket_quantity: formData.ticketQuantity,
            total_amount: event.price * formData.ticketQuantity,
            customer_name: formData.customerName,
            customer_email: formData.customerEmail,
            customer_phone: formData.customerPhone,
          }),
        }
      )

      if (!res.ok) {
        throw new Error(`Failed to create booking: ${res.statusText}`)
      }

      const bookingData = await res.json()
      router.push(`/bookings/${bookingData.id}/success`)
    } catch (err: any) {
      setError(err.message || "Failed to create booking")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) return <div>Loading...</div>
  if (error) return <ErrorMessageCallout errorMessage={error} />
  if (!event) return <div>Event not found</div>

  return (
    <div className="container mx-auto px-4 py-8">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Book Tickets - {event.title}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="ticketQuantity">Number of Tickets</Label>
                <Input
                  id="ticketQuantity"
                  name="ticketQuantity"
                  type="number"
                  min={1}
                  max={Math.min(10, event.capacity || 10)}
                  value={formData.ticketQuantity}
                  onChange={handleInputChange}
                />
                <div className="text-sm text-muted-foreground mt-1">
                  Price per ticket: ${event.price.toFixed(2)}
                  <br />
                  Total: ${(event.price * formData.ticketQuantity).toFixed(2)}
                </div>
              </div>

              <div>
                <Label htmlFor="customerName">Full Name</Label>
                <Input
                  id="customerName"
                  name="customerName"
                  value={formData.customerName}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div>
                <Label htmlFor="customerEmail">Email</Label>
                <Input
                  id="customerEmail"
                  name="customerEmail"
                  type="email"
                  value={formData.customerEmail}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div>
                <Label htmlFor="customerPhone">Phone Number</Label>
                <Input
                  id="customerPhone"
                  name="customerPhone"
                  type="tel"
                  value={formData.customerPhone}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="flex justify-end space-x-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Processing..." : "Book Now"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
