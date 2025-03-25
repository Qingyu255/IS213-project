"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { getBearerToken } from "@/utils/auth";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  ArrowRight,
  Home,
  Calendar,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getCheckoutSession } from "../actions";
import { useEventCreation } from "@/providers/event-creation-provider";
import { toast } from "sonner";
import type { EventDetails } from "@/types/event";
import React from "react";

type SuccessProps = {
  searchParams: {
    session_id: string;
  };
};

export default function Success({ searchParams }: SuccessProps) {
  const router = useRouter();
  const [status, setStatus] = useState<
    "loading" | "verifying" | "creating" | "success" | "error"
  >("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [eventId, setEventId] = useState<string | null>(null);
  const [eventTitle, setEventTitle] = useState<string | null>(null);
  const [progress, setProgress] = useState(33);
  const { eventData, clearEventData } = useEventCreation();
  const isProcessing = useRef(false);
  // @ts-expect-error next docs says to use React.use but ts was screaming
  const sessionId = React.use(searchParams).session_id;

  useEffect(() => {
    async function processSuccess() {
      // Prevent duplicate processing
      if (isProcessing.current) {
        console.log("Already processing event creation, skipping duplicate call");
        return;
      }
      
      // Set processing flag to prevent duplicate calls
      isProcessing.current = true;
      
      try {
        if (!sessionId) {
          throw new Error("Missing session_id parameter");
        }

        // 1. Check context data first (primary source)
        let eventToCreate = eventData;
        
        if (eventToCreate) {
          console.log("Found event data in context, ID:", eventToCreate.id);
        } else {
          // 2. Fall back to localStorage if context data is not available
          console.log("Context data not found, checking localStorage fallback");
          const storedEventDataString = localStorage.getItem('pending_event_data');
          
          if (!storedEventDataString) {
            console.error("No event data found in either context or localStorage!");
            throw new Error("Event data not found. Please try creating your event again.");
          }
          
          try {
            eventToCreate = JSON.parse(storedEventDataString) as EventDetails;
            console.log("Retrieved event from localStorage, ID:", eventToCreate.id);
          } catch (error) {
            console.error("Error parsing localStorage event data:", error);
            throw new Error("Could not retrieve valid event data. Please try again.");
          }
        }
        
        // 3. Verify payment with Stripe
        const sessionResult = await getCheckoutSession(sessionId);
        
        if (!sessionResult.success) {
          console.error("Session verification failed:", sessionResult.error);
          throw new Error(`Payment verification failed: ${sessionResult.error}`);
        }
        
        const checkoutSession = sessionResult.session;
        
        if (!checkoutSession || checkoutSession.status !== 'complete') {
          throw new Error(`Payment not completed. Status: ${checkoutSession?.status || 'unknown'}`);
        }
        
        console.log("Payment verification successful");
        setStatus('verifying');
        setProgress(66);
        
        // 4. Make sure we have valid event data to proceed
        if (!eventToCreate || !eventToCreate.id) {
          throw new Error("Invalid event data. Please try creating your event again.");
        }
        
        // At this point we've verified eventToCreate is not null
        const validEventData = eventToCreate; // Non-null assertion via new variable
        
        setEventId(validEventData.id);
        setEventTitle(validEventData.title);
        console.log("Creating event with ID:", validEventData.id);
        
        // 5. Create the event with the service
        setStatus("creating");
        setProgress(90);

        const token = await getBearerToken();

        // Send the payload to the backend
        const createResponse = await fetch(
          `${BACKEND_ROUTES.createEventServiceUrl}/api/v1/create-event`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(validEventData),
          }
        );

        if (!createResponse.ok) {
          const errorText = await createResponse.text();
          let errorMessage;
          try {
            const errorData = JSON.parse(errorText);
            errorMessage = errorData.error || "Unknown error";
          } catch {
            errorMessage = errorText || "Unknown error";
          }
          throw new Error(`Event creation failed: ${errorMessage}`);
        }

        // Success! Clear the pending event data
        clearEventData();
        setProgress(100);
        setStatus("success");
        toast.success("Event created successfully!");
      } catch (error: Error | unknown) {
        console.error("Error in success flow:", error);
        setErrorMessage(
          error instanceof Error ? error.message : "An unknown error occurred"
        );
        setStatus("error");
      } finally {
        // Reset processing flag in case of mount/unmount scenarios
        // This ensures future mounts can still process if needed
        setTimeout(() => {
          isProcessing.current = false;
        }, 5000); // Add a small delay to prevent rapid retries
      }
    }

    processSuccess();
  }, [clearEventData]); // Removed eventData from dependencies

  // Show appropriate UI based on status
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="max-w-md w-full shadow-lg">
        {status === "loading" ||
        status === "verifying" ||
        status === "creating" ? (
          <>
            <CardHeader className="pb-0">
              <div className="w-full bg-muted rounded-full h-2.5 mb-6">
                <div
                  className="bg-primary h-2.5 rounded-full transition-all duration-500 ease-in-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <h2 className="text-2xl font-bold text-center">
                {status === "loading"
                  ? "Processing Payment"
                  : status === "verifying"
                  ? "Verifying Payment"
                  : "Creating Your Event"}
              </h2>
            </CardHeader>
            <CardContent className="pt-4 flex flex-col items-center">
              <div className="transition-all duration-300 ease-in-out">
                <Spinner size="lg" className="my-8" />
              </div>
              <p className="text-muted-foreground text-center">
                {status === "loading"
                  ? "Please wait while we confirm your payment..."
                  : status === "verifying"
                  ? "Confirming your payment was successful..."
                  : "Almost done! Setting up your event..."}
              </p>
            </CardContent>
          </>
        ) : status === "success" ? (
          <>
            <CardHeader className="pb-0">
              <div className="flex flex-col items-center animate-in fade-in slide-in-from-bottom-5 duration-500">
                <div className="bg-green-100 p-3 rounded-full">
                  <CheckCircle className="h-16 w-16 text-green-500" />
                </div>
                <Badge className="mt-4 bg-green-500">Payment Successful</Badge>
                <h2 className="text-2xl font-bold mt-4 text-center">
                  Event Created Successfully!
                </h2>
              </div>
            </CardHeader>
            <CardContent className="pt-2">
              <div className="animate-in fade-in slide-in-from-bottom-5 duration-500 delay-300">
                <p className="text-muted-foreground mb-6 text-center">
                  {eventTitle ? `"${eventTitle}"` : "Your event"} has been
                  created and is now live. You can view your event details or
                  return to the dashboard.
                </p>
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-3">
              <div className="w-full animate-in fade-in slide-in-from-bottom-5 duration-500 delay-500">
                <Button
                  onClick={() => router.push(`/events/${eventId}`)}
                  className="w-full"
                  size="lg"
                >
                  View Your Event
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
              <div className="w-full animate-in fade-in slide-in-from-bottom-5 duration-500 delay-700">
                <Button
                  variant="outline"
                  onClick={() => router.push("/dashboard")}
                  className="w-full"
                  size="lg"
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  Go to Dashboard
                </Button>
              </div>
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
                  {errorMessage || "We couldn't complete your event creation."}
                </p>
                <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
                  <div className="flex">
                    <AlertCircle className="h-5 w-5 text-red-500 mr-2 shrink-0" />
                    <p className="text-sm text-red-700">
                      Your payment was successful, but we couldn&apos;t create
                      your event. Please contact support.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-3">
              <div className="w-full animate-in fade-in slide-in-from-bottom-5 duration-500 delay-500">
                <Button
                  onClick={() => router.push("/create")}
                  className="w-full"
                  size="lg"
                >
                  Try Again
                </Button>
              </div>
              <div className="w-full animate-in fade-in slide-in-from-bottom-5 duration-500 delay-700">
                <Button
                  variant="outline"
                  onClick={() => router.push("/")}
                  className="w-full"
                  size="lg"
                >
                  <Home className="mr-2 h-4 w-4" />
                  Go Home
                </Button>
              </div>
            </CardFooter>
          </>
        )}
      </Card>
    </div>
  );
}

