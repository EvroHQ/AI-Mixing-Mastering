import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "MixMaster - Mixing & Mastering in minutes - Studio Quality",
  description:
    "Professional AI-powered audio mixing and mastering. Upload your stems and get studio-quality masters in minutes.",
  keywords: [
    "audio mixing",
    "mastering",
    "AI music production",
    "stem mixing",
    "audio engineering",
  ],
  authors: [{ name: "MixMaster Studio" }],
  openGraph: {
    title: "MixMaster - Mixing & Mastering in minutes - Studio Quality",
    description: "Professional AI-powered audio mixing and mastering",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "MixMaster - Mixing & Mastering in minutes - Studio Quality",
    description: "Professional AI-powered audio mixing and mastering",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
