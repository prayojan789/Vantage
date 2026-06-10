import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "VANTAGE — Nepal Media Intelligence",
  description: "AI-powered news bias analysis for Nepali political media",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-base-900 font-body text-base-200 antialiased">
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 ml-64 min-h-screen">
            {children}
          </main>
        </div>
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "#21262D",
              color: "#E6EDF3",
              border: "1px solid #30363D",
              borderRadius: "8px",
              fontSize: "14px",
            },
          }}
        />
      </body>
    </html>
  );
}
