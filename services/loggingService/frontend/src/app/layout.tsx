import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "next-themes";
import { siteName } from "@/constants/common";
import Navbar from "@/components/navbar";
import ConfigureAmplifyClientSide from "./amplify-cognito-config";
import { Toaster } from "@/components/ui/sonner";
import Script from "next/script";
import InterestCheckWrapper from "@/components/InterestCheckWrapper";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: `${siteName}`,
  description: "Events simplified",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Script
          src={`https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&libraries=places`}
          strategy="beforeInteractive"
        />
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <main>
            <InterestCheckWrapper>
              <ConfigureAmplifyClientSide />
              <Navbar />
              {children}
            </InterestCheckWrapper>
          </main>
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
