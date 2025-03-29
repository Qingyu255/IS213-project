"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams, useParams } from "next/navigation"
import { confirmBooking } from "@/app/book/actions"
import { signInWithRedirect } from "aws-amplify/auth"
import { getBearerToken } from "@/utils/auth"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"
import { ErrorMessageCallout } from "@/components/error-message-callout"

export default function BookingSuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const params = useParams()
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  )
  const [error, setError] = useState<string | null>(null)
  const bookingId = params.id as string
  const sessionId = searchParams.get("session_id")

  useEffect(() => {
    const confirmBookingStatus = async () => {
      if (!bookingId || !sessionId) {
        setStatus("error")
        setError("Missing booking or session information")
        return
      }

      try {
        // Get the bearer token on the client side
        const bearerToken = await getBearerToken()
        if (!bearerToken) {
          setStatus("error")
          setError("Please log in to confirm your booking")
          return
        }

        const result = await confirmBooking(bookingId, sessionId, bearerToken)

        if (result.requiresAuth) {
          // Store the booking and session IDs in localStorage
          localStorage.setItem("pendingBookingId", bookingId)
          localStorage.setItem("pendingSessionId", sessionId)
          // Try to sign in
          try {
            await signInWithRedirect()
            return // The page will reload after auth
          } catch (err) {
            setStatus("error")
            setError("Authentication failed. Please try again.")
          }
          return
        }

        if (result.success) {
          setStatus("success")
        } else {
          setStatus("error")
          setError(result.error || "Failed to confirm booking")
        }
      } catch (err) {
        setStatus("error")
        setError(
          err instanceof Error ? err.message : "Failed to confirm booking"
        )
      }
    }

    confirmBookingStatus()
  }, [bookingId, sessionId])

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">
            Confirming your booking...
          </h1>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
        </div>
      </div>
    )
  }

  if (status === "error") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error</h1>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={() => router.push("/")}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Return to Home
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-green-600 mb-4">
          Booking Confirmed!
        </h1>
        <p className="text-gray-600">
          Your booking has been successfully confirmed.
        </p>
        <button
          onClick={() => router.push("/")}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Return to Home
        </button>
      </div>
    </div>
  )
}
