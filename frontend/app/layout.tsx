import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trading Terminal",
  description: "Automated trading terminal for BingX",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
