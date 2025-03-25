// NOT TESTED IF WORKING YET //
"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Textarea } from "@/components/ui/textarea";
import { AlertCircle, Loader2 } from "lucide-react";
import { getBearerToken } from "@/utils/auth";

interface PaymentVerification {
  verified: boolean;
  payment_intent_id: string;
  amount: number;
  currency: string;
  status: string;
  event_id: string;
  user_id: string;
  payment_date: string;
  can_refund: boolean;
}

interface RefundFormData {
  reason: string;
}

export default function EventRefundPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.eventId as string;
  
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentVerification, setPaymentVerification] = useState<PaymentVerification | null>(null);
  const [formData, setFormData] = useState<RefundFormData>({
    reason: "",
  });

  // Verify payment when the page loads
  useEffect(() => {
    const verifyPayment = async () => {
      try {
        const token = await getBearerToken();
        const response = await fetch(
          `${BACKEND_ROUTES.billingService}/api/payment/verify-event-payment`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": token,
            },
            body: JSON.stringify({
              event_id: eventId,
              user_id: "current_user_id", // Replace with actual user ID from auth context
            }),
          }
        );

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Failed to verify payment");
        }

        setPaymentVerification(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to verify payment");
      } finally {
        setVerifying(false);
        setLoading(false);
      }
    };

    verifyPayment();
  }, [eventId]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!paymentVerification?.payment_intent_id) return;

    setProcessing(true);
    setError(null);

    try {
      const response = await fetch(
        `${BACKEND_ROUTES.billingService}/api/refund/process`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": await getBearerToken(),
          },
          body: JSON.stringify({
            payment_intent_id: paymentVerification.payment_intent_id,
            reason: formData.reason,
            metadata: {
              event_id: eventId,
              refund_reason: formData.reason,
            },
          }),
        }
      );

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to process refund");
      }

      // Redirect to success page
      router.push(`/refund/success?refund_id=${data.refund_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setProcessing(false);
    }
  };

  if (loading || verifying) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Card>
          <CardContent className="flex items-center justify-center p-8">
            <Loader2 className="h-8 w-8 animate-spin" />
            <span className="ml-2">Verifying payment details...</span>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button variant="outline" onClick={() => router.back()}>
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  if (!paymentVerification?.verified || !paymentVerification?.can_refund) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>Refund Not Available</CardTitle>
            <CardDescription>
              {!paymentVerification?.verified
                ? "No payment found for this event."
                : "This payment is not eligible for refund."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={() => router.back()}>
              Return to Event
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Request Event Refund</CardTitle>
          <CardDescription>
            Please provide a reason for your refund request.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-6 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Amount Paid:</span>
              <span className="font-medium">
                {paymentVerification.amount / 100} {paymentVerification.currency.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Payment Date:</span>
              <span className="font-medium">
                {new Date(paymentVerification.payment_date).toLocaleDateString()}
              </span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Refund Reason
              </label>
              <Textarea
                name="reason"
                value={formData.reason}
                onChange={handleInputChange}
                placeholder="Please explain why you're requesting a refund"
                required
                className="w-full"
              />
            </div>

            <div className="flex gap-4">
              <Button
                type="submit"
                disabled={processing}
                className="flex-1"
              >
                {processing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  "Submit Refund Request"
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
} 