import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { Sidebar } from "@/components/sidebar";

const font = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Social App",
  description: "A modern social media application",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${font.className} antialiased bg-gray-50`}>
        <AuthProvider>
          <Sidebar />
          <main className="ml-[72px] min-h-screen">
            <div className="max-w-2xl mx-auto">
              {children}
            </div>
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}