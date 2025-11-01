"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listCandidates } from "@/lib/client";
import type { Candidate } from "@/lib/types";
import { utcToIndianTime } from "@/utils/utcToIndianTime";

export default function DashboardPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  useEffect(() => {
    document.title = "Dashboard - HireBuddy";
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    const loadCandidates = async () => {
      setLoading(true);
      setError(null);

      try {
        const res = await listCandidates(page,pageSize,controller.signal,);
        setCandidates(res.candidates || []);
        setTotalPages(res.pagination?.pages ?? 1);
      } catch (err: any) {
        if (err.name === "AbortError") {
          console.log("Fetch aborted");
          return;
        }
        console.error("listCandidates failed:", err);
        setError("Failed to load candidates. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    loadCandidates();
    return () => controller.abort();
  }, [page, pageSize]); // refetch when page size changes

  const handlePrev = () => setPage((p) => Math.max(1, p - 1));
  const handleNext = () => setPage((p) => Math.min(totalPages, p + 1));

  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 w-full max-w-6xl mx-auto mt-6">
      {/* Header */}
      <header className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-gray-800">Candidates</h1>

        <div className="flex items-center gap-3">
          {/* Page Size Dropdown */}
          <label className="text-sm text-gray-600 flex items-center gap-2">
            Show:
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setPage(1); // reset to first page when page size changes
              }}
              className="border rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400"
            >
              {[5, 10, 20, 30, 50].map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </label>

          <Link
            href="/upload"
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-400 focus:outline-none transition-colors"
          >
            Upload Resume
          </Link>
        </div>
      </header>

      {loading ? (
        <div className="text-gray-500 text-center py-6 animate-pulse">
          Loading candidates...
        </div>
      ) : error ? (
        <div className="text-red-600 text-center py-6">{error}</div>
      ) : candidates.length === 0 ? (
        <div className="text-gray-500 text-center py-6">
          No candidates found.
        </div>
      ) : (
        <>
          <div className="overflow-x-auto max-h-[70vh] rounded-md border border-gray-100">
            <table className="min-w-full border-collapse text-sm text-left text-gray-700">
              <thead className="bg-gray-100 text-gray-600 text-xs uppercase sticky top-0">
                <tr>
                  <th className="px-4 py-3 font-semibold">Sl No</th>
                  <th className="px-4 py-3 font-semibold">Name</th>
                  <th className="px-4 py-3 font-semibold">Email</th>
                  <th className="px-4 py-3 font-semibold">Company</th>
                  <th className="px-4 py-3 font-semibold">Status</th>
                  <th className="px-4 py-3 font-semibold">Last Updated</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {candidates.map((c, id) => (
                  <tr
                    key={c.id}
                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    <td className="px-4 py-3">
                      {(page - 1) * pageSize + (id + 1)}
                    </td>
                    <td className="px-4 py-3 font-medium text-primary-700 hover:underline">
                      <Link href={`/candidates/${c.id}`}>
                        {c.name ?? "—"}
                      </Link>
                    </td>
                    <td className="px-4 py-3">{c.email ?? "—"}</td>
                    <td className="px-4 py-3">{c.company ?? "—"}</td>
                    <td className="px-4 py-3">
                      {(() => {
                        const status = (c.extractionStatus ?? "").toLowerCase();
                        const colorMap: Record<string, string> = {
                          completed: "bg-green-100 text-green-700",
                          failed: "bg-red-100 text-red-700",
                          processing: "bg-yellow-100 text-yellow-700",
                          pending_documents: "bg-orange-100 text-orange-700",
                          document_requested: "bg-blue-100 text-blue-700",
                          partially_completed: "bg-purple-100 text-purple-700",
                        };
                        const colorClass =
                          colorMap[status] ?? "bg-gray-100 text-gray-600";
                        return (
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-semibold ${colorClass}`}
                          >
                            {c.extractionStatus ?? "unknown"}
                          </span>
                        );
                      })()}
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {c.updatedAt ? utcToIndianTime(c.updatedAt) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          <Pagination
            page={page}
            totalPages={totalPages}
            onPrev={handlePrev}
            onNext={handleNext}
          />
        </>
      )}
    </section>
  );
}

/**
 * Pagination Component
 */
function Pagination({
  page,
  totalPages,
  onPrev,
  onNext,
}: {
  page: number;
  totalPages: number;
  onPrev: () => void;
  onNext: () => void;
}) {
  return (
    <div className="flex justify-center items-center gap-2 mt-6">
      <button
        onClick={onPrev}
        disabled={page === 1}
        className="px-3 py-1 border rounded-md text-sm disabled:opacity-50 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-300"
      >
        Prev
      </button>
      <span className="text-gray-700 text-sm">
        Page {page} of {totalPages}
      </span>
      <button
        onClick={onNext}
        disabled={page === totalPages}
        className="px-3 py-1 border rounded-md text-sm disabled:opacity-50 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-300"
      >
        Next
      </button>
    </div>
  );
}
