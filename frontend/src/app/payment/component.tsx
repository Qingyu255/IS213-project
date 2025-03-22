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
  amount?: number;
  currency?: string;
}

export default function EmbeddedCheckoutPage({
  amount = 1000,
  currency = "usd",
}: EmbeddedCheckoutProps) {
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClientSecret = async () => {
      try {
        // Construct the payment request payload that matches your backend PaymentRequest model.
        // Note: "payment_method" is required by the backend model.
        // Since Embedded Checkout collects the payment method, you can send an empty string or a placeholder.
        const payload = {
          amount,              // Amount in cents
          currency,            // e.g., "usd"
          payment_method: "",  // Placeholder (will be set later by Stripe Embedded Checkout)
          description: "",     // Optional description
          metadata: {},        // Optional metadata
          customer_email: "",  // Optional receipt email
        };

        // Send a POST request to your backend payment endpoint.
        const response = await fetch(`${BACKEND_ROUTES.billingService}/api/payment/process`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
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
        <StripeEmbeddedCheckout />
      </EmbeddedCheckoutProvider>
    </div>
  );
}