"use client"

import React, { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import EmbeddedCheckout from "./component";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

function PaymentContent() {
  const searchParams = useSearchParams();
  const eventId = searchParams.get('eventId');
  const amount = searchParams.get('amount');
  const description = searchParams.get('description');
  
  // Check if this is an event creation payment
  const isEventCreation = description?.includes('Event Creation Fee');

  if (!eventId || !amount) {
    return (
      <div className="p-4 max-w-3xl mx-auto">
        <h1 className="text-xl font-bold mb-4">Invalid Payment Request</h1>
        <p>Missing required payment information. Please try again from the event page.</p>
        <Link href="/" className="text-primary hover:underline inline-flex items-center mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Return to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">
          {isEventCreation ? 'Event Creation Fee' : 'Complete Your Payment'}
        </h1>
        
        {isEventCreation ? (
          <div className="space-y-4 mb-6">
            <p>A one-time fee of $2 SGD is required to publish your event on our platform.</p>
            <p>This fee helps us maintain high-quality event listings and supports our platform operations.</p>
            <p className="text-sm text-muted-foreground">After successful payment, your event will be automatically created and published.</p>
          </div>
        ) : (
          <p className="mb-4">Complete your payment for: {description || 'Event Registration'}</p>
        )}
      </div>

      <EmbeddedCheckout 
        eventId={eventId}
        amount={parseInt(amount)}
        description={description || undefined}
      />
      
      <div className="mt-6 text-center">
        <Link href="/create" className="text-sm text-muted-foreground hover:underline inline-flex items-center">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Cancel and return to event form
        </Link>
      </div>
    </div>
  );
}

export default function PaymentPage() {
  return (
    <Suspense fallback={
      <div className="p-6 max-w-3xl mx-auto text-center">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-secondary rounded w-1/3 mx-auto"></div>
          <div className="h-4 bg-secondary rounded w-2/3 mx-auto"></div>
          <div className="h-4 bg-secondary rounded w-1/2 mx-auto"></div>
          <div className="h-64 bg-secondary rounded w-full mx-auto mt-8"></div>
        </div>
      </div>
    }>
      <PaymentContent />
    </Suspense>
  );
}

