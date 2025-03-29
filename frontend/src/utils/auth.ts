"use client";
import { fetchAuthSession } from "aws-amplify/auth";

export const getBearerToken = async (): Promise<string> => {
  const session = await fetchAuthSession();
  let token = "";
  if (session && session.tokens && session.tokens.accessToken) {
    token = `Bearer ${session.tokens.accessToken}`;
    console.log("Token:  " + token);
  } else {
    console.error("Error in retrieving access token.");
  }
  return token;
};

export const getBearerIdToken = async (): Promise<string> => {
  const session = await fetchAuthSession();
  let token = "";
  if (session && session.tokens && session.tokens.idToken) {
    token = `Bearer ${session.tokens.idToken}`;
    console.log("Token:  " + token);
  } else {
    console.error("Error in retrieving id token.");
  }
  return token;
};
