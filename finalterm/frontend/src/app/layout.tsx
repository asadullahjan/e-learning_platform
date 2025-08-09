import type { Metadata } from "next";
import { Nunito } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import Header from "@/components/header";

const nunito = Nunito({
  variable: "--font-nunito",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "eLearning Platform",
  description: "Advanced eLearning application built with Django and Next.js",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1.0"
        />
      </head>
      <body className={`${nunito.variable} font-sans antialiased`}>
        <div className="flex flex-col min-h-screen">
          <Header />
          <div className="flex-grow container mx-auto py-6 px-4">{children}</div>
        </div>
        <Toaster />
      </body>
    </html>
  );
}
