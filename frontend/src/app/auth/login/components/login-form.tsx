"use client";
import { AtSign, Key } from "lucide-react";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useFormStatus } from "react-dom";
import { handleSignIn } from "@/lib/cognitoActions";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorMessageCallout } from "@/components/error-message-callout";
import { useActionState } from "react";
import { Card, CardContent, CardTitle } from "@/components/ui/card";

export default function LoginForm() {
  const [errorMessage, dispatch] = useActionState(handleSignIn, undefined);
  return (
    <form action={dispatch} className="space-y-3">
      <Card className="flex-1 rounded-lgpx-6 pb-4 pt-8">
        <CardContent>
          <CardTitle className={`mb-3 text-2xl`}>Please log in to continue.</CardTitle>
          <div className="w-full">
            <div>
              <Label
                className="mb-3 mt-5 block text-xs font-medium"
                htmlFor="email"
              >
                Email
              </Label>
              <div className="relative">
                <input
                  className="peer block w-full rounded-md border border-gray-200 py-[9px] pl-10 text-sm outline-2"
                  id="email"
                  type="email"
                  name="email"
                  placeholder="Enter your email address"
                  required
                />
                <AtSign className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500 peer-focus:text-gray-900" />
              </div>
            </div>
            <div className="mt-4">
              <Label
                className="mb-3 mt-5 block text-xs font-medium"
                htmlFor="password"
              >
                Password
              </Label>
              <div className="relative">
                <Input
                  className="peer block w-full rounded-md border border-gray-200 py-[9px] pl-10 text-sm outline-2 placeholder:text-gray-500"
                  id="password"
                  type="password"
                  name="password"
                  placeholder="Enter password"
                  required
                />
                <Key className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500 peer-focus:text-gray-900" />
              </div>
            </div>
          </div>
          <LoginButton />
          {errorMessage && (
            <ErrorMessageCallout errorMessage={errorMessage} />
          )}
          <div className="flex justify-center">
            <Link
              href="/auth/signup"
              className="mt-2 cursor-pointer text-blue-500"
            >
              {"Don't have an account? "} Sign up.
            </Link>
          </div>
        </CardContent>
      </Card>
    </form>
  );
}

function LoginButton() {
  const { pending } = useFormStatus();

  return (
    <Button className="my-4 w-full" aria-disabled={pending}>
      Log in <ArrowRight className="ml-auto h-5 w-5 text-gray-50" />
    </Button>
  );
}
