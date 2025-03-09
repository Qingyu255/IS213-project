import type { NextConfig } from "next";

/** @type {NextConfig} */
const nextConfig: NextConfig = {
  output: "standalone", // Standalone deployment for Docker
  compiler: {
    removeConsole: process.env.NODE_ENV === "production", // Removes console logs in production
  },
};

export default nextConfig;