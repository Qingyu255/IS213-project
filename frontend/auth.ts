import NextAuth from "next-auth";
import { JWT } from "next-auth/jwt";
import Cognito from "next-auth/providers/cognito";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [Cognito],
  callbacks: {
    /**
     * 1. On initial sign in, store the tokens from Cognito in our JWT.
     * 2. If the access token is still valid, return it.
     * 3. Otherwise, refresh it using the refresh token.
     */
    async jwt({ token, account }) {
      // 1) Initial sign in
      if (account) {
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token;
        token.accessTokenExpires = (account.expires_at ?? 0) * 1000;
        console.debug("Access token issued on initial sign in: " + token.accessToken);

        // Store user role
        if (account.id_token) {
          const decodedIdToken = JSON.parse(atob(account.id_token.split('.')[1]));
          token.userRole = decodedIdToken["cognito:groups"][0] || ""; // Assuming a user can only have ONE ROLE
        }
        
        return token;
      }

      // 2) If access token hasn't expired, just return the current token
      if (token.accessTokenExpires && Date.now() < token.accessTokenExpires) {
        console.debug(
          "Access token valid, expiring in " +
            (token.accessTokenExpires - Date.now()) / 1000 +
            " seconds"
        );
        return token;
      }

      // 3) If the access token is expired, attempt to refresh it
      console.debug("Access token expired, refreshing accessToken");
      return await refreshAccessToken(token);
    },

    /**
     * Expose the access token in the session so it's available in the client.
     */
    async session({ session, token }) {
      session.userRole = token.userRole;
      session.accessToken = token.accessToken;
      session.error = token.error; // in case we need to surface refresh errors
      return session;
    },
  },
});

/**
 * Attempt to refresh the Cognito access token using the refresh token.
 */
async function refreshAccessToken(token: JWT): Promise<JWT> {
  try {
    const cognitoAuthority = process.env.COGNITO_DOMAIN_URL || "";
    const response = await fetch(`${cognitoAuthority}/oauth2/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Authorization: `Basic ${btoa(
          `${process.env.AUTH_COGNITO_ID}:${process.env.AUTH_COGNITO_SECRET}`
        )}`,
      },
      body: new URLSearchParams({
        grant_type: "refresh_token",
        client_id: process.env.COGNITO_APP_CLIENT_ID || "",
        refresh_token: token.refreshToken || "",
      }),
    });

    console.debug("Refreshing Cognito refresh token: ");
    const refreshedTokens = await response.json();

    if (!response.ok) {
      throw refreshedTokens;
    }

    // Cognito will return a new access token and possibly a new refresh token
    return {
      ...token,
      accessToken: refreshedTokens.access_token,
      accessTokenExpires: Date.now() + refreshedTokens.expires_in * 1000,
      refreshToken: refreshedTokens.refresh_token ?? token.refreshToken, // fall back to old refresh token
      error: undefined,
    };
  } catch (error) {
    console.error("Error refreshing access token", error);
    return {
      ...token,
      error: "RefreshAccessTokenError",
    };
  }
}
