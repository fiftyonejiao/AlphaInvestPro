import type { Metadata } from "next";
import { ReactNode } from "react";

import DisclaimerBanner from "@/components/DisclaimerBanner";
import I18nProvider from "@/components/I18nProvider";
import NavBar from "@/components/NavBar";

import "./globals.css";

export const metadata: Metadata = {
  title: "AlphaInvestPro",
  description: "Research-only AI investment analysis workbench. Not financial advice.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <I18nProvider>
          <NavBar />
          <main className="max-w-6xl mx-auto px-4 py-6">
            {children}
            <DisclaimerBanner />
          </main>
        </I18nProvider>
      </body>
    </html>
  );
}
