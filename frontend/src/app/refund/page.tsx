"use client";

import React, { useState } from "react";
import { useSearchParams } from "next/navigation";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

interface RefundFormData {
  payment_intent_id: string;
  amount?: number;
  reason: string;
}

interface RefundResponse {
  success: boolean;
  refund_id: string;
  amount: number;
  currency: string;
  status: string;
}

export default function RefundPage() {
  const searchParams = useSearchParams();
  const [formData, setFormData] = useState<RefundFormData>({
    payment_intent_id: searchParams.get("payment_intent_id") || "",
    reason: "requested_by_customer",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<RefundResponse | null>(null);
  const [verificationStatus, setVerificationStatus] = useState<string | null>(null);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "amount" ? Number(value) : value,
    }));
  };

  const verifyRefund = async (refundId: string) => {
    try {
      const response = await fetch(
        `${BACKEND_ROUTES.billingService}/api/refund/verify`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refund_id: refundId }),
        }
      );

      const data = await response.json();
      if (data.verified) {
        setVerificationStatus("verified");
      } else {
        setVerificationStatus("failed");
      }
    } catch (err) {
      setVerificationStatus("error");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    setVerificationStatus(null);

    try {
      const response = await fetch(
        `${BACKEND_ROUTES.billingService}/api/refund/process`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            payment_intent_id: formData.payment_intent_id,
            amount: formData.amount,
            reason: formData.reason,
            metadata: {
              refund_reason: formData.reason,
            },
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to process refund");
      }

      setSuccess(data);
      if (data.refund_id) {
        await verifyRefund(data.refund_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Request a Refund</CardTitle>
          <CardDescription>
            Please provide the payment details for your refund request.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Payment Intent ID
              </label>
              <Input
                type="text"
                name="payment_intent_id"
                value={formData.payment_intent_id}
                onChange={handleInputChange}
                placeholder="pi_..."
                required
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Refund Amount (in cents)
              </label>
              <Input
                type="number"
                name="amount"
                value={formData.amount || ""}
                onChange={handleInputChange}
                placeholder="Leave empty for full refund"
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Refund Reason
              </label>
              <Textarea
                name="reason"
                value={formData.reason}
                onChange={handleInputChange}
                placeholder="Please provide a reason for the refund"
                required
                className="w-full"
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert className="bg-green-50">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <AlertTitle className="text-green-800">
                  Refund Processed Successfully
                </AlertTitle>
                <AlertDescription className="text-green-700">
                  Refund ID: {success.refund_id}
                  <br />
                  Amount: {success.amount / 100} {success.currency.toUpperCase()}
                  <br />
                  Status: {success.status}
                  {verificationStatus && (
                    <div className="mt-2">
                      Verification Status:{" "}
                      <span
                        className={
                          verificationStatus === "verified"
                            ? "text-green-600"
                            : "text-red-600"
                        }
                      >
                        {verificationStatus}
                      </span>
                    </div>
                  )}
                </AlertDescription>
              </Alert>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing Refund...
                </>
              ) : (
                "Submit Refund Request"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
