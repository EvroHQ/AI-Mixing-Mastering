"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Howl } from "howler";
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  SkipBack,
  SkipForward,
  Repeat,
  Download,
} from "lucide-react";

interface ProAudioPlayerProps {
  masterUrl: string;
  originalUrl?: string;
  mixUrl?: string;
  title?: string;
  onDownloadMaster?: () => void;
}

export default function ProAudioPlayer({
  masterUrl,
  originalUrl,
  mixUrl,
  title = "Your Master",
  onDownloadMaster,
}: ProAudioPlayerProps) {
  // Audio state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [isLooping, setIsLooping] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // A/B comparison state
  const [activeTrack, setActiveTrack] = useState<"master" | "original" | "mix">(
    "master"
  );

  // Waveform data
  const [waveformData, setWaveformData] = useState<number[]>([]);

  // Howl instances
  const howlRefs = useRef<{
    master: Howl | null;
    original: Howl | null;
    mix: Howl | null;
  }>({
    master: null,
    original: null,
    mix: null,
  });

  const animationRef = useRef<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Create fake waveform data for visualization
  const generateWaveform = useCallback(() => {
    const bars = 80;
    const data = [];
    for (let i = 0; i < bars; i++) {
      // Create a more natural looking waveform
      const base = Math.sin(i * 0.1) * 0.3 + 0.5;
      const random = Math.random() * 0.4;
      data.push(Math.min(1, Math.max(0.1, base + random)));
    }
    setWaveformData(data);
  }, []);

  // Initialize Howler instances
  useEffect(() => {
    generateWaveform();

    const createHowl = (url: string, onLoad?: () => void): Howl => {
      return new Howl({
        src: [url],
        html5: true,
        volume: volume,
        loop: isLooping,
        onload: () => {
          if (onLoad) onLoad();
        },
        onplay: () => {
          setIsPlaying(true);
          startProgressAnimation();
        },
        onpause: () => {
          setIsPlaying(false);
          stopProgressAnimation();
        },
        onstop: () => {
          setIsPlaying(false);
          setCurrentTime(0);
          stopProgressAnimation();
        },
        onend: () => {
          if (!isLooping) {
            setIsPlaying(false);
            setCurrentTime(0);
            stopProgressAnimation();
          }
        },
      });
    };

    // Master (always created)
    howlRefs.current.master = createHowl(masterUrl, () => {
      setDuration(howlRefs.current.master?.duration() || 0);
      setIsLoading(false);
    });

    // Original (optional)
    if (originalUrl) {
      howlRefs.current.original = createHowl(originalUrl);
    }

    // Mix (optional)
    if (mixUrl) {
      howlRefs.current.mix = createHowl(mixUrl);
    }

    return () => {
      Object.values(howlRefs.current).forEach((howl) => howl?.unload());
      stopProgressAnimation();
    };
  }, [masterUrl, originalUrl, mixUrl]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      switch (e.key.toLowerCase()) {
        case " ":
          e.preventDefault();
          togglePlay();
          break;
        case "a":
          if (originalUrl) switchTrack("original");
          break;
        case "b":
          switchTrack("master");
          break;
        case "m":
          if (mixUrl) switchTrack("mix");
          break;
        case "arrowleft":
          skipBack();
          break;
        case "arrowright":
          skipForward();
          break;
        case "l":
          toggleLoop();
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isPlaying, activeTrack, currentTime, originalUrl, mixUrl]);

  // Update volume on all tracks
  useEffect(() => {
    const actualVolume = isMuted ? 0 : volume;
    Object.values(howlRefs.current).forEach((howl) => {
      howl?.volume(actualVolume);
    });
  }, [volume, isMuted]);

  // Update loop on all tracks
  useEffect(() => {
    Object.values(howlRefs.current).forEach((howl) => {
      howl?.loop(isLooping);
    });
  }, [isLooping]);

  // Progress animation
  const startProgressAnimation = useCallback(() => {
    const animate = () => {
      const activeHowl = howlRefs.current[activeTrack];
      if (activeHowl && activeHowl.playing()) {
        setCurrentTime(activeHowl.seek() as number);
        animationRef.current = requestAnimationFrame(animate);
      }
    };
    animationRef.current = requestAnimationFrame(animate);
  }, [activeTrack]);

  const stopProgressAnimation = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
  }, []);

  // Playback controls
  const togglePlay = () => {
    const activeHowl = howlRefs.current[activeTrack];
    if (!activeHowl) return;

    if (isPlaying) {
      activeHowl.pause();
    } else {
      activeHowl.play();
    }
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const time = percentage * duration;

    setCurrentTime(time);
    howlRefs.current[activeTrack]?.seek(time);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    setIsMuted(false);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const toggleLoop = () => {
    setIsLooping(!isLooping);
  };

  const skipBack = () => {
    const activeHowl = howlRefs.current[activeTrack];
    if (activeHowl) {
      const newTime = Math.max(0, currentTime - 10);
      activeHowl.seek(newTime);
      setCurrentTime(newTime);
    }
  };

  const skipForward = () => {
    const activeHowl = howlRefs.current[activeTrack];
    if (activeHowl) {
      const newTime = Math.min(duration, currentTime + 10);
      activeHowl.seek(newTime);
      setCurrentTime(newTime);
    }
  };

  // A/B Switch with seamless crossfade
  const switchTrack = (track: "master" | "original" | "mix") => {
    if (track === activeTrack) return;
    if (track === "original" && !originalUrl) return;
    if (track === "mix" && !mixUrl) return;

    const currentHowl = howlRefs.current[activeTrack];
    const newHowl = howlRefs.current[track];

    if (!currentHowl || !newHowl) return;

    const currentPosition = currentHowl.seek() as number;
    const wasPlaying = isPlaying;

    // Pause current
    currentHowl.pause();

    // Seek new to same position
    newHowl.seek(currentPosition);

    // Play new if was playing
    if (wasPlaying) {
      newHowl.play();
    }

    setActiveTrack(track);
    setCurrentTime(currentPosition);
  };

  // Format time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div
      ref={containerRef}
      className="rounded-2xl border border-white/10 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/5">
        <h3 className="text-lg font-bold">{title}</h3>

        {/* Track switcher */}
        <div className="flex items-center gap-1 bg-white/5 rounded-full p-1">
          {originalUrl && (
            <button
              onClick={() => switchTrack("original")}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                activeTrack === "original"
                  ? "bg-white text-black"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Original
            </button>
          )}
          {mixUrl && (
            <button
              onClick={() => switchTrack("mix")}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                activeTrack === "mix"
                  ? "bg-blue-500 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Mix
            </button>
          )}
          <button
            onClick={() => switchTrack("master")}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
              activeTrack === "master"
                ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white"
                : "text-gray-400 hover:text-white"
            }`}
          >
            Master
          </button>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 border-white/20 border-t-purple-500 rounded-full animate-spin"></div>
          <span className="ml-3 text-gray-400">Loading audio...</span>
        </div>
      )}

      {/* Player */}
      {!isLoading && (
        <div className="p-4">
          {/* Waveform visualization */}
          <div
            className="relative h-24 mb-4 cursor-pointer group"
            onClick={handleSeek}
          >
            {/* Waveform bars */}
            <div className="absolute inset-0 flex items-center justify-between gap-[2px]">
              {waveformData.map((height, i) => {
                const barProgress = (i / waveformData.length) * 100;
                const isPlayed = barProgress <= progressPercent;

                return (
                  <div
                    key={i}
                    className={`flex-1 rounded-full transition-all duration-75 ${
                      isPlayed
                        ? "bg-gradient-to-t from-purple-500 to-pink-500"
                        : "bg-white/20 group-hover:bg-white/30"
                    }`}
                    style={{
                      height: `${height * 100}%`,
                      opacity: isPlayed ? 1 : 0.6,
                    }}
                  ></div>
                );
              })}
            </div>

            {/* Playhead */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-white shadow-lg shadow-white/50 z-10"
              style={{ left: `${progressPercent}%` }}
            ></div>
          </div>

          {/* Time display */}
          <div className="flex justify-between text-sm text-gray-400 mb-6">
            <span className="font-mono">{formatTime(currentTime)}</span>
            <span className="text-xs text-gray-500 uppercase tracking-wider">
              {activeTrack === "master"
                ? "✨ Mastered"
                : activeTrack === "mix"
                ? "🎚️ Mix"
                : "📁 Original"}
            </span>
            <span className="font-mono">{formatTime(duration)}</span>
          </div>

          {/* Main controls */}
          <div className="flex items-center justify-center gap-6">
            <button
              onClick={skipBack}
              className="p-3 rounded-full hover:bg-white/5 transition-colors text-gray-400 hover:text-white"
              title="Skip 10s back"
            >
              <SkipBack className="w-5 h-5" />
            </button>

            <button
              onClick={togglePlay}
              className="w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center hover:scale-105 active:scale-95 transition-transform shadow-lg shadow-purple-500/30"
            >
              {isPlaying ? (
                <Pause className="w-7 h-7 text-white" />
              ) : (
                <Play className="w-7 h-7 text-white ml-1" />
              )}
            </button>

            <button
              onClick={skipForward}
              className="p-3 rounded-full hover:bg-white/5 transition-colors text-gray-400 hover:text-white"
              title="Skip 10s forward"
            >
              <SkipForward className="w-5 h-5" />
            </button>
          </div>

          {/* Secondary controls */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-white/5">
            {/* Volume */}
            <div className="flex items-center gap-3">
              <button
                onClick={toggleMute}
                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
              >
                {isMuted || volume === 0 ? (
                  <VolumeX className="w-5 h-5 text-gray-400" />
                ) : (
                  <Volume2 className="w-5 h-5 text-gray-300" />
                )}
              </button>
              <div className="w-24 h-1 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-white/50 rounded-full"
                  style={{ width: `${(isMuted ? 0 : volume) * 100}%` }}
                ></div>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.01}
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="absolute w-24 h-4 opacity-0 cursor-pointer"
                style={{ marginLeft: 40 }}
              />
            </div>

            {/* Loop & Download */}
            <div className="flex items-center gap-2">
              <button
                onClick={toggleLoop}
                className={`p-2 rounded-lg transition-all ${
                  isLooping
                    ? "bg-purple-500/20 text-purple-400"
                    : "hover:bg-white/5 text-gray-400"
                }`}
                title="Toggle loop (L)"
              >
                <Repeat className="w-5 h-5" />
              </button>

              {onDownloadMaster && (
                <button
                  onClick={onDownloadMaster}
                  className="p-2 rounded-lg hover:bg-white/5 transition-colors text-gray-400 hover:text-white"
                  title="Download"
                >
                  <Download className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>

          {/* Keyboard shortcuts hint */}
          <div className="mt-4 flex items-center justify-center gap-4 text-xs text-gray-600">
            <span>
              <kbd className="px-1.5 py-0.5 bg-white/5 rounded">Space</kbd> Play
            </span>
            {originalUrl && (
              <span>
                <kbd className="px-1.5 py-0.5 bg-white/5 rounded">A</kbd>{" "}
                Original
              </span>
            )}
            <span>
              <kbd className="px-1.5 py-0.5 bg-white/5 rounded">B</kbd> Master
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 bg-white/5 rounded">L</kbd> Loop
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
