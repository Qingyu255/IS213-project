"use client";

import { useEffect, useState } from "react";
import { Hub } from "@aws-amplify/core";
import {
  fetchAuthSession,
  getCurrentUser,
  fetchUserAttributes,
} from "aws-amplify/auth";
import { User } from "@/types/user";

// We'll use username-based identification instead of ID mapping
export default function useAuthUser(): { user: User | undefined; getUserId: () => string | undefined; getUsername: () => string | undefined } {
  // TODO: Expose loading state
  const [user, setUser] = useState<User | undefined>(undefined);
  const [tokenUserId, setTokenUserId] = useState<string | undefined>(undefined);
  const [username, setUsername] = useState<string | undefined>(undefined);

  async function updateUser() {
    try {
      const session = await fetchAuthSession();
      if (!session.tokens) {
        // No session => user is not logged in
        setUser({ isLoggedIn: false });
        return;
      }
      // Use ID token instead of access token for custom attributes
      const token = session.tokens?.idToken;
      console.log(`User authenticated with ID Token: ${token}`);
      
      if (token) {
        try {
          const payload = token.toString().split('.')[1];
          const decodedClaims = JSON.parse(atob(payload));
          console.log('ID Token claims:', decodedClaims);
          
          const extractedUserId = decodedClaims['custom:id'];
          const extractedUsername = decodedClaims.username || 
                                   decodedClaims['cognito:username'] ||
                                   decodedClaims.preferred_username;
          
          if (!extractedUserId) {
            console.error('No custom:id found in token claims');
          }
          
          setTokenUserId(extractedUserId);
          setUsername(extractedUsername);
        } catch (e) {
          console.error('Error decoding token:', e);
        }
      }
      
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
        setTokenUserId(undefined);
        setUsername(undefined);
      }
    });

    // Cleanup on unmount
    return () => {
      unsubscribe();
    };
  }, []);

  // Get the username (preferred method for identification)
  const getUsername = (): string | undefined => {
    if (!user || !user.isLoggedIn) return undefined;
    return username || user["username"] as string || 
           user["cognito:username"] as string || 
           user["preferred_username"] as string;
  };

  // Keep getUserId for backward compatibility
  const getUserId = (): string | undefined => {
    if (!user || !user.isLoggedIn) return undefined;
    return tokenUserId || user["custom:id"] as string;
  };

  return {
    user,
    getUserId,
    getUsername
  };
}
