"use client";
import { useEffect, useState } from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import UploadArea from "@/components/UploadArea";
import { uploadResume } from "@/lib/client";
import { CheckCircle, AlertCircle } from "lucide-react";

export default function UploadPage() {
  useEffect(() => {
    document.title = "Upload Resume - HireBuddy";
  }, []);

  const [progress, setProgress] = useState<number>(0);
  const [status, setStatus] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadAreaKey, setUploadAreaKey] = useState<number>(0);

  // Yup validation schema
  const validationSchema = Yup.object({
    name: Yup.string()
      .min(3, "Name must be at least 3 characters")
      .required("Name is required"),
    email: Yup.string()
      .email("Invalid email format")
      .required("Email is required"),
    currCompany: Yup.string()
      .min(2, "Company name must be at least 2 characters")
      .required("Current company is required"),
  });

  const formik = useFormik({
    initialValues: {
      name: "",
      email: "",
      currCompany: "",
    },
    validationSchema,
    validateOnMount: true,
    onSubmit: () => {},
  });

  const handleFile = async (file: File) => {
    // Double-check validation before upload
    await formik.validateForm();
    
    if (!formik.isValid || Object.keys(formik.errors).length > 0) {
      setStatus("⚠️ Please fill all required fields correctly before uploading.");
      return;
    }

    try {
      setUploading(true);
      setStatus("Uploading...");
      setProgress(25);

      const result: any = await uploadResume(file, {
        name: formik.values.name,
        email: formik.values.email,
        curr_company: formik.values.currCompany,
      });

      setProgress(100);
      setStatus(`✅ Uploaded successfully! Candidate ID: ${result.candidate_id}`);

      // Reset everything after successful upload
      setTimeout(() => {
        formik.resetForm();
        setProgress(0);
        setStatus(null);
        setUploading(false);
        setUploadAreaKey(prev => prev + 1); // Force UploadArea to reset
      }, 2500);
    } catch (e) {
      console.error(e);
      setStatus("❌ Upload failed. Please try again.");
      setProgress(0);
      setUploading(false);
    }
  };

  // Check if all required fields are valid (not just touched)
  const isFormComplete = 
    formik.values.name.length >= 3 &&
    formik.values.email.length > 0 &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formik.values.email) &&
    formik.values.currCompany.length >= 2;

  return (
    <div className="flex justify-center items-center max-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <section className="bg-white w-full max-w-xl rounded-2xl shadow-lg p-8 bg-white">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
          Upload Candidate Resume
        </h2>

        {/* Form */}
        <form onSubmit={formik.handleSubmit} className="space-y-5">
          {/* Full Name */}
          <div className="relative">
            <label className="block text-gray-700 font-medium mb-1">
              Full Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              value={formik.values.name}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              placeholder="Enter full name"
              disabled={uploading}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:outline-none transition ${
                uploading ? "bg-gray-100 cursor-not-allowed" :
                formik.touched.name && formik.errors.name
                  ? "border-red-400 focus:ring-red-400"
                  : formik.touched.name && !formik.errors.name
                  ? "border-green-400 focus:ring-green-400"
                  : "border-gray-300 focus:ring-blue-500"
              }`}
            />
            {formik.touched.name && formik.errors.name && (
              <p className="text-sm text-red-600 mt-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" /> {formik.errors.name}
              </p>
            )}
            {formik.touched.name && !formik.errors.name && formik.values.name && (
              <CheckCircle className="absolute right-3 top-10 text-green-500 w-5 h-5" />
            )}
          </div>

          {/* Email */}
          <div className="relative">
            <label className="block text-gray-700 font-medium mb-1">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              name="email"
              value={formik.values.email}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              placeholder="Enter email address"
              disabled={uploading}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:outline-none transition ${
                uploading ? "bg-gray-100 cursor-not-allowed" :
                formik.touched.email && formik.errors.email
                  ? "border-red-400 focus:ring-red-400"
                  : formik.touched.email && !formik.errors.email
                  ? "border-green-400 focus:ring-green-400"
                  : "border-gray-300 focus:ring-blue-500"
              }`}
            />
            {formik.touched.email && formik.errors.email && (
              <p className="text-sm text-red-600 mt-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" /> {formik.errors.email}
              </p>
            )}
            {formik.touched.email && !formik.errors.email && formik.values.email && (
              <CheckCircle className="absolute right-3 top-10 text-green-500 w-5 h-5" />
            )}
          </div>

          {/* Current Company */}
          <div className="relative">
            <label className="block text-gray-700 font-medium mb-1">
              Current Company <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="currCompany"
              value={formik.values.currCompany}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              placeholder="Enter current company name"
              disabled={uploading}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:outline-none transition ${
                uploading ? "bg-gray-100 cursor-not-allowed" :
                formik.touched.currCompany && formik.errors.currCompany
                  ? "border-red-400 focus:ring-red-400"
                  : formik.touched.currCompany && !formik.errors.currCompany
                  ? "border-green-400 focus:ring-green-400"
                  : "border-gray-300 focus:ring-blue-500"
              }`}
            />
            {formik.touched.currCompany && formik.errors.currCompany && (
              <p className="text-sm text-red-600 mt-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" /> {formik.errors.currCompany}
              </p>
            )}
            {formik.touched.currCompany && !formik.errors.currCompany && formik.values.currCompany && (
              <CheckCircle className="absolute right-3 top-10 text-green-500 w-5 h-5" />
            )}
          </div>

          {/* Upload Area */}
          <div className="mt-8">
            <div
              className={`transition-opacity ${
                isFormComplete && !uploading
                  ? "opacity-100"
                  : "opacity-50 pointer-events-none"
              }`}
            >
              <UploadArea 
                key={uploadAreaKey}
                onFileSelected={handleFile} 
                disabled={!isFormComplete || uploading} 
              />
            </div>
            {!isFormComplete && !uploading && (
              <p className="text-center text-sm text-gray-500 mt-2">
                ⚠️ Please fill all fields correctly before uploading.
              </p>
            )}
          </div>
        </form>

        {/* Progress Bar */}
        {progress > 0 && (
          <div className="w-full h-2 bg-gray-200 rounded-full mt-6">
            <div
              className="h-2 bg-blue-600 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        {/* Status */}
        {status && (
          <div className="mt-4 text-center">
            <p
              className={`text-sm font-medium ${
                status.includes("✅")
                  ? "text-green-600"
                  : status.includes("⚠️")
                  ? "text-yellow-600"
                  : status.includes("❌")
                  ? "text-red-600"
                  : "text-gray-600"
              }`}
            >
              {status}
            </p>
          </div>
        )}
      </section>
    </div>
  );
}