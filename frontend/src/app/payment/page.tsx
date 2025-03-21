"use client"

import React from "react";
import EmbeddedCheckout from "./component";

export default function PaymentPage() {
  return (
    <div style={{ padding: "2rem" }}>
      <h1>Payment Page</h1>
      <p>This page demonstrates the embedded checkout flow.</p>

      {/* Pass dynamic values if needed */}
      <EmbeddedCheckout amount={2000} currency="usd" />
    </div>
  );
}