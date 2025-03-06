import { useEffect, useState } from "react";
import {
  fetchAuthSession,
  fetchUserAttributes,
  getCurrentUser,
} from "aws-amplify/auth";
import { User } from "@/types/user";

export default function useAuthUser(): User | undefined {
  const [user, setUser] = useState<User | undefined>(undefined);

  useEffect(() => {
    async function getUser() {
      const session = await fetchAuthSession();
      if (!session.tokens) {
        console.log("Unauthenticated user");
        return;
      }
      console.log(`User is authenticated. Token: Bearer ${session.tokens.accessToken}`);
      const currentUser = await getCurrentUser();
      const attributes = await fetchUserAttributes();
      setUser({ ...currentUser, ...attributes, isLoggedIn: true });
    }
    getUser();
  }, []);

  return user;
}
