"use client";

import React, { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import Link from "next/link";

interface RefundDetails {
  refund_id: string;
  payment_intent_id: string;
  amount: number;
  currency: string;
  status: string;
  reason: string;
  created: number;
}

export default function RefundSuccessPage() {
  const searchParams = useSearchParams();
  const refundId = searchParams.get("refund_id");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refundDetails, setRefundDetails] = useState<RefundDetails | null>(null);

  useEffect(() => {
    const fetchRefundDetails = async () => {
      if (!refundId) {
        setError("No refund ID provided");
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `${BACKEND_ROUTES.billingService}/api/refund/${refundId}`,
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to fetch refund details");
        }

        setRefundDetails(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchRefundDetails();
  }, [refundId]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Card>
          <CardContent className="flex items-center justify-center p-8">
            <Loader2 className="h-8 w-8 animate-spin" />
            <span className="ml-2">Loading refund details...</span>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <div className="mt-4">
          <Link href="/refund">
            <Button variant="outline">Return to Refund Page</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!refundDetails) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>No Details Found</AlertTitle>
          <AlertDescription>No refund details were found.</AlertDescription>
        </Alert>
        <div className="mt-4">
          <Link href="/refund">
            <Button variant="outline">Return to Refund Page</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-6 w-6 text-green-600" />
            Refund Processed Successfully
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <div className="flex justify-between">
              <span className="font-medium">Refund ID:</span>
              <span>{refundDetails.refund_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Amount:</span>
              <span>
                {refundDetails.amount / 100} {refundDetails.currency.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Status:</span>
              <span className="capitalize">{refundDetails.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Reason:</span>
              <span>{refundDetails.reason}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Date:</span>
              <span>
                {new Date(refundDetails.created * 1000).toLocaleDateString()}
              </span>
            </div>
          </div>

          <div className="flex gap-4 justify-center mt-6">
            <Link href="/events">
              <Button variant="outline">Return to Events</Button>
            </Link>
            <Link href="/refund">
              <Button variant="outline">Process Another Refund</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 