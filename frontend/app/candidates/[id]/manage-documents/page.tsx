"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { submitDocuments, getCandidate } from "@/lib/client";
import UploadArea from "@/components/UploadArea";
import { utcToIndianTime } from "@/utils/utcToIndianTime";

interface UploadedDoc {
  type: string;
  filename: string;
  path: string;
  uploaded_at: string;
}

export default function UploadDocumentsPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [selectedType, setSelectedType] = useState<"aadhaar" | "pan" | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [documents, setDocuments] = useState<UploadedDoc[]>([]);


  useEffect(() => {
    async function fetchDocs() {
      if (!id) return;
      try {
        const data = await getCandidate(id);
        console.log("Candidate data:", data?.candidate);
        const docsObj = data?.candidate?.documents || {};

        const docsList: UploadedDoc[] = Object.entries(docsObj)
          .filter(([_, info]: any) => info !== null && info !== undefined)
          .map(([type, info]: any) => ({
            type,
            filename: info.filename,
            path: info.path,
            uploaded_at: info.uploaded_at,
          }));

        setDocuments(docsList);
      } catch (err) {
        console.error("Failed to load documents:", err);
      }
    }
    fetchDocs();
  }, [id]);

  const getPublicUrl = (filePath: string) => {
    const relativePath = filePath
      .replace(/^.*uploads[\\/]/, "")
      .replace(/\\/g, "/");
    return `http://localhost:5000/uploads/${relativePath}`;
  };



  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id || !selectedType || !file) {
      setMessage("Please select document type and upload a file.");
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const res = await submitDocuments(id, [file], [selectedType]);
      setMessage(res.message || "Document uploaded successfully!");
      setTimeout(() => router.push(`/candidates/${id}`), 800);
    } catch (err: any) {
      console.error("Upload failed:", err);
      setMessage(err.message || "Failed to upload document.");
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="w-full max-w-2xl mx-auto mt-10 bg-white rounded-xl shadow-md border border-gray-200 p-8">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">
        Upload Document
      </h1>

      {/* 🧾 View Existing Documents */}
      {documents.length > 0 && (
        <section className="mb-8 bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h2 className="text-lg font-medium text-gray-800 mb-3">
            Uploaded Documents
          </h2>
          <ul className="space-y-2">
            {documents.map((doc) => (
              <li
                key={doc.type}
                className="flex justify-between items-center bg-white border border-gray-200 rounded-md p-3 shadow-sm"
              >
                <div>
                  <p className="font-medium text-gray-700 capitalize">
                    {doc.type}
                  </p>
                  <p className="text-xs text-gray-500">
                    Uploaded: {utcToIndianTime(new Date(doc.uploaded_at).toLocaleString())}
                  </p>
                </div>
                <a
                  href={getPublicUrl(doc.path)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline text-sm font-medium"
                >
                  View
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* Document Type Selector */}
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            Select Document Type
          </label>
          <div className="flex gap-4">
            {(["aadhaar", "pan"] as const).map((type) => {
              const alreadyUploaded = documents.some((doc) => doc.type === type); 
              return (
                <button
                  key={type}
                  type="button"
                  disabled={alreadyUploaded}
                  onClick={() => {
                    if (!alreadyUploaded) {
                      setSelectedType(type);
                      setFile(null);
                    }
                  }}
                  className={`px-4 py-2 rounded-lg border transition-colors
            ${alreadyUploaded
                      ? "bg-gray-200 text-gray-500 border-gray-300 cursor-not-allowed"
                      : selectedType === type
                        ? "bg-primary-600 text-white border-primary-600"
                        : "bg-white text-gray-700 border-gray-300 hover:border-primary-400"
                    }`}
                >
                  {type === "aadhaar" ? "Aadhaar" : "PAN"}
                  {alreadyUploaded && (
                    <span className="ml-2 text-xs text-green-600 font-medium">
                      ✓ Uploaded
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>


        {/* Upload Area */}
        {selectedType && (
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Upload {selectedType === "aadhaar" ? "Aadhaar" : "PAN"} Card
            </label>
            <UploadArea
              onFileSelected={(file) => setFile(file)}
              disabled={loading}
            />
            {file && (
              <p className="text-sm text-gray-600 mt-2 text-center">
                Selected: <strong>{file.name}</strong>
              </p>
            )}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !selectedType || !file}
          className={`w-full py-2 px-4 text-white font-medium rounded-lg 
            ${loading || !selectedType || !file
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-primary-600 hover:bg-primary-700"
            } transition-colors`}
        >
          {loading ? "Uploading..." : "Submit Document"}
        </button>

        {/* Status Message */}
        {message && (
          <p
            className={`text-center text-sm mt-4 ${message.toLowerCase().includes("fail")
              ? "text-red-600"
              : "text-green-600"
              }`}
          >
            {message}
          </p>
        )}
      </form>
    </main>
  );
}
