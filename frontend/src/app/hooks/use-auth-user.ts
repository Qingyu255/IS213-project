"use client";

import { useEffect, useState } from "react";
import { Hub } from "@aws-amplify/core";
import {
  fetchAuthSession,
  getCurrentUser,
  fetchUserAttributes,
} from "aws-amplify/auth";
import { User } from "@/types/user";

export default function useAuthUser(): User | undefined {
  const [user, setUser] = useState<User | undefined>(undefined);

  async function updateUser() {
    try {
      const session = await fetchAuthSession();
      if (!session.tokens) {
        // No session => user is not logged in
        setUser({ isLoggedIn: false });
        return;
      }
    const token = session.tokens?.accessToken;
    console.log(`User authenticated Token: ${token}`)
      // Session is valid => fetch user details
      const currentUser = await getCurrentUser();
      const attributes = await fetchUserAttributes();
      setUser({ ...currentUser, ...attributes, isLoggedIn: true });
    } catch (error) {
      console.error("Error fetching user:", error);
      setUser({ isLoggedIn: false });
    }
  }

  useEffect(() => {
    // On mount, get the initial user
    updateUser();

    // Listen for Auth events like signIn / signOut / tokenRefresh
    const unsubscribe = Hub.listen("auth", ({ payload: { event } }) => {
      if (event === "signedIn" || event === "tokenRefresh") {
        updateUser();
      } else if (event === "signedOut") {
        setUser({ isLoggedIn: false });
      }
    });

    // Cleanup on unmount
    return () => {
      unsubscribe();
    };
  }, []);

  return user;
}
