"use client";
import { useEffect } from "react";
import Link from "next/link";

export default function HomePage() {
  useEffect(() => {
    document.title = "HireBuddy - AI-Powered Candidate Verification";
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-primary-600 to-blue-800 bg-clip-text text-transparent mb-4">
          Welcome to HireBuddy
        </h1>
        <p className="text-gray-600 text-lg sm:text-xl">
          Your AI-powered candidate verification system
        </p>
      </div>

      {/* Action Cards */}
      <div className="grid md:grid-cols-2 gap-8 mb-16">
        {/* Upload Resume */}
        <Link
          href="/upload"
          className="block bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition transform hover:-translate-y-1 p-6"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-blue-400 flex items-center justify-center text-2xl text-white">
              📄
            </div>
            <h2 className="text-xl font-semibold text-gray-800">Upload Resume</h2>
          </div>
          <p className="text-gray-600 leading-relaxed">
            Upload a candidate’s resume to begin the AI-powered extraction and
            verification process.
          </p>
        </Link>

        {/* Dashboard */}
        <Link
          href="/dashboard"
          className="block bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition transform hover:-translate-y-1 p-6"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-400 flex items-center justify-center text-2xl text-white">
              📊
            </div>
            <h2 className="text-xl font-semibold text-gray-800">Dashboard</h2>
          </div>
          <p className="text-gray-600 leading-relaxed">
            View all candidates, track extraction status, and manage verification
            workflows.
          </p>
        </Link>
      </div>

      {/* How it Works */}
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-6">
          How it works
        </h3>
        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            {
              step: "1️⃣",
              title: "Upload Resume",
              desc: "Drag and drop or select a resume file.",
            },
            {
              step: "2️⃣",
              title: "AI Extraction",
              desc: "Automatic information extraction.",
            },
            {
              step: "3️⃣",
              title: "Document Request",
              desc: "AI agent requests PAN/Aadhaar.",
            },
            {
              step: "4️⃣",
              title: "Verification",
              desc: "Complete candidate verification.",
            },
          ].map(({ step, title, desc }) => (
            <div key={title}>
              <div className="text-primary-600 text-3xl mb-2">{step}</div>
              <h4 className="font-semibold text-gray-800 mb-1">{title}</h4>
              <p className="text-gray-600 text-sm">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
