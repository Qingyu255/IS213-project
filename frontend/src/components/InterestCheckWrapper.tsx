"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import InterestPromptModal from "./interest-prompt-modal";
import { toast } from "sonner";
import useAuthUser from "@/hooks/use-auth-user";
import { getBearerToken } from "@/utils/auth";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { LocalStorageKeys } from "@/enums/LocalStorageKeys";

export default function InterestCheckWrapper({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { getUserId } = useAuthUser();
  const userId = getUserId();
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    async function fetchUserInterests() {
      if (!userId || localStorage.getItem(LocalStorageKeys.DontAskInterests) === "true" || localStorage.getItem(LocalStorageKeys.UserHasOnceSetInterests) === "true" ) {
        return;
      };

      try {
        const res = await fetch(`${BACKEND_ROUTES.userManagementServiceUrl}/userinterests/user/${userId}`, {
            method: "GET",
            headers: {
                Authorization: await getBearerToken(),
            }
        });
        if (!res.ok) {
          toast.error("Failed to load interests.");
          return;
        }
        const data = await res.json();
        const interests = data as string[]; // cast
        if (interests.length === 0) {
          setShowModal(true);
        }
      } catch (error) {
        console.error("Error fetching interests:", error);
        toast.error("Error fetching interests.");
      }
    }
    fetchUserInterests();
  }, [userId]);

  const handleYes = () => {
    setShowModal(false);
    router.push(`/indicate-interests/${userId}`);
  };

  const handleDontAsk = () => {
    localStorage.setItem(LocalStorageKeys.DontAskInterests, "true");
    setShowModal(false);
  };

  return (
    <>
      {children}
      {showModal && <InterestPromptModal onYes={handleYes} onDontAsk={handleDontAsk} />}
    </>
  );
}
