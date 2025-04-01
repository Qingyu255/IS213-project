"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

const TEST_SCENARIOS = [
  {
    title: "Successful Payment",
    description: "Test a successful payment flow",
    amount: 2000,
    eventId: "test-success",
  },
  {
    title: "3D Secure Payment",
    description: "Test a payment requiring authentication",
    amount: 3000,
    eventId: "test-3ds",
  },
  {
    title: "Failed Payment",
    description: "Test a payment that will fail",
    amount: 4000,
    eventId: "test-fail",
  },
];

export default function TestPaymentsPage() {
  const router = useRouter();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Payment Test Scenarios</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {TEST_SCENARIOS.map((scenario) => (
          <Card key={scenario.eventId}>
            <CardHeader>
              <CardTitle>{scenario.title}</CardTitle>
              <CardDescription>{scenario.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="mb-4">
                Amount: ${(scenario.amount / 100).toFixed(2)} SGD
              </p>
              <Button
                onClick={() => router.push(`/events/${scenario.eventId}`)}
                className="w-full"
              >
                Test This Scenario
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-8 p-4 bg-muted rounded-lg">
        <h2 className="font-semibold mb-2">Test Card Numbers</h2>
        <ul className="space-y-2 text-sm">
          <li>Success: 4242 4242 4242 4242</li>
          <li>Requires Authentication: 4000 0027 6000 3184</li>
          <li>Payment Fails: 4000 0000 0000 0002</li>
          <li>Use any future date for expiry and any 3 digits for CVC</li>
        </ul>
      </div>
    </div>
  );
} 