"use client"
import { ModeToggle } from '@/components/mode-toggle'
import { Route } from '@/enums/routes';
import { fetchAuthSession } from 'aws-amplify/auth';
import { redirect, useRouter } from 'next/navigation';
import React, { useEffect } from 'react'

export default function BookingPage() {
    // Client-side route protection
    const router = useRouter();
    useEffect(() => {
      async function checkSession() {
        const session = await fetchAuthSession();
        const token = session.tokens?.accessToken;
        if (!token) {
          // Not logged in; redirect to login
          redirect(Route.Login);
        }
      }
      checkSession();
    }, [router]);
  return (
    <div>
        <ModeToggle/>
      yooo
    </div>
  )
}
