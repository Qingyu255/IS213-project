"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle2 } from "lucide-react"
import { BACKEND_ROUTES } from "@/constants/backend-routes"
import { getBearerToken } from "@/utils/auth"

export default function BookingSuccessPage() {
  const params = useParams()
  const router = useRouter()

  return (
    <div className="container mx-auto px-4 py-8">
      <Card className="max-w-2xl mx-auto">
        <CardHeader className="text-center">
          <CheckCircle2 className="w-16 h-16 mx-auto text-green-500 mb-4" />
          <CardTitle className="text-2xl">Booking Successful!</CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          <p>Your booking has been confirmed.</p>
          <p className="text-sm text-muted-foreground">
            Booking ID: {params.id}
          </p>
          <div className="flex justify-center space-x-4 mt-6">
            <Button onClick={() => router.push("/bookings")}>
              View My Bookings
            </Button>
            <Button variant="outline" onClick={() => router.push("/events")}>
              Browse More Events
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
