"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getCandidate, requestDocuments } from "@/lib/client";
import type { CandidateProfileData } from "@/lib/types";
import { utcToIndianTime } from "@/utils/utcToIndianTime";
import Link from "next/link";

export default function CandidateProfilePage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<CandidateProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [requestMsg, setRequestMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const controller = new AbortController();

    const fetchCandidate = async () => {
      try {
        setLoading(true);
        const res = await getCandidate(id, controller.signal);
        setData(res || null);
      } catch (err: any) {
        if (err.name !== "AbortError") {
          console.error("getCandidate failed:", err);
          setError("Failed to load candidate data.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchCandidate();
    return () => controller.abort();
  }, [id]);

  useEffect(() => {
    document.title = data?.candidate?.name
      ? `${data.candidate.name} - HireBuddy`
      : "Candidate Profile - HireBuddy";
  }, [data]);

  async function handleRequestDocs() {
    if (!id) return;
    setRequestMsg("Sending request...");
    try {
      await requestDocuments(id);
      setRequestMsg("Request queued successfully.");
    } catch {
      setRequestMsg("Failed to queue request.");
    }
  }

  if (loading)
    return (
      <div className="p-8 text-center text-gray-500 animate-pulse">
        Loading candidate profile...
      </div>
    );

  if (error)
    return (
      <div className="p-8 text-center text-red-600 font-medium">{error}</div>
    );

  if (!data) return null;

  const { candidate } = data;
  const parsedSection = candidate.parsed_data || {};
  const parsed = (parsedSection as any).parsed_data || {};
  const confidence = (parsedSection as any).confidence || {};

  return (
    <main className="w-full max-w-[1600px] mx-auto mt-6 flex flex-col lg:flex-row gap-8 px-6">
      {/* LEFT SECTION — 75% */}
      <div className="flex-1 lg:w-3/4 space-y-6">
        {/* Profile Info */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Profile</h2>
            <Link
              href={`/candidates/${id}/manage-documents`}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg 
                 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-400 transition-colors"
            >
              Manage Documents
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field label="Name" value={candidate.name} />
            <Field label="Email" value={candidate.email} />
            <Field label="Company" value={candidate.curr_company} />
            <Field label="Status" value={candidate.status} />
            <Field
              label="Created At"
              // value={new Date(candidate.created_at).toLocaleString()}
              value={utcToIndianTime(new Date(candidate.created_at).toLocaleString())}
            />
            <Field
              label="Updated At"
              value={utcToIndianTime(new Date(candidate.updated_at).toLocaleString())}

            />
          </div>
        </section>


        {/* Parsed Resume Data */}
        {Object.keys(parsed).length > 0 && (
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">
              Parsed Resume Data
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {Object.entries(parsed).map(([key, value]) => (
                <div key={key}>
                  <div className="flex items-center justify-between">
                    <Label label={formatKey(key)} />
                    {confidence[key] !== undefined && (
                      <ConfidenceBar score={confidence[key]} />
                    )}
                  </div>

                  <p className="text-gray-700 mt-1">
                    {Array.isArray(value)
                      ? value
                        .map((v) =>
                          v && typeof v === "object"
                            ? JSON.stringify(v, null, 2)
                            : String(v ?? "")
                        )
                        .join(", ")
                      : value && typeof value === "object"
                        ? JSON.stringify(value, null, 2)
                        : String(value ?? "—")}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>

      {/* RIGHT SECTION — 25% */}
      <aside
        className="lg:w-1/4 w-full bg-white rounded-xl shadow-sm border border-gray-200 p-6 
             h-fit max-h-[calc(100vh-6rem)] overflow-y-auto sticky top-8 self-start"
      >

        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Document Requests</h2>
          <button
            onClick={handleRequestDocs}
            className="px-3 py-1.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-400 transition-colors"
          >
            Request
          </button>
        </div>


        {requestMsg && (
          <p
            className={`text-sm mb-4 ${requestMsg.includes("Failed")
              ? "text-red-600"
              : "text-green-600"
              }`}
          >
            {requestMsg}
          </p>
        )}

        {/* Document Requests */}
        {(candidate.document_requests ?? "") !== "" && (
          <section className="mt-4">

            {(() => {
              let requests: any = [];

              const raw = candidate.document_requests;

              try {
                if (Array.isArray(raw)) {
                  requests = raw;
                } else if (typeof raw === "string") {
                  const trimmed = raw.trim();
                  if (!trimmed || trimmed === "null") {
                    requests = [];
                  } else {
                    requests = JSON.parse(trimmed);
                    if (typeof requests === "string") {
                      const inner = requests.trim();
                      requests = inner ? JSON.parse(inner) : [];
                    }
                  }
                } else {
                  requests = [];
                }
              } catch (err) {
                console.warn("Failed to parse document_requests:", err, raw);
                requests = [];
              }

              if (!requests || requests.length === 0) {
                return <p className="text-sm text-gray-500">No requests yet.</p>;
              }

              // Reverse newest-first
              const reversed = [...requests].reverse();

              return (
                <div className="max-h-128 overflow-y-auto pr-2 custom-scrollbar">
                  <ul className="space-y-4">
                    {reversed.map((req, i) => (
                      <li
                        key={i}
                        className="p-3 border border-gray-200 rounded-lg bg-gray-50"
                      >
                        <p className="text-xs text-gray-500 mb-1">
                          {req.timestamp
                            ? utcToIndianTime(new Date(req.timestamp).toLocaleString())
                            : "—"}
                        </p>
                        <p className="text-sm text-gray-700 whitespace-pre-wrap">
                          {req.message || "—"}
                        </p>
                        <p
                          className={`text-xs mt-2 font-medium ${req.status === "sent"
                            ? "text-green-600"
                            : req.status === "failed"
                              ? "text-red-600"
                              : "text-gray-600"
                            }`}
                        >
                          Status: {req.status || "unknown"}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })()}
          </section>
        )}
      </aside>



    </main>
  );
}

/* --- Reusable Components --- */

function Field({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <Label label={label} />
      <p className="text-gray-600">{value || "—"}</p>
    </div>
  );
}

function Label({ label }: { label: string }) {
  return <p className="text-gray-800 font-medium mb-1">{label}</p>;
}

function ConfidenceBar({ score }: { score: number }) {
  const percent = Math.round(score * 100);
  const color =
    percent > 90
      ? "bg-green-500"
      : percent > 70
        ? "bg-yellow-500"
        : "bg-red-500";

  return (
    <div className="flex items-center gap-2 text-xs text-gray-500">
      <div className="w-16 bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`${color} h-2 rounded-full`}
          style={{ width: `${percent}%` }}
        />
      </div>
      <span>{percent}%</span>
    </div>
  );
}

function formatKey(key: string) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (l) => l.toUpperCase());
}
