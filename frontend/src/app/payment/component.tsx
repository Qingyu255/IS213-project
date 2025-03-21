"use client"

import React, { useState, useEffect } from "react";
import { EmbeddedCheckout, EmbeddedCheckoutProvider } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";

// Load Stripe with your publishable key. The exclamation mark (!) asserts the variable is not undefined.
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!, {
  betas: ["custom_checkout_beta_5"],
});

interface EmbeddedCheckoutProps {
  amount?: number;
  currency?: string;
}

export default function EmbeddedCheckout({
  amount = 1000,
  currency = "usd",
}: EmbeddedCheckoutProps) {
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClientSecret = async () => {
      try {
        // This endpoint is your backend's route that creates a PaymentIntent (or Checkout Session)
        // and returns { clientSecret: '...' }
        const response = await fetch("/api/payment/process", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ amount, currency }),
        });

        const data = await response.json();
        if (data.clientSecret) {
          setClientSecret(data.clientSecret);
        } else {
          setError("Error: No client secret returned from server.");
        }
      } catch (err: any) {
        setError("Error fetching client secret: " + err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchClientSecret();
  }, [amount, currency]);

  if (loading) return <div>Loading embedded checkout...</div>;
  if (error) return <div>{error}</div>;
  if (!clientSecret) return <div>No client secret available.</div>;

  return (
    <div id="checkout">
      <EmbeddedCheckoutProvider stripe={stripePromise} options={{ clientSecret }}>
        <EmbeddedCheckout />
      </EmbeddedCheckoutProvider>
    </div>
  );
}