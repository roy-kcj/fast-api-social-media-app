import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",  // Allow all domains (for development)
      },
    ],
  },
};

export default nextConfig;
