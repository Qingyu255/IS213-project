"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { ErrorMessageCallout } from "@/components/error-message-callout";
import { InterestCategoryArr, InterestCategoryIcons } from "@/constants/common";
import { toast } from "sonner";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { getBearerToken } from "@/utils/auth";
import { Spinner } from "@/components/ui/spinner";
import { getErrorMessage } from "@/lib/cognitoActions";
import { LocalStorageKeys } from "@/enums/LocalStorageKeys";

export default function IndicateInterestsPage() {
  const { userId } = useParams() as { userId: string }; // dynamic route param
  const [existingInterests, setExistingInterests] = useState<string[]>([]);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  // Fetch existing interests for the user
  useEffect(() => {
    async function fetchUserInterests() {
      if (!userId) return;
      try {
        const res = await fetch(`${BACKEND_ROUTES.userManagementServiceUrl}/api/userinterests/user/${userId}`, {
          method: "GET",
          headers: {
              Authorization: await getBearerToken(),
          }
        });
        if (!res.ok) {
          toast.error("Failed to load interests");
          setError(getErrorMessage(res));
          return;
        }
        const interests: string[] = await res.json();
        setExistingInterests(interests);
      } catch (error) {
        setError(error + "");
        toast.error(`Error fetching interests: ${error}`);
      } finally {
        setLoading(false);
      }
    }
    fetchUserInterests();
  }, [userId]);

  // Toggle interest selection
  const toggleInterest = (interest: string) => {
    if (existingInterests.includes(interest)) {
      setExistingInterests(existingInterests.filter((i) => i !== interest));
    } else {
      setExistingInterests([...existingInterests, interest]);
    }
  }

  //Save (Upsert) interests
  const handleSaveInterests = async () => {
    try {
      setError("");
      setLoading(true);

      const res = await fetch(`${BACKEND_ROUTES.userManagementServiceUrl}/api/userinterests/user/${userId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: await getBearerToken(),
        },
        // We send the final list of interests as a simple array of strings
        body: JSON.stringify(existingInterests),
      });
      if (!res.ok) {
        setError(getErrorMessage(res));
      }

      toast("Interests updated successfully");

      if (!localStorage.getItem(LocalStorageKeys.UserHasOnceSetInterests)) {
        localStorage.setItem(LocalStorageKeys.UserHasOnceSetInterests, "true");
      }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message || "Error updating interests");
    } finally {
      setLoading(false);
    }
  }

  if (error) {
    return (
      <div className="p-4">
        <ErrorMessageCallout errorMessage={error} />
      </div>
    )
  }

  // 4) Render
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-xl font-bold mb-4">Select Your Interests</h1>

      {loading && (
        <Spinner size="sm" className="bg-black dark:bg-white" />
      )}

      {!loading && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 my-4">
            {InterestCategoryArr.map((interest) => {
              // Get the corresponding icon component
              const Icon = InterestCategoryIcons[interest];
              const isSelected = existingInterests.includes(interest);
              return (
                <div
                  key={interest}
                  onClick={() => toggleInterest(interest)}
                  className={`flex flex-col items-center justify-center p-4 border border-2 rounded-lg cursor-pointer transition-colors ${
                    isSelected ? "bg-gray-300 dark:bg-gray-500/50": "bg-transparent"
                  }`}
                >
                  <Icon className="w-8 h-8 mb-2" />
                  <span className="text-center">{interest}</span>
                </div>
              );
            })}
          </div>

          <Button onClick={handleSaveInterests} disabled={loading}>
            {loading ? "Saving..." : "Save Interests"}
          </Button>
        </>
      )}
    </div>
  );
}
