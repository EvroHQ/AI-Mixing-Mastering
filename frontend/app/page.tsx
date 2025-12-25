import Link from "next/link";
import {
  Music2,
  Sparkles,
  Zap,
  Shield,
  Clock,
  TrendingUp,
  ArrowRight,
  Play,
  Upload,
  AudioWaveform,
  Sliders,
  Download,
  Check,
  X,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen grid-background">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass">
        <nav className="container mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-white to-gray-400 flex items-center justify-center">
              <Music2 className="w-6 h-6 text-black" />
            </div>
            <span className="text-2xl font-bold tracking-tight">MixMaster</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <Link
              href="#features"
              className="text-sm font-medium text-gray-400 hover:text-white transition-colors"
            >
              Features
            </Link>
            <Link
              href="#pricing"
              className="text-sm font-medium text-gray-400 hover:text-white transition-colors"
            >
              Pricing
            </Link>
            <Link
              href="#how-it-works"
              className="text-sm font-medium text-gray-400 hover:text-white transition-colors"
            >
              How It Works
            </Link>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/studio"
              className="group relative p-[1px] rounded-lg overflow-hidden cursor-pointer hover:shadow-[0_0_20px_rgba(168,85,247,0.4)] transition-shadow duration-300"
            >
              {/* Animated gradient border */}
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 bg-[length:200%_100%] animate-gradient-x"></div>
              {/* Button content */}
              <div className="relative px-5 py-2 rounded-[7px] bg-black/90 backdrop-blur-sm flex items-center gap-2 group-hover:bg-black/70 transition-all">
                <span className="text-sm font-medium text-white">
                  Get Started
                </span>
                <ArrowRight className="w-4 h-4 text-purple-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="pt-40 pb-32 px-6 relative overflow-hidden">
        <div className="container mx-auto max-w-6xl relative z-10">
          <div className="text-center animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#0a0a0a] border border-white/10 mb-8">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-medium">
                AI-Powered Audio Processing
              </span>
            </div>

            <h1 className="text-7xl md:text-8xl font-bold mb-8 leading-none glow-text">
              Mixing & Mastering
              <br />
              <span className="text-gradient-accent">In Minutes</span>
            </h1>

            <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
              Upload your stems, and our platform will automatically process
              them, delivering a professional master ready for streaming
              platforms.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-20">
              {/* Start Mixing Button - Gradient */}
              <Link
                href="/studio"
                className="group relative px-8 py-4 rounded-xl overflow-hidden cursor-pointer"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 transition-opacity"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <span className="relative flex items-center justify-center gap-2 font-bold text-white">
                  <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                  Start now
                </span>
              </Link>

              {/* Watch Demo Button - Outline */}
              <button className="group relative px-8 py-4 rounded-xl border border-white/20 hover:border-purple-500/50 transition-all cursor-pointer overflow-hidden">
                <div className="absolute inset-0 bg-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <span className="relative flex items-center justify-center gap-2 font-bold text-gray-300 group-hover:text-white transition-colors">
                  <Play className="w-5 h-5 text-purple-400" />
                  Watch Demo
                </span>
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <div className="p-6 rounded-2xl bg-[#0a0a0a] border border-white/10 text-center hover:border-purple-500/20 transition-colors">
                <div className="text-4xl font-bold mb-1 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  2.5min
                </div>
                <div className="text-gray-500 text-xs font-medium uppercase tracking-wider">
                  Avg. Processing Time
                </div>
              </div>
              <div className="p-6 rounded-2xl bg-[#0a0a0a] border border-white/10 text-center hover:border-purple-500/20 transition-colors">
                <div className="text-4xl font-bold mb-1 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  -10 LUFS
                </div>
                <div className="text-gray-500 text-xs font-medium uppercase tracking-wider">
                  Streaming Standard
                </div>
              </div>
              <div className="p-6 rounded-2xl bg-[#0a0a0a] border border-white/10 text-center hover:border-purple-500/20 transition-colors">
                <div className="text-4xl font-bold mb-1 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  $6.99
                </div>
                <div className="text-gray-500 text-xs font-medium uppercase tracking-wider">
                  Per Download
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 px-6 relative z-10">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-bold mb-6">Professional Features</h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Everything you need to create studio-quality masters
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="card group hover:border-yellow-500/30 transition-all duration-500">
              <Zap className="w-8 h-8 text-yellow-400 mb-4" />
              <h3 className="text-xl font-bold mb-3">Lightning Fast</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Process 8 stems in under 3 minutes. Optimized pipeline with
                Essentia, Matchering, and custom DSP.
              </p>
            </div>

            <div className="card group hover:border-purple-500/30 transition-all duration-500">
              <Sparkles className="w-8 h-8 text-purple-400 mb-4" />
              <h3 className="text-xl font-bold mb-3">AI-Powered Analysis</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Automatic tempo, key, and genre detection. Smart EQ,
                compression, and spatial processing.
              </p>
            </div>

            <div className="card group hover:border-green-500/30 transition-all duration-500">
              <TrendingUp className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="text-xl font-bold mb-3">Streaming Ready</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Optimized for Spotify, Apple Music, YouTube. -9 to -14 LUFS with
                true-peak limiting.
              </p>
            </div>

            <div className="card group hover:border-blue-500/30 transition-all duration-500">
              <Shield className="w-8 h-8 text-blue-400 mb-4" />
              <h3 className="text-xl font-bold mb-3">Secure & Private</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Files encrypted and auto-deleted after 7 days. Your audio is
                never shared or used for training.
              </p>
            </div>

            <div className="card group hover:border-orange-500/30 transition-all duration-500">
              <Clock className="w-8 h-8 text-orange-400 mb-4" />
              <h3 className="text-xl font-bold mb-3">Real-Time Progress</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Live progress updates as your mix comes together. Preview
                before/after comparison.
              </p>
            </div>

            <div className="card group hover:border-pink-500/30 transition-all duration-500">
              <Music2 className="w-8 h-8 text-pink-400 mb-4" />
              <h3 className="text-xl font-bold mb-3">Studio Quality</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Industry-standard results. Neural EQ, adaptive compression, and
                reference-based mastering.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-32 px-6 relative z-10">
        <div className="container mx-auto max-w-6xl relative z-10">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-bold mb-6">How It Works</h2>
            <p className="text-xl text-gray-400">
              Four simple steps to professional audio
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center group">
              <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center mx-auto mb-4 group-hover:border-purple-500/30 transition-all">
                <Upload className="w-7 h-7 text-purple-400" />
              </div>
              <div className="text-xs text-purple-400 font-bold mb-2">
                STEP 1
              </div>
              <h3 className="text-lg font-bold mb-2">Upload Stems</h3>
              <p className="text-gray-500 text-sm">Drag and drop your tracks</p>
            </div>

            <div className="text-center group">
              <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center mx-auto mb-4 group-hover:border-blue-500/30 transition-all">
                <AudioWaveform className="w-7 h-7 text-blue-400" />
              </div>
              <div className="text-xs text-blue-400 font-bold mb-2">STEP 2</div>
              <h3 className="text-lg font-bold mb-2">AI Analysis</h3>
              <p className="text-gray-500 text-sm">Genre and audio detection</p>
            </div>

            <div className="text-center group">
              <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center mx-auto mb-4 group-hover:border-pink-500/30 transition-all">
                <Sliders className="w-7 h-7 text-pink-400" />
              </div>
              <div className="text-xs text-pink-400 font-bold mb-2">STEP 3</div>
              <h3 className="text-lg font-bold mb-2">Mix & Master</h3>
              <p className="text-gray-500 text-sm">Pro processing applied</p>
            </div>

            <div className="text-center group">
              <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center mx-auto mb-4 group-hover:border-green-500/30 transition-all">
                <Download className="w-7 h-7 text-green-400" />
              </div>
              <div className="text-xs text-green-400 font-bold mb-2">
                STEP 4
              </div>
              <h3 className="text-lg font-bold mb-2">Download</h3>
              <p className="text-gray-500 text-sm">Get your master</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-32 px-6 relative z-10">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-6">Simple Pricing</h2>
            <p className="text-xl text-gray-400">
              Choose the plan that works for you
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Free Tier */}
            <div className="bg-[#0a0a12] rounded-2xl border border-white/10 p-8 flex flex-col">
              <div className="text-center mb-8">
                <p className="text-gray-400 uppercase tracking-wider text-sm mb-4">
                  FREE
                </p>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-5xl font-bold bg-gradient-to-r from-gray-100 to-gray-400 bg-clip-text text-transparent">
                    $6.99
                  </span>
                </div>
                <p className="text-gray-500 mt-2">per download</p>
              </div>

              <div className="border-t border-white/10 pt-6 flex-grow">
                <ul className="space-y-4">
                  {[
                    { text: "12-track mixing & mastering", included: true },
                    { text: "1GB audio storage", included: true },
                    { text: "Pay per download", included: true },
                  ].map((feature, i) => (
                    <li key={i} className="flex items-center gap-3 text-sm">
                      {feature.included ? (
                        <Check className="w-4 h-4 text-purple-400 flex-shrink-0" />
                      ) : (
                        <X className="w-4 h-4 text-gray-600 flex-shrink-0" />
                      )}
                      <span
                        className={
                          feature.included ? "text-gray-300" : "text-gray-600"
                        }
                      >
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <Link
                href="/studio"
                className="mt-8 block w-full py-4 rounded-xl border border-white/20 text-center font-bold text-white hover:bg-white/5 transition-colors"
              >
                Get Started
              </Link>
            </div>

            {/* Pro Tier */}
            <div className="relative">
              <div className="absolute -top-3 right-6 px-4 py-1.5 rounded-md bg-gradient-to-r from-purple-500 to-pink-500 text-xs font-bold text-white uppercase tracking-wider z-10">
                Best Value
              </div>
              <div className="bg-[#0a0a12] rounded-2xl border border-purple-500/30 p-8 h-full flex flex-col">
                <div className="text-center mb-8">
                  <p className="text-gray-400 uppercase tracking-wider text-sm mb-4">
                    PRO
                  </p>
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-5xl font-bold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">
                      $12.99
                    </span>
                  </div>
                  <p className="text-gray-500 mt-2">per month</p>
                </div>

                <div className="border-t border-white/10 pt-6 flex-grow">
                  <ul className="space-y-4">
                    {[
                      { text: "32-track mixing & mastering", included: true },
                      { text: "5GB audio storage", included: true },
                      { text: "Unlimited downloads", included: true },
                      { text: "Download processed stems", included: true },
                    ].map((feature, i) => (
                      <li key={i} className="flex items-center gap-3 text-sm">
                        <Check className="w-4 h-4 text-purple-400 flex-shrink-0" />
                        <span className="text-gray-300">{feature.text}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button className="mt-8 w-full py-4 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 font-bold text-white hover:from-purple-500 hover:to-pink-500 transition-all cursor-pointer">
                  Get Pro
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

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
                    href="#features"
                    className="hover:text-white transition-colors"
                  >
                    Features
                  </Link>
                </li>
                <li>
                  <Link
                    href="#pricing"
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
