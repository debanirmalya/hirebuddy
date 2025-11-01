import type { ReactNode } from "react";
import Link from "next/link";
import "./globals.css";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="flex flex-col min-h-screen bg-gray-50 text-gray-800 antialiased">
        {/* HEADER */}
        <header className="flex items-center justify-between px-8 py-4 bg-white border-b border-gray-200 shadow-sm sticky top-0 z-20">
          <Link
            href="/"
            className="text-2xl font-semibold text-primary-600 hover:text-primary-700 transition-colors"
          >
            HireBuddy
          </Link>

          <nav className="flex items-center gap-6">
            <Link
              href="/dashboard"
              className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/upload"
              className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
            >
              Add Candidate
            </Link>

          </nav>
        </header>

        {/* MAIN */}
        <main className="flex-1 px-6 py-10 overflow-y-auto">
          <div className="w-full">{children}</div>
        </main>

        {/* FOOTER */}
        <footer className="w-full bg-white border-t border-gray-200 text-center py-3 text-sm text-gray-500">
          © {new Date().getFullYear()} HireBuddy. All rights reserved.
        </footer>
      </body>
    </html>
  );
}
