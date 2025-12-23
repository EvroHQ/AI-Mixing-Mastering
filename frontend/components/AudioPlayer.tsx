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
  ToggleLeft,
  ToggleRight,
} from "lucide-react";

interface AudioPlayerProps {
  masterUrl: string;
  originalUrl?: string;
  title?: string;
}

export default function AudioPlayer({
  masterUrl,
  originalUrl,
  title = "Your Master",
}: AudioPlayerProps) {
  // Audio state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [isLooping, setIsLooping] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // A/B comparison state
  const [activeTrack, setActiveTrack] = useState<"master" | "original">(
    "master"
  );
  const [hasOriginal, setHasOriginal] = useState(false);

  // Howl instances
  const masterHowl = useRef<Howl | null>(null);
  const originalHowl = useRef<Howl | null>(null);
  const animationRef = useRef<number | null>(null);

  // Initialize Howler instances
  useEffect(() => {
    // Create master audio
    masterHowl.current = new Howl({
      src: [masterUrl],
      html5: true, // Streaming for large files
      volume: volume,
      loop: isLooping,
      onload: () => {
        setDuration(masterHowl.current?.duration() || 0);
        setIsLoading(false);
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
      onloaderror: (id, error) => {
        console.error("Error loading audio:", error);
        setIsLoading(false);
      },
    });

    // Create original audio if provided
    if (originalUrl) {
      setHasOriginal(true);
      originalHowl.current = new Howl({
        src: [originalUrl],
        html5: true,
        volume: volume,
        loop: isLooping,
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
    }

    return () => {
      masterHowl.current?.unload();
      originalHowl.current?.unload();
      stopProgressAnimation();
    };
  }, [masterUrl, originalUrl]);

  // Update volume on both tracks
  useEffect(() => {
    const actualVolume = isMuted ? 0 : volume;
    masterHowl.current?.volume(actualVolume);
    originalHowl.current?.volume(actualVolume);
  }, [volume, isMuted]);

  // Update loop on both tracks
  useEffect(() => {
    masterHowl.current?.loop(isLooping);
    originalHowl.current?.loop(isLooping);
  }, [isLooping]);

  // Progress animation
  const startProgressAnimation = useCallback(() => {
    const animate = () => {
      const activeHowl =
        activeTrack === "master" ? masterHowl.current : originalHowl.current;
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
    const activeHowl =
      activeTrack === "master" ? masterHowl.current : originalHowl.current;
    if (!activeHowl) return;

    if (isPlaying) {
      activeHowl.pause();
    } else {
      activeHowl.play();
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);

    const activeHowl =
      activeTrack === "master" ? masterHowl.current : originalHowl.current;
    activeHowl?.seek(time);
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
    const activeHowl =
      activeTrack === "master" ? masterHowl.current : originalHowl.current;
    if (activeHowl) {
      const newTime = Math.max(0, currentTime - 10);
      activeHowl.seek(newTime);
      setCurrentTime(newTime);
    }
  };

  const skipForward = () => {
    const activeHowl =
      activeTrack === "master" ? masterHowl.current : originalHowl.current;
    if (activeHowl) {
      const newTime = Math.min(duration, currentTime + 10);
      activeHowl.seek(newTime);
      setCurrentTime(newTime);
    }
  };

  // A/B Switch with seamless crossfade
  const switchTrack = (track: "master" | "original") => {
    if (!hasOriginal || track === activeTrack) return;

    const currentHowl =
      activeTrack === "master" ? masterHowl.current : originalHowl.current;
    const newHowl =
      track === "master" ? masterHowl.current : originalHowl.current;

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

  return (
    <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-2xl border border-white/10 p-6">
      {/* Title & A/B Toggle */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold">{title}</h3>

        {hasOriginal && (
          <div className="flex items-center gap-2 bg-white/5 rounded-full p-1">
            <button
              onClick={() => switchTrack("original")}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                activeTrack === "original"
                  ? "bg-white text-black"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Original
            </button>
            <button
              onClick={() => switchTrack("master")}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                activeTrack === "master"
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Master
            </button>
          </div>
        )}
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
          <span className="ml-3 text-gray-400">Loading audio...</span>
        </div>
      )}

      {/* Player controls */}
      {!isLoading && (
        <>
          {/* Waveform/Progress bar */}
          <div className="mb-6">
            <div className="relative h-12 bg-white/5 rounded-xl overflow-hidden group">
              {/* Progress fill */}
              <div
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500/50 to-pink-500/50"
                style={{ width: `${(currentTime / duration) * 100}%` }}
              ></div>

              {/* Seek input */}
              <input
                type="range"
                min={0}
                max={duration || 100}
                value={currentTime}
                onChange={handleSeek}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />

              {/* Playhead */}
              <div
                className="absolute top-0 bottom-0 w-1 bg-white shadow-lg transition-opacity group-hover:opacity-100 opacity-70"
                style={{ left: `${(currentTime / duration) * 100}%` }}
              ></div>
            </div>

            {/* Time display */}
            <div className="flex justify-between text-sm text-gray-400 mt-2">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>

          {/* Main controls */}
          <div className="flex items-center justify-center gap-4">
            {/* Skip back */}
            <button
              onClick={skipBack}
              className="p-3 rounded-full hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
              title="Skip 10s back"
            >
              <SkipBack className="w-5 h-5" />
            </button>

            {/* Play/Pause */}
            <button
              onClick={togglePlay}
              className="w-14 h-14 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center hover:scale-105 transition-transform shadow-lg shadow-purple-500/25"
            >
              {isPlaying ? (
                <Pause className="w-6 h-6 text-white" />
              ) : (
                <Play className="w-6 h-6 text-white ml-1" />
              )}
            </button>

            {/* Skip forward */}
            <button
              onClick={skipForward}
              className="p-3 rounded-full hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
              title="Skip 10s forward"
            >
              <SkipForward className="w-5 h-5" />
            </button>
          </div>

          {/* Secondary controls */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-white/10">
            {/* Volume */}
            <div className="flex items-center gap-3">
              <button
                onClick={toggleMute}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                {isMuted || volume === 0 ? (
                  <VolumeX className="w-5 h-5 text-gray-400" />
                ) : (
                  <Volume2 className="w-5 h-5" />
                )}
              </button>
              <input
                type="range"
                min={0}
                max={1}
                step={0.01}
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-24 h-1 bg-white/20 rounded-full appearance-none cursor-pointer
                  [&::-webkit-slider-thumb]:appearance-none
                  [&::-webkit-slider-thumb]:w-3
                  [&::-webkit-slider-thumb]:h-3
                  [&::-webkit-slider-thumb]:rounded-full
                  [&::-webkit-slider-thumb]:bg-white"
              />
            </div>

            {/* Loop toggle */}
            <button
              onClick={toggleLoop}
              className={`p-2 rounded-lg transition-colors ${
                isLooping
                  ? "bg-purple-500/20 text-purple-400"
                  : "hover:bg-white/10 text-gray-400"
              }`}
              title="Toggle loop"
            >
              <Repeat className="w-5 h-5" />
            </button>
          </div>

          {/* A/B Quick toggle (keyboard hint) */}
          {hasOriginal && (
            <div className="mt-4 text-center text-xs text-gray-500">
              Press <kbd className="px-2 py-1 bg-white/10 rounded">A</kbd> for
              Original •
              <kbd className="px-2 py-1 bg-white/10 rounded ml-2">B</kbd> for
              Master
            </div>
          )}
        </>
      )}
    </div>
  );
}
