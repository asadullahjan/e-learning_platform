import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: process.env.NEXT_PUBLIC_URL?.split("://")[1].split(":")[0] || "localhost",
      },
    ],
  },
};

export default nextConfig;
