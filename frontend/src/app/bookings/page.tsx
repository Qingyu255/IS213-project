"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ErrorMessageCallout } from "@/components/error-message-callout"
import { BACKEND_ROUTES } from "@/constants/backend-routes"
import { getBearerToken } from "@/utils/auth"

interface Booking {
  id: string
  event_id: string
  event_title: string
  ticket_quantity: number
  total_amount: number
  status: string
  created_at: string
}

export default function BookingsPage() {
  const router = useRouter()
  const [bookings, setBookings] = useState<Booking[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchBookings() {
      try {
        const res = await fetch(
          `${BACKEND_ROUTES.bookingService}/api/v1/bookings/my-bookings`,
          {
            headers: {
              Accept: "application/json",
              Authorization: await getBearerToken(),
            },
          }
        )

        if (!res.ok) {
          throw new Error(`Failed to fetch bookings: ${res.statusText}`)
        }

        const data = await res.json()
        setBookings(data)
      } catch (err: any) {
        setError(err.message || "An unknown error occurred")
      } finally {
        setIsLoading(false)
      }
    }
    fetchBookings()
  }, [])

  if (isLoading) return <div>Loading...</div>
  if (error) return <ErrorMessageCallout errorMessage={error} />
  if (!bookings.length) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-4xl mx-auto">
          <CardContent className="text-center py-8">
            <p className="mb-4">You haven't made any bookings yet.</p>
            <Button onClick={() => router.push("/events")}>
              Browse Events
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">My Bookings</h1>
        <div className="space-y-4">
          {bookings.map((booking) => (
            <Card
              key={booking.id}
              className="hover:shadow-md transition-shadow"
            >
              <CardContent className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-semibold mb-2">
                      {booking.event_title}
                    </h2>
                    <div className="space-y-1 text-sm text-muted-foreground">
                      <p>Booking ID: {booking.id}</p>
                      <p>Tickets: {booking.ticket_quantity}</p>
                      <p>Total: ${booking.total_amount.toFixed(2)}</p>
                      <p>
                        Booked on:{" "}
                        {new Date(booking.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <Badge
                    className={
                      booking.status === "CONFIRMED"
                        ? "bg-green-500"
                        : booking.status === "PENDING"
                        ? "bg-yellow-500"
                        : booking.status === "CANCELED"
                        ? "bg-red-500"
                        : "bg-gray-500"
                    }
                  >
                    {booking.status}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
