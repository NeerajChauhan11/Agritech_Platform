import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";

export const metadata: Metadata = {
  title: "AgriSmart — Precision Agriculture Platform",
  description:
    "AI-powered precision agriculture platform with real-time IoT telemetry, crop disease detection, irrigation intelligence, and yield prediction.",
  keywords: ["precision agriculture", "IoT", "AI", "crop disease", "irrigation", "yield prediction"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <div className="app-shell">
          <Sidebar />
          <div className="main-content">
            <TopBar />
            <main className="page-content">{children}</main>
          </div>
        </div>
        <style>{`
          .app-shell {
            display: flex;
            min-height: 100vh;
            background: var(--bg-base);
          }
          .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
            overflow: hidden;
          }
          .page-content {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
          }
          @media (max-width: 768px) {
            .page-content { padding: 16px; }
          }
        `}</style>
      </body>
    </html>
  );
}
