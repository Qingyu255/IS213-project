"use client"

import React from "react";
import { useSearchParams } from "next/navigation";
import EmbeddedCheckout from "./component";

export default function PaymentPage() {
  const searchParams = useSearchParams();
  const eventId = searchParams.get('eventId');
  const amount = searchParams.get('amount');
  const description = searchParams.get('description');

  if (!eventId || !amount) {
    return (
      <div className="p-4">
        <h1 className="text-xl font-bold mb-4">Invalid Payment Request</h1>
        <p>Missing required payment information. Please try again from the event page.</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Payment Page</h1>
      <p className="mb-4">Complete your payment for: {description || 'Event Registration'}</p>

      <EmbeddedCheckout 
        eventId={eventId}
        amount={parseInt(amount)}
        description={description || undefined}
      />
    </div>
  );
}

