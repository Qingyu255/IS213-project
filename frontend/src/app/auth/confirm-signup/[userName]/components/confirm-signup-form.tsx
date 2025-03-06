"use client";
import { useState } from "react";
import { Key, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { confirmSignUp } from "aws-amplify/auth";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { ErrorMessageCallout } from "@/components/error-message-callout";
import { toast } from "sonner";
import { Route } from "@/constants/routes";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardTitle } from "@/components/ui/card";

export default function ConfirmSignUpForm({ userName } : { userName: string; }) {
  const router = useRouter();
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const code = formData.get("code") as string;

    try {
      await confirmSignUp({ username: userName, confirmationCode: code });

      toast("User Confirmed Successfully", {
        description: `User ${userName} confirmed successfully!`,
      });
      router.push(`${Route.Login}`);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message ||  "An error occurred while confirming sign up.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <Card className="flex-1 rounded-lgpx-6 pb-4 pt-8">
        <CardContent>
          <CardTitle className="mb-3 text-2xl">Please verify your account.</CardTitle>
          <div className="w-full">
            <div className="mt-4">
              <div className="mt-4">
                <Label
                  className="mb-1 block text-xs font-medium"
                  htmlFor="code"
                >
                  Confirmation Code
                </Label>
                <p className="mb-3 text-xs text-gray-500">
                  A code has been sent to your email. Please check your inbox (and spam folder) and enter it below.
                </p>
              </div>
              <div className="relative mb-3">
                <Input
                  className="peer block w-full rounded-md border border-gray-200 py-[9px] pl-10 text-sm outline-2"
                  id="code"
                  type="text"
                  name="code"
                  placeholder="Enter code"
                  required
                  minLength={6}
                />
                <Key className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500 peer-focus:text-gray-900" />
              </div>
            </div>
          </div>
          {error && (
              <ErrorMessageCallout errorMessage={error} />
          )}
          <ConfirmButton loading={loading} />
        </CardContent>    
      </Card>
    </form>
  );
}

function ConfirmButton({ loading }: { loading: boolean }) {
  return (
    <Button className="mt-4 w-full" disabled={loading}>
      Confirm <ArrowRight className="ml-auto h-5 w-5 text-gray-50" />
    </Button>
  );
}
