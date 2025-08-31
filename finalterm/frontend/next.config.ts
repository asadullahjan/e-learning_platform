import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: process.env.NEXT_PUBLIC_SERVER_URL?.split("://")[1].split(":")[0] || "localhost",
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*/",
        destination: `${process.env.NEXT_PUBLIC_SERVER_URL}/api/:path*/`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/api/:path*/",
        headers: [
          {
            key: "Access-Control-Allow-Credentials",
            value: "true",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
