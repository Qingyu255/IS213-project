"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { fetchAuthSession } from "aws-amplify/auth";

const TICKET_SERVICE_URL =
  process.env.NEXT_PUBLIC_TICKET_SERVICE_URL || "http://localhost:8000";

export function AuthTest() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [testResult, setTestResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const testAuth = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get the token
      const session = await fetchAuthSession();
      const token = session.tokens?.idToken || session.tokens?.accessToken;

      if (!token) {
        throw new Error("No auth token available");
      }

      // Test the auth endpoint
      const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/test-auth`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Auth test failed: ${response.statusText}`);
      }

      const result = await response.json();
      setTestResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to test auth");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg">
      <h3 className="text-lg font-semibold">Auth Test</h3>
      <Button onClick={testAuth} disabled={loading}>
        {loading ? "Testing..." : "Test Authentication"}
      </Button>

      {error && <div className="text-red-500">Error: {error}</div>}

      {testResult && (
        <div className="mt-4 space-y-2">
          <p className="text-green-500">{testResult.message}</p>
          <div className="bg-gray-100 p-4 rounded">
            <p className="font-semibold">User ID: {testResult.user_id}</p>
            <pre className="mt-2 text-sm overflow-auto">
              {JSON.stringify(testResult.user_claims, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
