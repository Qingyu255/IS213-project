"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getBearerToken } from "@/utils/auth";

// Test scenarios data
const TEST_EVENT_DATA = {
  'test-success': {
    id: 'test-success',
    title: "Test Successful Payment",
    description: "This event is for testing successful payments",
    price: 2000,
    currency: "sgd",
  },
  'test-3ds': {
    id: 'test-3ds',
    title: "Test 3D Secure Payment",
    description: "This event is for testing 3D Secure authentication",
    price: 3000,
    currency: "sgd",
  },
  'test-fail': {
    id: 'test-fail',
    title: "Test Failed Payment",
    description: "This event is for testing payment failures",
    price: 4000,
    currency: "sgd",
  }
};

export default function EventPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.eventId as string;
  const [loading, setLoading] = useState(false);
  const [event, setEvent] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [fetchingEvent, setFetchingEvent] = useState(true);

  useEffect(() => {
    const fetchEventData = async () => {
      // If it's a test event, use the test data
      if (eventId.startsWith('test-')) {
        setEvent(TEST_EVENT_DATA[eventId as keyof typeof TEST_EVENT_DATA]);
        setFetchingEvent(false);
        return;
      }

      // Otherwise fetch real event data
      try {
        const response = await fetch(
          `${BACKEND_ROUTES.eventsService}/api/v1/events/${eventId}`,
          {
            headers: {
              Authorization: await getBearerToken(),
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch event details');
        }

        const data = await response.json();
        setEvent(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch event');
      } finally {
        setFetchingEvent(false);
      }
    };

    fetchEventData();
  }, [eventId]);

  const handlePaymentClick = async () => {
    if (!event) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_ROUTES.billingService}/api/payment/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": await getBearerToken(),
        },
        body: JSON.stringify({
          amount: event.price,
          currency: event.currency,
          description: `Payment for ${event.title}`,
          metadata: {
            event_id: event.id,
            event_title: event.title,
          },
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to create payment");
      }

      // Redirect to payment page with client secret
      router.push(`/payment?clientSecret=${data.payment.client_secret}&eventId=${event.id}`);
    } catch (error) {
      console.error("Payment error:", error);
      alert("Failed to initiate payment. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleRefundClick = () => {
    router.push(`/events/${eventId}/refund`);
  };

  if (fetchingEvent) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="flex items-center justify-center p-8">
            Loading event details...
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="p-8">
            <p className="text-red-500">{error || 'Event not found'}</p>
            <Button
              variant="outline"
              onClick={() => router.push('/events')}
              className="mt-4"
            >
              Return to Events
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <CardTitle>{event.title}</CardTitle>
          <CardDescription>{event.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <p className="text-2xl font-bold">
              {(event.price / 100).toFixed(2)} {event.currency.toUpperCase()}
            </p>
          </div>

          <div className="space-y-4">
            <Button
              onClick={handlePaymentClick}
              disabled={loading}
              className="w-full"
            >
              {loading ? "Processing..." : "Register and Pay"}
            </Button>

            <Button
              variant="outline"
              onClick={handleRefundClick}
              className="w-full"
            >
              Request Refund
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 