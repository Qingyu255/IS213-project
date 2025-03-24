import type { NextConfig } from "next";

/** @type {NextConfig} */
const nextConfig: NextConfig = {
  output: "standalone", // Standalone deployment for Docker
  compiler: {
    removeConsole: process.env.NODE_ENV === "production", // Removes console logs in production
  },
  // Temporarily disable ESLint during build
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;