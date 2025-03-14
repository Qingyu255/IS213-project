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
      
      // Debug: Log token claims if available
      if (token) {
        try {
          // Extract and log the payload part of the JWT
          const payload = token.toString().split('.')[1];
          const decodedClaims = JSON.parse(atob(payload));
          console.log('ID Token claims:', decodedClaims);
          
          // Extract user ID from token claims - only use custom:id
          const extractedUserId = decodedClaims['custom:id'];
          console.log('Extracted custom:id from ID token:', extractedUserId);
          
          if (!extractedUserId) {
            console.warn('No custom:id found in ID token claims. Available claims:', Object.keys(decodedClaims));
          }
                                 
          // Extract username from token claims
          const extractedUsername = decodedClaims.username || 
                                   decodedClaims['cognito:username'] ||
                                   decodedClaims.preferred_username;
                                 
          console.log('Username from ID token:', extractedUsername);
          
          // Store the user ID and username from token
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
    
    // First try to get the username from the token
    if (username) {
      console.log("Using username from token:", username);
      return username;
    }
    
    // Fallback to user attributes
    const usernameFromAttrs = user["username"] as string || 
                             user["cognito:username"] as string || 
                             user["preferred_username"] as string;
    
    if (usernameFromAttrs) {
      console.log("Using username from attributes:", usernameFromAttrs);
      return usernameFromAttrs;
    }
    
    console.warn("Could not find username");
    return undefined;
  };

  // Keep getUserId for backward compatibility
  const getUserId = (): string | undefined => {
    if (!user || !user.isLoggedIn) return undefined;
    
    // First try to get custom:id from token
    if (tokenUserId) {
      console.log("Using custom:id from token:", tokenUserId);
      return tokenUserId;
    }
    
    // Then try to get custom:id from user attributes
    const customId = user["custom:id"] as string;
    if (customId) {
      console.log("Using custom:id from attributes:", customId);
      return customId;
    }
    
    // If no custom:id is found, log a warning and return undefined
    console.warn("No custom:id found in token or attributes");
    return undefined;
  };

  return {
    user,
    getUserId,
    getUsername
  };
}
