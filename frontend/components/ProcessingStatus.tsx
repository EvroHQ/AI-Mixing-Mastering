"use client";

import {
  Loader2,
  CheckCircle2,
  Music,
  Sliders,
  Sparkles,
  Upload,
  Wand2,
  AudioWaveform,
} from "lucide-react";

interface ProcessingStatusProps {
  status: "uploading" | "processing";
  progress: number;
  jobId: string | null;
  stage?: string;
  detail?: string;
  genreName?: string;
}

const stages = [
  { id: "downloading", label: "Loading Stems", icon: Upload },
  { id: "processing", label: "Analyzing", icon: AudioWaveform },
  { id: "mixing", label: "Mixing", icon: Sliders },
  { id: "mastering", label: "Mastering", icon: Sparkles },
  { id: "uploading", label: "Finalizing", icon: Wand2 },
];

const stageDescriptions: Record<string, string> = {
  downloading: "Downloading your stems from cloud storage...",
  initializing: "Initializing professional audio engine...",
  processing: "Classifying stems and analyzing spectral content...",
  mixing: "Applying intelligent EQ, compression, and sidechain ducking...",
  mastering:
    "Optimizing loudness, applying limiting, and running quality checks...",
  uploading: "Uploading your professional mix and master...",
  finalizing: "Generating download URLs and creating report...",
  complete: "Processing complete! Your master is ready.",
};

export default function ProcessingStatus({
  status,
  progress,
  jobId,
  stage,
  detail,
  genreName,
}: ProcessingStatusProps) {
  const getCurrentStageIndex = () => {
    if (stage) {
      const stageMap: Record<string, number> = {
        downloading: 0,
        initializing: 0,
        processing: 1,
        mixing: 2,
        mastering: 3,
        uploading: 4,
        finalizing: 4,
        complete: 4,
      };
      const mappedIndex = stageMap[stage];
      if (mappedIndex !== undefined) return mappedIndex;
    }

    if (status === "uploading") return 0;
    if (progress < 25) return 1;
    if (progress < 60) return 2;
    if (progress < 90) return 3;
    return 4;
  };

  const currentStageIndex = getCurrentStageIndex();
  const currentStageLabel = stage
    ? stages.find((s) => s.id === stage)?.label || "Processing"
    : stages[currentStageIndex]?.label || "Processing";

  const currentDescription =
    detail ||
    stageDescriptions[stage || "processing"] ||
    "Processing your audio...";

  return (
    <div className="card">
      {/* Header */}
      <div className="text-center mb-8">
        {/* Animated Equalizer Visualization */}
        <div className="relative w-48 h-32 mx-auto mb-6 flex items-end justify-center gap-1">
          {/* Equalizer Bars */}
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="equalizer-bar"
              style={{
                animationDelay: `${i * 0.1}s`,
                height: "100%",
              }}
            />
          ))}
          {/* Glow overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-purple-500/20 to-transparent blur-xl" />
        </div>

        {/* Waveform Animation */}
        <div className="relative w-full h-16 mb-6 overflow-hidden rounded-xl bg-white/5">
          <div className="waveform-container">
            <svg
              className="waveform-svg"
              viewBox="0 0 200 40"
              preserveAspectRatio="none"
            >
              <path
                className="waveform-path"
                d="M0 20 Q 10 10, 20 20 T 40 20 T 60 20 T 80 20 T 100 20 T 120 20 T 140 20 T 160 20 T 180 20 T 200 20"
                fill="none"
                stroke="url(#waveGradient)"
                strokeWidth="2"
              />
              <defs>
                <linearGradient
                  id="waveGradient"
                  x1="0%"
                  y1="0%"
                  x2="100%"
                  y2="0%"
                >
                  <stop offset="0%" stopColor="#a855f7" />
                  <stop offset="50%" stopColor="#ec4899" />
                  <stop offset="100%" stopColor="#a855f7" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          {/* Scanning line */}
          <div className="scan-line" />
        </div>

        <h2 className="text-2xl font-bold mb-2">Processing...</h2>
        <p className="text-gray-500">
          Professional mixing & mastering in progress
        </p>

        {genreName && (
          <div className="mt-3 inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10">
            <span className="text-sm text-gray-400">Genre:</span>
            <span className="text-sm font-medium text-purple-400">
              {genreName}
            </span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between items-center mt-2">
          <span className="text-xs text-gray-600">0%</span>
          <span className="text-sm font-bold text-white">{progress}%</span>
          <span className="text-xs text-gray-600">100%</span>
        </div>
      </div>

      {/* Stages - Clean Design */}
      <div className="grid grid-cols-5 gap-2 mb-8">
        {stages.map((stageItem, index) => {
          const Icon = stageItem.icon;
          const isComplete = index < currentStageIndex;
          const isCurrent = index === currentStageIndex;

          return (
            <div
              key={stageItem.id}
              className={`
                p-3 rounded-xl text-center transition-all duration-300
                ${isCurrent ? "bg-white/5 border border-purple-500/30" : ""}
                ${isComplete ? "opacity-60" : ""}
                ${!isCurrent && !isComplete ? "opacity-30" : ""}
              `}
            >
              <div className="flex flex-col items-center gap-2">
                {/* Icon - gradient for current, plain for others */}
                {isComplete ? (
                  <CheckCircle2 className="w-6 h-6 text-green-500" />
                ) : isCurrent ? (
                  <Icon className="w-6 h-6 text-purple-400" />
                ) : (
                  <Icon className="w-6 h-6 text-gray-600" />
                )}
                <span
                  className={`
                    text-xs font-medium
                    ${isCurrent ? "text-white" : ""}
                    ${isComplete ? "text-gray-400" : ""}
                    ${!isCurrent && !isComplete ? "text-gray-600" : ""}
                  `}
                >
                  {stageItem.label}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Current Stage Details - Simple Design */}
      <div className="p-4 bg-white/5 rounded-xl border border-white/5">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
            <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-white mb-1">{currentStageLabel}</p>
            <p className="text-sm text-gray-400">{currentDescription}</p>
          </div>
        </div>
      </div>

      {/* Job ID - Full */}
      {jobId && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <p className="text-xs text-gray-600 text-center font-mono">
            Job ID: {jobId}
          </p>
        </div>
      )}
    </div>
  );
}
