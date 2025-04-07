"use client"

import { useRouter, useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle } from "lucide-react"

export default function RefundSuccessPage() {
  const router = useRouter()
  const params = useParams()

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto">
        <Card>
          <CardHeader>
            <div className="flex justify-center mb-2">
              <CheckCircle className="h-16 w-16 text-green-500" />
            </div>
            <CardTitle className="text-center text-2xl">
              Refund Request Submitted
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-center text-muted-foreground">
              Your refund request has been successfully submitted. We'll process
              it as soon as possible.
            </p>
            <p className="text-center text-muted-foreground">
              You will receive an email confirmation once your refund has been
              processed.
            </p>
            <p className="text-center text-sm font-medium">
              Reference ID: {params.id}
            </p>
            <div className="flex justify-center pt-4">
              <Button onClick={() => router.push("/my-events")}>
                View My Events
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
