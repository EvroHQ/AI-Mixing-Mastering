"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Music2,
  Music,
  Download,
  ArrowLeft,
  CheckCircle2,
  Loader2,
  Sparkles,
  ChevronDown,
  Play,
  Pause,
} from "lucide-react";
import UploadWidget from "@/components/UploadWidget";
import ProAudioPlayer from "@/components/ProAudioPlayer";
import ProcessingStatus from "@/components/ProcessingStatus";

interface Genre {
  id: string;
  name: string;
  description: string;
  target_lufs: number;
}

interface GenreDetectionResult {
  genre: string;
  genre_name: string;
  confidence: number;
  description: string;
  all_scores: Record<string, number>;
  recommended_settings: {
    target_lufs: number;
    ceiling_dbTP: number;
    stereo_width: number;
  };
  available_genres: string[];
}

export default function StudioPage() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<
    "idle" | "uploading" | "analyzing" | "processing" | "complete" | "error"
  >("idle");
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [mp3Url, setMp3Url] = useState<string | null>(null);
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const [stage, setStage] = useState<string>("");
  const [detail, setDetail] = useState<string>("");

  // Genre state
  const [genres, setGenres] = useState<Genre[]>([]);
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [detectedGenre, setDetectedGenre] =
    useState<GenreDetectionResult | null>(null);
  const [showGenreSelector, setShowGenreSelector] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  // Fetch available genres on mount
  useEffect(() => {
    fetchGenres();
  }, []);

  const fetchGenres = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/genres`
      );
      const data = await response.json();
      setGenres(data.genres);
    } catch (error) {
      console.error("Error fetching genres:", error);
    }
  };

  // Add files to the list (without starting analysis)
  const handleFilesSelected = (files: File[]) => {
    setUploadedFiles((prev) => {
      // Avoid duplicates
      const existingNames = new Set(prev.map((f) => f.name));
      const newFiles = files.filter((f) => !existingNames.has(f.name));
      return [...prev, ...newFiles];
    });
  };

  // Remove a file from the list
  const handleRemoveFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // Start genre analysis when user clicks the button
  const handleStartAnalysis = async () => {
    if (uploadedFiles.length === 0) return;

    setStatus("analyzing");

    // Create FormData for genre analysis
    const formData = new FormData();
    uploadedFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/analyze-genre`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (response.ok) {
        const result: GenreDetectionResult = await response.json();
        setDetectedGenre(result);
        setSelectedGenre(result.genre);
        setShowGenreSelector(true);
        setStatus("idle");
      } else {
        // Fallback to showing genre selector without detection
        setShowGenreSelector(true);
        setStatus("idle");
      }
    } catch (error) {
      console.error("Error analyzing genre:", error);
      setShowGenreSelector(true);
      setStatus("idle");
    }
  };

  const handleStartProcessing = async () => {
    if (uploadedFiles.length === 0) return;

    setStatus("uploading");

    const formData = new FormData();
    uploadedFiles.forEach((file) => {
      formData.append("files", file);
    });

    // Add genre if selected
    if (selectedGenre) {
      formData.append("genre", selectedGenre);
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/upload-with-genre`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (data.job_id) {
        setJobId(data.job_id);
        setStatus("processing");
        pollJobStatus(data.job_id);
      }
    } catch (error) {
      console.error("Error starting processing:", error);
      setStatus("error");
    }
  };

  const handleUploadComplete = (newJobId: string) => {
    setJobId(newJobId);
    setStatus("processing");
    pollJobStatus(newJobId);
  };

  const pollJobStatus = async (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/status/${jobId}`
        );
        const data = await response.json();

        console.log("API Response:", data);

        setProgress(data.progress || 0);

        if (data.stage) setStage(data.stage);
        if (data.detail) setDetail(data.detail);

        if (data.status === "complete") {
          setStatus("complete");
          setDownloadUrl(data.download_url);
          setMp3Url(data.mp3_url);
          setOriginalUrl(data.original_url);
          clearInterval(interval);
        } else if (data.status === "error") {
          setStatus("error");
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Error polling status:", error);
      }
    }, 2000);
  };

  const handleReset = () => {
    setJobId(null);
    setStatus("idle");
    setProgress(0);
    setDownloadUrl(null);
    setOriginalUrl(null);
    setDetectedGenre(null);
    setSelectedGenre(null);
    setShowGenreSelector(false);
    setUploadedFiles([]);
  };

  const getGenreIcon = (genreId: string) => {
    const icons: Record<string, string> = {
      edm: "🎧",
      hiphop: "🎤",
      pop: "⭐",
      rock: "🎸",
      rnb: "💫",
      acoustic: "🎻",
      metal: "🤘",
    };
    return icons[genreId] || "🎵";
  };

  return (
    <div className="min-h-screen grid-background">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass">
        <nav className="container mx-auto px-6 py-5 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-white to-gray-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Music2 className="w-6 h-6 text-black" />
            </div>
            <span className="text-2xl font-bold tracking-tight">MixMaster</span>
          </Link>

          <Link
            href="/"
            className="text-sm inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-purple-500/30 text-gray-300 hover:text-white hover:border-purple-500/50 transition-all"
          >
            <ArrowLeft className="w-4 h-4 text-purple-400" />
            Back to Home
          </Link>
        </nav>
      </header>

      {/* Main Content */}
      <main className="pt-32 pb-16 px-6 relative z-10">
        <div className="container mx-auto max-w-5xl">
          {/* Title */}
          <div className="text-center mb-16 animate-fade-in">
            <h1 className="text-6xl font-bold mb-6 glow-text">
              AI Mix & Master{" "}
              <span className="text-gradient-accent">Studio</span>
            </h1>
            <p className="text-xl text-gray-400">
              AI mixing and mastering for studio quality results
            </p>
          </div>

          {/* Upload Section - Before Genre Detection */}
          {status === "idle" && !showGenreSelector && (
            <div className="animate-fade-in space-y-8">
              <div className="card">
                <div className="flex items-center gap-3 mb-6">
                  <Sparkles className="w-6 h-6 text-purple-400" />
                  <h2 className="text-2xl font-bold">
                    Step 1: Upload Your Stems
                  </h2>
                </div>
                <p className="text-gray-400 mb-6">
                  Upload your audio stems. You can add multiple files, then
                  click "Start Analysis" when ready.
                </p>
                <UploadWidget
                  onUploadComplete={handleUploadComplete}
                  onUploadStart={() => setStatus("uploading")}
                  onFilesSelected={handleFilesSelected}
                  skipAutoUpload={true}
                />

                {/* Uploaded Files List */}
                {uploadedFiles.length > 0 && (
                  <div className="mt-8">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-white">
                        {uploadedFiles.length} Stems Ready
                      </h3>
                      <button
                        onClick={() => setUploadedFiles([])}
                        className="text-sm text-gray-500 hover:text-red-400 transition-colors"
                      >
                        Clear all
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
                      {uploadedFiles.map((file, index) => {
                        const name = file.name.toLowerCase();
                        const getIcon = () => {
                          if (name.includes("vocal") || name.includes("voice"))
                            return "🎤";
                          if (name.includes("drum") || name.includes("beat"))
                            return "🥁";
                          if (name.includes("bass")) return "🎸";
                          if (
                            name.includes("synth") ||
                            name.includes("key") ||
                            name.includes("piano")
                          )
                            return "🎹";
                          if (name.includes("guitar")) return "🎸";
                          if (name.includes("perc")) return "🪘";
                          return "🎵";
                        };
                        return (
                          <div
                            key={index}
                            className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10 group"
                          >
                            <span className="text-lg">{getIcon()}</span>
                            <span className="text-sm text-gray-300 truncate flex-1">
                              {file.name.replace(/\.(wav|mp3|aiff|flac)$/i, "")}
                            </span>
                            <span className="text-xs text-gray-500">
                              {(file.size / 1024 / 1024).toFixed(1)}MB
                            </span>
                            <button
                              onClick={() => handleRemoveFile(index)}
                              className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition-all"
                            >
                              ✕
                            </button>
                          </div>
                        );
                      })}
                    </div>

                    {/* Start Analysis Button */}
                    <button
                      onClick={handleStartAnalysis}
                      className="w-full group relative overflow-hidden cursor-pointer"
                    >
                      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 opacity-75 group-hover:opacity-100 transition-opacity"></div>
                      <div className="relative px-8 py-4 rounded-xl bg-black m-[2px] flex items-center justify-center gap-3 group-hover:bg-black/80 transition-colors">
                        <Sparkles className="w-5 h-5 text-purple-400 group-hover:text-pink-400 transition-colors" />
                        <span className="font-bold text-white text-lg">
                          Start AI Genre Analysis
                        </span>
                      </div>
                    </button>
                  </div>
                )}
              </div>

              <div className="card">
                <h3 className="text-xl font-bold mb-6">Supported Formats</h3>
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <p className="font-semibold mb-4 text-sm uppercase tracking-wider text-gray-400">
                      Audio Formats
                    </p>
                    <ul className="space-y-2 text-gray-300">
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
                        WAV (recommended)
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
                        AIFF
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
                        FLAC
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
                        MP3 (320kbps)
                      </li>
                    </ul>
                  </div>
                  <div>
                    <p className="font-semibold mb-4 text-sm uppercase tracking-wider text-gray-400">
                      Guidelines
                    </p>
                    <ul className="space-y-2 text-gray-300">
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-pink-500"></div>
                        Up to 32 stems per project
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-pink-500"></div>
                        Max 100MB per file
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-pink-500"></div>
                        44.1kHz or 48kHz sample rate
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-pink-500"></div>
                        16-bit or 24-bit depth
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Analyzing Genre */}
          {status === "analyzing" && (
            <div className="animate-fade-in">
              <div className="card glow text-center py-16">
                <Loader2 className="w-16 h-16 mx-auto mb-6 animate-spin text-purple-400" />
                <h2 className="text-2xl font-bold mb-4">
                  Analyzing Your Music...
                </h2>
                <p className="text-gray-400">
                  Our AI is detecting the genre and optimal settings for your
                  track
                </p>
              </div>
            </div>
          )}

          {/* Genre Selection Section */}
          {status === "idle" && showGenreSelector && (
            <div className="animate-fade-in space-y-8">
              {/* Detected Genre Card */}
              {detectedGenre && (
                <div className="relative p-[2px] rounded-2xl bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500">
                  <div className="p-8 bg-black rounded-2xl">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        <Sparkles className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">
                          Genre Detected
                        </h2>
                        <p className="text-sm text-gray-500">
                          AI-powered analysis complete
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-8 mb-6">
                      <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center text-5xl border border-purple-500/30">
                        {getGenreIcon(detectedGenre.genre)}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                          {detectedGenre.genre_name}
                        </h3>
                        <p className="text-gray-400 mt-1">
                          {detectedGenre.description}
                        </p>
                        <div className="mt-4 flex items-center gap-4">
                          <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                              style={{
                                width: `${detectedGenre.confidence * 100}%`,
                              }}
                            ></div>
                          </div>
                          <span className="text-sm font-bold text-purple-300 min-w-[80px]">
                            {Math.round(detectedGenre.confidence * 100)}% match
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white/5 rounded-xl p-4 mb-6">
                      <p className="text-sm text-gray-400 mb-2">
                        Recommended Settings
                      </p>
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <p className="text-2xl font-bold text-purple-400">
                            {detectedGenre.recommended_settings.target_lufs}{" "}
                            LUFS
                          </p>
                          <p className="text-xs text-gray-500">
                            Target Loudness
                          </p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-pink-400">
                            {detectedGenre.recommended_settings.ceiling_dbTP}{" "}
                            dBTP
                          </p>
                          <p className="text-xs text-gray-500">True Peak</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-blue-400">
                            {detectedGenre.recommended_settings.stereo_width}%
                          </p>
                          <p className="text-xs text-gray-500">Stereo Width</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Genre Selector */}
              <div className="card">
                <h3 className="text-xl font-bold mb-4">
                  {detectedGenre
                    ? "Or select a different genre:"
                    : "Select Genre"}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {genres.map((genre) => (
                    <button
                      key={genre.id}
                      onClick={() => setSelectedGenre(genre.id)}
                      className={`p-4 rounded-xl border-2 transition-all text-left ${
                        selectedGenre === genre.id
                          ? "border-purple-500 bg-purple-500/10"
                          : "border-white/10 hover:border-white/30"
                      }`}
                    >
                      <div className="text-3xl mb-2">
                        {getGenreIcon(genre.id)}
                      </div>
                      <p className="font-bold">{genre.name}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {genre.target_lufs} LUFS
                      </p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Files Summary - Clean Design */}
              <div className="card">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center border border-white/10">
                      <Music className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold">
                        {uploadedFiles.length} Stems
                      </h3>
                      <p className="text-sm text-gray-500">Ready to process</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Selected genre</p>
                    <p className="font-bold text-purple-400">
                      {selectedGenre
                        ? genres.find((g) => g.id === selectedGenre)?.name ||
                          selectedGenre
                        : detectedGenre?.genre_name || "Auto-detect"}
                    </p>
                  </div>
                </div>

                {/* Stem Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                  {uploadedFiles.map((f, i) => {
                    // Determine stem type for icon
                    const name = f.name.toLowerCase();
                    const getIcon = () => {
                      if (name.includes("vocal") || name.includes("voice"))
                        return "🎤";
                      if (name.includes("drum") || name.includes("beat"))
                        return "🥁";
                      if (name.includes("bass")) return "🎸";
                      if (
                        name.includes("synth") ||
                        name.includes("key") ||
                        name.includes("piano")
                      )
                        return "🎹";
                      if (name.includes("guitar")) return "🎸";
                      if (name.includes("perc")) return "🪘";
                      return "🎵";
                    };

                    return (
                      <div
                        key={i}
                        className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors"
                      >
                        <span className="text-lg">{getIcon()}</span>
                        <span className="text-sm text-gray-300 truncate flex-1">
                          {f.name.replace(/\.(wav|mp3|aiff|flac)$/i, "")}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* Action Button */}
                <button
                  onClick={handleStartProcessing}
                  className="w-full group relative overflow-hidden cursor-pointer"
                >
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 opacity-75 group-hover:opacity-100 transition-opacity"></div>
                  <div className="relative px-8 py-4 rounded-xl bg-black m-[2px] flex items-center justify-center gap-3 group-hover:bg-black/80 transition-colors">
                    <Sparkles className="w-5 h-5 text-purple-400 group-hover:text-pink-400 transition-colors" />
                    <span className="font-bold text-white text-lg">
                      Start Mixing & Mastering
                    </span>
                  </div>
                </button>
              </div>
            </div>
          )}

          {/* Processing Section */}
          {(status === "uploading" || status === "processing") && (
            <div className="animate-fade-in">
              <ProcessingStatus
                status={status}
                progress={progress}
                jobId={jobId}
                stage={stage}
                detail={detail}
                genreName={detectedGenre?.genre_name}
              />
            </div>
          )}

          {/* Complete Section */}
          {status === "complete" && downloadUrl && (
            <div className="animate-fade-in space-y-8">
              <div className="card glow">
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center">
                      <CheckCircle2 className="w-6 h-6" />
                    </div>
                    <div>
                      <h2 className="text-3xl font-bold">
                        Your Master is Ready!
                      </h2>
                      {detectedGenre && (
                        <p className="text-gray-400">
                          Processed as {detectedGenre.genre_name}
                        </p>
                      )}
                    </div>
                  </div>
                  <button onClick={handleReset} className="btn btn-secondary">
                    Start New Project
                  </button>
                </div>

                {/* Audio Player */}
                <div className="mb-8">
                  <ProAudioPlayer
                    masterUrl={mp3Url || downloadUrl}
                    title={
                      detectedGenre
                        ? `${detectedGenre.genre_name} Master`
                        : "Your Master"
                    }
                  />
                </div>

                {/* Download Buttons */}
                <div className="flex flex-wrap gap-4">
                  <a
                    href={downloadUrl}
                    download
                    className="btn btn-primary inline-flex items-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Download WAV Master
                  </a>
                  {mp3Url && (
                    <a
                      href={mp3Url}
                      download
                      className="btn btn-secondary inline-flex items-center gap-2"
                    >
                      <Download className="w-5 h-5" />
                      Download MP3
                    </a>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Error Section */}
          {status === "error" && (
            <div className="animate-fade-in">
              <div className="card border-red-500/50">
                <div className="text-center py-8">
                  <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-6">
                    <span className="text-4xl">❌</span>
                  </div>
                  <h2 className="text-2xl font-bold mb-4">Processing Error</h2>
                  <p className="text-gray-400 mb-6">
                    Something went wrong during processing. Please try again.
                  </p>
                  <button onClick={handleReset} className="btn btn-primary">
                    Try Again
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-16 px-6 border-t border-white/10 bg-black relative z-10">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-white to-gray-400 flex items-center justify-center">
                  <Music2 className="w-5 h-5 text-black" />
                </div>
                <span className="text-xl font-bold">MixMaster</span>
              </div>
              <p className="text-gray-500 text-sm leading-relaxed">
                Professional AI-powered audio mixing and mastering for modern
                producers.
              </p>
            </div>

            <div>
              <h4 className="font-bold mb-4 text-sm uppercase tracking-wider">
                Product
              </h4>
              <ul className="space-y-3 text-gray-400 text-sm">
                <li>
                  <Link
                    href="/#features"
                    className="hover:text-white transition-colors"
                  >
                    Features
                  </Link>
                </li>
                <li>
                  <Link
                    href="/#pricing"
                    className="hover:text-white transition-colors"
                  >
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link
                    href="/studio"
                    className="hover:text-white transition-colors"
                  >
                    Studio
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold mb-4 text-sm uppercase tracking-wider">
                Company
              </h4>
              <ul className="space-y-3 text-gray-400 text-sm">
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    About
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Blog
                  </Link>
                </li>
                <li>
                  <Link
                    href="/contact"
                    className="hover:text-white transition-colors"
                  >
                    Contact
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold mb-4 text-sm uppercase tracking-wider">
                Legal
              </h4>
              <ul className="space-y-3 text-gray-400 text-sm">
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Privacy
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Terms
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-white/10 pt-8 text-center text-gray-500 text-sm">
            <p>© 2025 MixMaster Studio. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
