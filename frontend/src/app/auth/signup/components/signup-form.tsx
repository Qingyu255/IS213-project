"use client";
import { AtSign, Key, ArrowRight, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { BackendRoutes } from "@/constants/backend-routes";
import { Spinner } from "@/components/ui/spinner";
import { getErrorString } from "@/utils/common";
import { ErrorMessageCallout } from "@/components/error-message-callout";
import { toast } from "sonner";
import { Route } from "@/constants/routes";
import { useRouter } from "next/navigation";
import { interestCategories } from "@/constants/common";

export default function SignUpForm() {
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [step, setStep] = useState<number>(1);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const router = useRouter();

  async function handleSignUp(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const username = formData.get("username") as string;
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    const confirmPassword = formData.get("confirmPassword") as string;

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      setLoading(false);
      return;
    }

    // Validate password
    const passwordErrors = validatePassword(password);
    if (passwordErrors.length > 0) {
      setError(passwordErrors.join(" "));
      setLoading(false);
      return;
    }

    // Adjust the fields to match your CreateUserDto in C#
    const bodyData = {
      username: username,
      email,
      password, // TODO: allow pass in user defined password
    };

    try {
      // Replace with your actual API endpoint if different
      const res = await fetch(`${BackendRoutes.userManagementServiceUrl}/api/users/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(bodyData),
      });

      if (!(res.ok && res.status === 201)) {
        const errorString = await getErrorString(res);
          console.error("An error occurred while fetching user details:", errorString);
          setError(errorString);
          return;
      }

      toast("User Created Successfully", {
        description: `${formData.get("username") as string} created successfully!`,
      });
      router.push(`${Route.ConfirmSignUp}/${username}`);

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (err) {
      setError("An unknown error occurred.");
    } finally {
      setLoading(false);
    }
  }

  const toggleInterest = (interest: string) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter((i) => i !== interest));
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  async function handleInterestsSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    toast.success("Interests saved successfully!");
    router.push(Route.BrowseEvents); // Replace with your target URL
  }

  if (step === 2) {
    return (
      <form onSubmit={handleInterestsSubmit} className="space-y-3">
        <div className="flex-1 rounded-lg bg-gray-50 px-6 pb-4 pt-8">
          <h1 className="mb-3 text-2xl">Select Your Interests</h1>
          <p className="mb-4">Choose from the options below:</p>
          <div className="grid grid-cols-2 gap-3">
            {interestCategories.map((interest) => (
              <label key={interest} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  value={interest}
                  checked={selectedInterests.includes(interest)}
                  onChange={() => toggleInterest(interest)}
                  className="h-4 w-4"
                />
                <span>{interest}</span>
              </label>
            ))}
          </div>
          {error && <ErrorMessageCallout errorMessage={error} />}
          <Button type="submit" className="mt-4 w-full">
            Continue <ArrowRight className="ml-auto h-5 w-5" />
          </Button>
        </div>
      </form>
    );
  }

  return (
    <form onSubmit={handleSignUp} className="space-y-3">
      <div className="flex-1 rounded-lg bg-gray-50 px-6 pb-4 pt-8">
        <h1 className={`mb-3 text-2xl`}>Please create an account.</h1>
        <div className="w-full">
          <div>
            <Label
              className="mb-3 mt-5 block text-xs font-medium text-gray-900"
              htmlFor="username"
            >
              username
            </Label>
            <div className="relative">
              <Input
                className="peer block w-full rounded-md border border-gray-200 py-[9px] pl-10 text-sm outline-2 placeholder:text-gray-500"
                id="username"
                type="text"
                name="username"
                minLength={4}
                placeholder="Enter your username"
                required
              />
              <User className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500 peer-focus:text-gray-900" />
            </div>
          </div>
          <div className="mt-4">
            <Label
              className="mb-3 mt-5 block text-xs font-medium text-gray-900"
              htmlFor="email"
            >
              Email
            </Label>
            <div className="relative">
              <Input
                className="peer block w-full rounded-md border border-gray-200 py-[9px] pl-10 text-sm outline-2 placeholder:text-gray-500"
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
              className="mb-3 mt-5 block text-xs font-medium text-gray-900"
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
        <div className="mt-4">
            <Label
              className="mb-3 mt-5 block text-xs font-medium text-gray-900"
              htmlFor="confirmPassword"
            >
              Confirm Password
            </Label>
            <div className="relative">
              <Input
                className="peer block w-full rounded-md border border-gray-200 py-[9px] pl-10 text-sm outline-2 placeholder:text-gray-500"
                id="confirmPassword"
                type="password"
                name="confirmPassword"
                placeholder="Confirm your password"
                required
              />
              <Key className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500 peer-focus:text-gray-900" />
            </div>
          </div>
        </div>
        {error && (
          <ErrorMessageCallout errorMessage={error} />
        )}
        <Button className="mt-4 w-full">
          Create account <ArrowRight className="ml-auto h-5 w-5 text-gray-50" />
          {loading && (
            <Spinner size="sm" className="bg-black dark:bg-white" />
          )}
        </Button>
        <div className="flex justify-center">
          <Link
            href="/auth/login"
            className="mt-2 cursor-pointer text-primary"
          >
            Already have an account? Log in.
          </Link>
        </div>
    </form>
  );
}

const validatePassword = (password: string): string[] => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push("Password must be at least 8 characters long.");
  }
  if (!/[a-z]/.test(password)) {
    errors.push("Password must contain at least one lowercase letter.");
  }
  if (!/[A-Z]/.test(password)) {
    errors.push("Password must contain at least one uppercase letter.");
  }
  if (!/[0-9]/.test(password)) {
    errors.push("Password must contain at least one number.");
  }
  if (!/[^A-Za-z0-9]/.test(password)) {
    errors.push("Password must contain at least one symbol.");
  }
  return errors;
}
