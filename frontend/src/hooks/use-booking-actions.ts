"use client"

import { useState } from "react"
import { updateBookingStatus } from "@/lib/api/tickets";
import { toast } from "sonner"

export function useBookingActions() {
  const [processingBookingId, setProcessingBookingId] = useState<string | null>(null)

  const handleBookingAction = async (bookingId: string, action: "cancel" | "refund") => {
    setProcessingBookingId(bookingId)
    try {
      await updateBookingStatus(bookingId, action)
      toast.success("Success", {
        description: `Booking ${action}ed successfully`,
      })
      return true
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to ${action} booking`
      toast.error("Error", {
        description: errorMessage,
      })
      throw err
    } finally {
      setProcessingBookingId(null)
    }
  }

  return {
    processingBookingId,
    handleBookingAction,
  }
}

