"use client";

import { useState, useCallback, useEffect } from "react";
import { Upload, X, FileAudio, Sparkles } from "lucide-react";

interface UploadWidgetProps {
  onUploadComplete: (jobId: string) => void;
  onUploadStart: () => void;
  onFilesSelected?: (files: File[]) => void;
  skipAutoUpload?: boolean;
}

export default function UploadWidget({
  onUploadComplete,
  onUploadStart,
  onFilesSelected,
  skipAutoUpload = false,
}: UploadWidgetProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  // Notify parent when files change
  useEffect(() => {
    if (files.length > 0 && onFilesSelected) {
      onFilesSelected(files);
    }
  }, [files, onFilesSelected]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files).filter((file) => {
      const ext = file.name.toLowerCase();
      return (
        ext.endsWith(".wav") ||
        ext.endsWith(".aiff") ||
        ext.endsWith(".flac") ||
        ext.endsWith(".mp3")
      );
    });

    setFiles((prev) => [...prev, ...droppedFiles].slice(0, 12));
  }, []);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        const selectedFiles = Array.from(e.target.files);
        setFiles((prev) => [...prev, ...selectedFiles].slice(0, 12));
      }
    },
    []
  );

  const removeFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleUpload = async () => {
    if (files.length === 0) return;

    onUploadStart();

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      onUploadComplete(data.job_id);
    } catch (error) {
      console.error("Upload error:", error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className={skipAutoUpload ? "" : "card glow"}>
      {/* Drop Zone with gradient border on hover */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className="group relative rounded-2xl p-16 text-center transition-all duration-300"
      >
        {/* Gradient border wrapper */}
        <div
          className={`absolute inset-0 rounded-2xl transition-opacity duration-300 ${
            isDragging ? "opacity-100" : "opacity-0 group-hover:opacity-100"
          }`}
          style={{
            background: "linear-gradient(135deg, #a855f7, #ec4899, #a855f7)",
            padding: "2px",
            WebkitMask:
              "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
            WebkitMaskComposite: "xor",
            maskComposite: "exclude",
          }}
        ></div>

        {/* Default dashed border */}
        <div
          className={`absolute inset-0 rounded-2xl border-2 border-dashed transition-opacity duration-300 ${
            isDragging
              ? "border-transparent opacity-0"
              : "border-white/20 group-hover:opacity-0"
          }`}
        ></div>

        {/* Background on drag */}
        <div
          className={`absolute inset-0 rounded-2xl bg-purple-500/10 transition-all duration-300 ${
            isDragging ? "opacity-100 scale-[1.02]" : "opacity-0"
          }`}
        ></div>

        {/* Content */}
        <div className="relative">
          <div
            className={`mb-6 transition-transform duration-300 ${
              isDragging ? "scale-110" : ""
            }`}
          >
            <Upload
              className={`w-12 h-12 mx-auto mb-4 ${
                isDragging ? "text-pink-400" : "text-purple-400"
              }`}
            />
          </div>

          <h3 className="text-2xl font-bold mb-3">
            Drop your audio files here
          </h3>
          <p className="text-gray-500 mb-6 max-w-md mx-auto">
            or click to browse your computer
          </p>

          <input
            type="file"
            multiple
            accept=".wav,.aiff,.flac,.mp3"
            onChange={handleFileSelect}
            className="hidden"
            id="file-input"
          />
          <label
            htmlFor="file-input"
            className="group/btn relative px-6 py-3 rounded-xl overflow-hidden cursor-pointer inline-flex items-center gap-2"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 transition-opacity"></div>
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 opacity-0 group-hover/btn:opacity-100 transition-opacity"></div>
            <Sparkles className="relative w-4 h-4 text-white" />
            <span className="relative font-bold text-white">Browse Files</span>
          </label>

          <div className="mt-8 pt-6 border-t border-white/5">
            <p className="text-xs text-gray-600 mb-2">Supported formats</p>
            <div className="flex items-center justify-center gap-3">
              {["WAV", "AIFF", "FLAC", "MP3"].map((format) => (
                <span
                  key={format}
                  className="px-3 py-1 rounded-full bg-white/5 text-gray-400 text-xs border border-white/5"
                >
                  {format}
                </span>
              ))}
            </div>
            <p className="text-xs text-gray-600 mt-4 flex items-center justify-center gap-3">
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-500/50"></span>
                Max 12 files
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-pink-500/50"></span>
                100MB each
              </span>
            </p>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-bold text-lg">
              Selected Files ({files.length}/12)
            </h4>
            <button
              onClick={() => setFiles([])}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Clear All
            </button>
          </div>

          <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-all group"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0">
                    <FileAudio className="w-5 h-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium truncate">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors flex-shrink-0 opacity-0 group-hover:opacity-100"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          {/* Only show upload button if not skipping auto upload */}
          {!skipAutoUpload && (
            <button
              onClick={handleUpload}
              className="btn btn-primary w-full mt-6 text-base py-4 inline-flex items-center justify-center gap-2"
              disabled={files.length === 0}
            >
              <Sparkles className="w-5 h-5" />
              <span>
                Upload & Process {files.length}{" "}
                {files.length === 1 ? "File" : "Files"}
              </span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
