"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ErrorMessageCallout } from "@/components/error-message-callout";
import { interestCategories } from "@/constants/common";
import { toast } from "sonner";
import { Route } from "@/constants/routes";
import { BACKEND_ROUTES } from "@/constants/backend-routes";

export default function IndicateInterestsPage() {
  const router = useRouter();
  const { userId } = useParams() as { userId: string }; // dynamic route param
  const [existingInterests, setExistingInterests] = useState<string[]>([]);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  // Toggle interest selection
  function toggleInterest(interest: string) {
    if (existingInterests.includes(interest)) {
      setExistingInterests(existingInterests.filter((i) => i !== interest));
    } else {
      setExistingInterests([...existingInterests, interest]);
    }
  }

  //Save (Upsert) interests
  async function handleSaveInterests() {
    try {
      setError("");
      setLoading(true);

      const res = await fetch(`${BACKEND_ROUTES.userManagementServiceUrl}/api/userinterests/user/${userId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // We send the final list of interests as a simple array of strings
        body: JSON.stringify(existingInterests),
      });
      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg);
      }

      toast("Interests updated successfully");
      // Optional: navigate to another page
      router.push(Route.BrowseEvents);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message || "Error updating interests");
    } finally {
      setLoading(false);
    }
  }

  // 4) Render
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-2">
        Indicate Interests for User: {userId}
      </h1>

      {error && <ErrorMessageCallout errorMessage={error} />}

      {loading && <p>Loading...</p>}

      {!loading && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 my-4">
            {interestCategories.map((interest) => (
              <label key={interest} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={existingInterests.includes(interest)}
                  onChange={() => toggleInterest(interest)}
                />
                <span>{interest}</span>
              </label>
            ))}
          </div>

          <Button onClick={handleSaveInterests} disabled={loading}>
            {loading ? "Saving..." : "Save Interests"}
          </Button>
        </>
      )}
    </div>
  );
}
