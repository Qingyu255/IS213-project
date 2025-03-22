"use client"

import React, { useState, useEffect } from "react";
import {
  EmbeddedCheckout as StripeEmbeddedCheckout,
  EmbeddedCheckoutProvider,
} from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import { BACKEND_ROUTES } from "@/constants/backend-routes";

// Load Stripe with your publishable key and required beta flag.
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!, {
  betas: ["custom_checkout_beta_5"],
});

interface EmbeddedCheckoutProps {
  eventId: string;
  amount?: number;
  currency?: string;
  description?: string;
}

export default function EmbeddedCheckoutPage({
  eventId,
  amount = 1000,
  currency = "sgd",
  description = "Event ticket purchase",
}: EmbeddedCheckoutProps) {
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClientSecret = async () => {
      try {
        const payload = {
          event_id: eventId,
          amount,              
          currency,            
          description,     
          metadata: {
            event_id: eventId
          }
        };

        console.log("Sending payment request:", payload);

        const response = await fetch(`${BACKEND_ROUTES.billingService}/api/payment/process`, {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          body: JSON.stringify(payload),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to create payment');
        }
        
        const data = await response.json();
        console.log("Payment response:", data);

        if (data.payment && data.payment.client_secret) {
          setClientSecret(data.payment.client_secret);
        } else {
          throw new Error("No client secret returned from server");
        }
      } catch (err: any) {
        console.error("Payment error:", err);
        setError("Error fetching client secret: " + err.message);
      } finally {
        setLoading(false);
      }
    };

    if (eventId && amount > 0) {
      fetchClientSecret();
    }
  }, [eventId, amount, currency, description]);

  if (loading) return <div className="p-4">Loading payment checkout...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (!clientSecret) return <div className="p-4">Unable to initialize payment.</div>;

  return (
    <div id="checkout" className="w-full max-w-md mx-auto p-4">
      <EmbeddedCheckoutProvider stripe={stripePromise} options={{ clientSecret }}>
        <StripeEmbeddedCheckout />
      </EmbeddedCheckoutProvider>
    </div>
  );
}