"use server";
import { authConfig } from "@/app/amplify-cognito-config";
import { User } from "@/types/user";
import { NextServer, createServerRunner } from "@aws-amplify/adapter-nextjs";
import { fetchAuthSession, getCurrentUser } from "aws-amplify/auth/server";

export const { runWithAmplifyServerContext } = createServerRunner({
  config: {
    Auth: authConfig,
  },
});

export async function authenticatedUser(context: NextServer.Context) {
  return await runWithAmplifyServerContext({
    nextServerContext: context,
    operation: async (contextSpec): Promise<User> => {
      try {
        let user: User = {
          isLoggedIn: true,
        };

        const session = await fetchAuthSession(contextSpec);

        if (!session.tokens) {
          user.isLoggedIn = false;
          return user;
        }
        user = {
          ...user,
          ...(await getCurrentUser(contextSpec)),
        };
        user.isLoggedIn = true;
        console.log("user: ", user)
        console.log(`User is authenticated. Bearer Token:\n ${session.tokens.accessToken}`)
        return user;
      } catch (error) {
        console.error(error);
        throw error;
      }
    },
  });
}
