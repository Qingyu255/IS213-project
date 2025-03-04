"use client"
import { getSession } from "next-auth/react"

export const getBearerToken = async (): Promise<string> => {
    const session = await getSession();
    let token = "Bearer ";
    if (session && session.accessToken) {
        token += session.accessToken;
    } else {
        console.error("Error in retrieving accessToken.")
    }
    return token;
}
