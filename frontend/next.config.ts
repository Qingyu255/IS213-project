import type { NextConfig } from "next";

/** @type {NextConfig} */
const nextConfig: NextConfig = {
  output: "standalone", // Standalone deployment for Docker
  compiler: {
    removeConsole: process.env.NODE_ENV === "production", // Removes console logs in production
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    domains: ['is213-project-dev-public-bucket.s3.amazonaws.com'],
  },
};

export default nextConfig;