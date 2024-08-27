import type { Metadata } from "next";
import { Inter } from "next/font/google";
import localFont from "next/font/local";

import Header from "@/components/header";
import Providers from "@/providers/all";
import { ToastContainer } from "react-toastify";

import "./globals.css";
import "react-toastify/dist/ReactToastify.css";

const inter = Inter({ subsets: ["latin"] });

const klinicSlab = localFont({
  src: [
    {
      path: "./fonts/klinic/KlinicSlabMedium.otf",
      weight: "500",
      style: "normal",
    },
    {
      path: "./fonts/klinic/KlinicSlabBook.otf",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/klinic/KlinicSlabBold.otf",
      weight: "700",
      style: "normal",
    },
  ],
  display: "swap",
  variable: "--font-klinic-slab",
});

export const metadata: Metadata = {
  title: "ZeroK",
  description: "A ZKML framework based on the Virgo++/Libra protocol",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <Providers>
      <html lang="en">
        <body className={`${inter.className} ${klinicSlab.className}`}>
          <Header />
          {children}
          <ToastContainer theme="dark" />
        </body>
      </html>
    </Providers>
  );
}
