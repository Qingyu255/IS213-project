"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams, useParams } from "next/navigation"
import { confirmBooking } from "@/app/book/actions"
import { getBearerIdToken } from "@/utils/auth"
import { Spinner } from "@/components/ui/spinner"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card"
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Home,
  ArrowRight,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { getBooking } from "@/lib/api/tickets"

interface BookingDetails {
  booking_id: string
  status: string
  ticket_quantity: number
  total_amount?: number
  event_id: string
}

export default function BookingSuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const params = useParams()
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  )
  const [error, setError] = useState<string | null>(null)
  const [booking, setBooking] = useState<BookingDetails | null>(null)
  const bookingId = params.id as string
  const sessionId = searchParams.get("session_id")
  const price = Number(searchParams.get("price")) || 0

  useEffect(() => {
    async function processBooking() {
      try {
        // Get the bearer token
        const bearerToken = await getBearerIdToken()
        if (!bearerToken) {
          setStatus("error")
          setError("Please log in to view your booking")
          return
        }

        // First get booking details
        const bookingData = await getBooking(bookingId)
        console.log("Initial booking data:", bookingData) // Debug log

        // If there's a session ID, this is a paid booking that needs confirmation
        if (sessionId && bookingData.status !== "CONFIRMED") {
          const result = await confirmBooking(bookingId, sessionId, bearerToken)
          if (!result.success) {
            throw new Error(result.error || "Failed to confirm booking")
          }
          // Refresh booking data after confirmation
          const confirmedBookingData = await getBooking(bookingId)
          console.log("Confirmed booking data:", confirmedBookingData) // Debug log

          setBooking({
            booking_id: confirmedBookingData.booking_id,
            status: confirmedBookingData.status,
            ticket_quantity: confirmedBookingData.tickets.length,
            event_id: confirmedBookingData.event_id,
            total_amount: price * confirmedBookingData.tickets.length,
          })
        } else {
          // For free events or already confirmed bookings
          setBooking({
            booking_id: bookingData.booking_id,
            status: bookingData.status,
            ticket_quantity: bookingData.tickets.length,
            event_id: bookingData.event_id,
            total_amount: price * bookingData.tickets.length,
          })
        }

        // Important: Set status to success after setting the booking
        setStatus("success")
      } catch (err) {
        console.error("Error processing booking:", err) // Debug log
        setStatus("error")
        setError(
          err instanceof Error ? err.message : "Failed to process booking"
        )
      }
    }

    processBooking()
  }, [bookingId, sessionId, price])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="max-w-md w-full shadow-lg">
        {status === "loading" ? (
          <>
            <CardHeader className="pb-0">
              <h2 className="text-2xl font-bold text-center">
                Processing Your Booking
              </h2>
            </CardHeader>
            <CardContent className="pt-4 flex flex-col items-center">
              <Spinner size="lg" className="my-8" />
              <p className="text-muted-foreground text-center">
                Please wait while we confirm your booking...
              </p>
            </CardContent>
          </>
        ) : status === "success" && booking ? (
          <>
            <CardHeader className="pb-0">
              <div className="flex flex-col items-center animate-in fade-in slide-in-from-bottom-5 duration-500">
                <div className="bg-green-100 p-3 rounded-full">
                  <CheckCircle className="h-16 w-16 text-green-500" />
                </div>
                <Badge className="mt-4 bg-green-500">Booking Confirmed</Badge>
                <h2 className="text-2xl font-bold mt-4 text-center">
                  Booking Successful!
                </h2>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-5 duration-500 delay-300">
                <div className="text-muted-foreground text-center mb-6">
                  Your booking has been confirmed successfully.
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Tickets:</span>
                    <span className="font-medium">
                      {booking.ticket_quantity}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-3">
              <Button
                onClick={() => router.push("/my-events")}
                className="w-full animate-in fade-in slide-in-from-bottom-5 duration-500 delay-500"
                size="lg"
              >
                View Your Bookings
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardFooter>
          </>
        ) : (
          <>
            <CardHeader className="pb-0">
              <div className="flex flex-col items-center animate-in fade-in slide-in-from-bottom-5 duration-500">
                <div className="bg-red-100 p-3 rounded-full">
                  <XCircle className="h-16 w-16 text-red-500" />
                </div>
                <h2 className="text-2xl font-bold mt-4 text-center">
                  Something Went Wrong
                </h2>
              </div>
            </CardHeader>
            <CardContent className="pt-2">
              <div className="animate-in fade-in slide-in-from-bottom-5 duration-500 delay-300">
                <p className="text-muted-foreground mb-6 text-center">
                  {error || "We couldn't process your booking."}
                </p>
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="flex">
                    <AlertCircle className="h-5 w-5 text-red-500 mr-2 shrink-0" />
                    <p className="text-sm text-red-700">
                      Please try again or contact support if the problem
                      persists.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button
                onClick={() => router.push("/")}
                className="w-full animate-in fade-in slide-in-from-bottom-5 duration-500 delay-500"
                size="lg"
              >
                <Home className="mr-2 h-4 w-4" />
                Return to Home
              </Button>
            </CardFooter>
          </>
        )}
      </Card>
    </div>
  )
}
