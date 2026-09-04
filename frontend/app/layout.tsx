import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import Navbar from "@/components/Navbar";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: {
    default: "Honey Chain",
    template: "%s | Honey Chain",
  },
  description:
    "Honey Chain is a blockchain-based honey traceability system that lets consumers verify the complete supply-chain journey of their honey — from hive to shelf.",
  keywords: ["honey", "blockchain", "traceability", "supply chain", "beekeeping", "food safety"],
  openGraph: {
    title: "Honey Chain",
    description: "Blockchain-powered honey traceability — verify authenticity from hive to shelf.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-stone-950 text-stone-100 min-h-screen`}
      >
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
