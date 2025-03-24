"use client"

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { getBearerToken } from "@/utils/auth";
import { Spinner } from "@/components/ui/spinner";
import { CheckCircle, XCircle, AlertCircle } from "lucide-react";

export default function PaymentSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<
    "loading" | "verifying" | "creating" | "success" | "error"
  >("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [eventId, setEventId] = useState<string | null>(null);
  
  // Get eventId and payment_intent from the URL
  const eventIdParam = searchParams.get("eventId");
  const paymentIntentParam = searchParams.get("payment_intent");
  const paymentIntentClientSecretParam = searchParams.get("payment_intent_client_secret");
  
  // Effect to handle the process when component mounts
  useEffect(() => {
    async function processPaymentSuccess() {
      try {
        // Check if we have the required params
        if (!eventIdParam || !paymentIntentParam) {
          throw new Error("Missing required payment parameters");
        }

        // Step 1: Get the pending event data from localStorage
        const storedEventData = localStorage.getItem("pending_event_data");
        if (!storedEventData) {
          throw new Error("No pending event data found");
        }

        setStatus("verifying");
        
        // Step 2: Verify payment was successful with the payment service
        const verifyResponse = await fetch(`${BACKEND_ROUTES.billingService}/api/payment/verify`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            payment_intent_id: paymentIntentParam
          }),
        });

        if (!verifyResponse.ok) {
          const errorData = await verifyResponse.json();
          throw new Error(
            `Payment verification failed: ${errorData.error || "Unknown error"}`
          );
        }

        const verifyData = await verifyResponse.json();
        
        // Check if payment is actually successful
        if (!verifyData.verified || verifyData.status !== "succeeded") {
          throw new Error(
            `Payment not completed successfully. Status: ${verifyData.status}`
          );
        }

        // Step 3: Create the event with the composite service
        setStatus("creating");
        const eventData = JSON.parse(storedEventData);
        setEventId(eventData.id);

        const token = await getBearerToken();
        const createResponse = await fetch(`${BACKEND_ROUTES.createEventService}/api/events`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(eventData),
        });

        if (!createResponse.ok) {
          const errorData = await createResponse.json();
          throw new Error(
            `Event creation failed: ${errorData.error || "Unknown error"}`
          );
        }

        // Step 4: Success! Clear the pending event data
        localStorage.removeItem("pending_event_data");
        setStatus("success");
      } catch (error: any) {
        console.error("Error in payment success flow:", error);
        setErrorMessage(error.message || "An unknown error occurred");
        setStatus("error");
      }
    }

    processPaymentSuccess();
  }, [eventIdParam, paymentIntentParam, paymentIntentClientSecretParam]);

  // Render different content based on status
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="max-w-md w-full p-6 bg-card rounded-lg shadow-lg">
        {status === "loading" || status === "verifying" || status === "creating" ? (
          <div className="text-center py-8">
            <Spinner className="mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">
              {status === "loading" ? "Processing" : 
               status === "verifying" ? "Verifying Payment" : 
               "Creating Your Event"}
            </h2>
            <p className="text-muted-foreground">
              {status === "loading" ? "Please wait..." : 
               status === "verifying" ? "Confirming your payment with our payment provider..." : 
               "Setting up your event. This will just take a moment..."}
            </p>
          </div>
        ) : status === "success" ? (
          <div className="text-center py-8">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Event Created Successfully!</h2>
            <p className="text-muted-foreground mb-6">
              Your payment was processed and your event has been created.
            </p>
            <div className="flex flex-col gap-3">
              <Button onClick={() => router.push(`/events/${eventId}`)}>
                View Your Event
              </Button>
              <Button variant="outline" onClick={() => router.push("/dashboard")}>
                Go to Dashboard
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Something Went Wrong</h2>
            <p className="text-muted-foreground mb-6">
              {errorMessage || "We couldn't complete your event creation."}
            </p>
            <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
                <p className="text-sm text-red-700">
                  If you were charged, don't worry - we'll automatically process a refund.
                </p>
              </div>
            </div>
            <div className="flex flex-col gap-3">
              <Button onClick={() => router.push("/create")}>
                Try Again
              </Button>
              <Button variant="outline" onClick={() => router.push("/")}>
                Go Home
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 