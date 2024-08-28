import type { Metadata } from "next";
import localFont from "next/font/local";

import Header from "@/components/header";
import Providers from "@/providers/all";
import { ToastContainer } from "react-toastify";

import "./globals.css";
import "react-toastify/dist/ReactToastify.css";
import Footer from "@/components/footer";

const fonts = localFont({
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
    {
      path: "./fonts/vulf/VulfSansDemo-Regular.otf",
      weight: "100",
      style: "normal",
    },
  ],
  display: "swap",
  variable: "--font-klinic",
});

export const metadata: Metadata = {
  title: "ZeroK",
  description:
    "A distributed zkML framework for secure and verifiable machine learning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <Providers>
      <html lang="en">
        <body className={`${fonts.className}`}>
          <Header />
          {children}
          <ToastContainer theme="dark" />
          <Footer />
        </body>
      </html>
    </Providers>
  );
}
