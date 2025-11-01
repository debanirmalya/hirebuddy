"use client";
import { useCallback, useRef, useState } from "react";

interface Props {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
  maxSizeMB?: number; // default 5MB
}

export default function UploadArea({
  onFileSelected,
  disabled = false,
  maxSizeMB = 5,
}: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // ✅ Allowed MIME types and extensions
  const allowedTypes = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/png",
    "image/jpeg",
  ];
  const allowedExtensions = [".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg"];

  const validateFile = (file: File) => {
    const maxBytes = maxSizeMB * 1024 * 1024;

    // ✅ Check size
    if (file.size > maxBytes) {
      setError(`❌ File exceeds ${maxSizeMB} MB limit`);
      return false;
    }

    // ✅ Check MIME type and extension
    const isValidType =
      allowedTypes.includes(file.type) ||
      allowedExtensions.some((ext) => file.name.toLowerCase().endsWith(ext));

    if (!isValidType) {
      setError("❌ Invalid file type. Allowed: PDF, DOC, DOCX, PNG, JPG, JPEG.");
      return false;
    }

    setError(null);
    return true;
  };

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragOver(false);
      if (disabled) return;
      const file = e.dataTransfer.files?.[0];
      if (file && validateFile(file)) {
        onFileSelected(file);
      }
    },
    [onFileSelected, disabled]
  );

  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file && validateFile(file)) {
        onFileSelected(file);
      }
    },
    [onFileSelected]
  );

  return (
    <div className="w-full">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        role="button"
        tabIndex={0}
        className={`flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-300
          ${
            dragOver
              ? "border-blue-500 bg-blue-50 shadow-md scale-[1.02]"
              : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
          }
          ${disabled ? "opacity-50 cursor-not-allowed" : ""}
          border border-gray-200`}
      >
        {/* Hidden file input */}
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/png,image/jpeg"
          style={{
            position: "absolute",
            left: "-9999px",
            width: "1px",
            height: "1px",
            opacity: 0,
          }}
          onChange={onChange}
          disabled={disabled}
        />

        {/* Inner content */}
        <div className="text-center select-none">
          <div className="text-4xl mb-2">📄</div>
          <p className="text-gray-700 font-medium">
            <strong>Drag & drop</strong> your file here
          </p>
          <p className="text-gray-500 text-sm mt-1">
            or click to select (PDF, DOC, DOCX, PNG, JPG, JPEG)
          </p>
          <p className="text-gray-400 text-xs mt-1">Max size: {maxSizeMB} MB</p>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <p className="text-red-600 text-sm text-center mt-2 font-medium">{error}</p>
      )}
    </div>
  );
}
