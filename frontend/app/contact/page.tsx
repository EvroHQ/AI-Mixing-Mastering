"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Music2,
  ArrowLeft,
  Mail,
  MessageSquare,
  Send,
  CheckCircle2,
} from "lucide-react";

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate form submission
    await new Promise((resolve) => setTimeout(resolve, 1500));

    setIsSubmitting(false);
    setIsSubmitted(true);
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen grid-background">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass">
        <nav className="container mx-auto px-6 py-5 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-white to-gray-400 flex items-center justify-center">
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
      <main className="pt-32 pb-16 px-6">
        <div className="container mx-auto max-w-4xl">
          {/* Title */}
          <div className="text-center mb-16 animate-fade-in">
            <h1 className="text-5xl font-bold mb-6 glow-text">
              Get in <span className="text-gradient-accent">Touch</span>
            </h1>
            <p className="text-xl text-gray-400">
              Have a question or feedback? We&apos;d love to hear from you.
            </p>
          </div>

          {isSubmitted ? (
            /* Success Message */
            <div className="animate-fade-in">
              <div className="card glow text-center py-16">
                <div className="w-20 h-20 mx-auto rounded-full bg-green-500/20 flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-10 h-10 text-green-500" />
                </div>
                <h2 className="text-3xl font-bold mb-4">Message Sent!</h2>
                <p className="text-gray-400 mb-8 max-w-md mx-auto">
                  Thank you for reaching out. We&apos;ll get back to you as soon
                  as possible.
                </p>
                <Link href="/" className="btn btn-primary">
                  Back to Home
                </Link>
              </div>
            </div>
          ) : (
            /* Contact Form */
            <div className="grid md:grid-cols-3 gap-8">
              {/* Contact Info */}
              <div className="space-y-6">
                <div className="card">
                  <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-4">
                    <Mail className="w-6 h-6 text-purple-400" />
                  </div>
                  <h3 className="font-bold mb-2">Email Us</h3>
                  <p className="text-gray-400 text-sm">
                    support@mixmaster.studio
                  </p>
                </div>

                <div className="card">
                  <div className="w-12 h-12 rounded-xl bg-pink-500/10 flex items-center justify-center mb-4">
                    <MessageSquare className="w-6 h-6 text-pink-400" />
                  </div>
                  <h3 className="font-bold mb-2">Response Time</h3>
                  <p className="text-gray-400 text-sm">
                    We typically respond within 24 hours
                  </p>
                </div>
              </div>

              {/* Form */}
              <div className="md:col-span-2">
                <form onSubmit={handleSubmit} className="card">
                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div>
                      <label
                        htmlFor="name"
                        className="block text-sm font-medium text-gray-400 mb-2"
                      >
                        Your Name
                      </label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-purple-500/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-white placeholder-gray-500"
                        placeholder="John Doe"
                      />
                    </div>
                    <div>
                      <label
                        htmlFor="email"
                        className="block text-sm font-medium text-gray-400 mb-2"
                      >
                        Email Address
                      </label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-purple-500/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-white placeholder-gray-500"
                        placeholder="john@example.com"
                      />
                    </div>
                  </div>

                  <div className="mb-6">
                    <label
                      htmlFor="subject"
                      className="block text-sm font-medium text-gray-400 mb-2"
                    >
                      Subject
                    </label>
                    <select
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-purple-500/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-white cursor-pointer"
                    >
                      <option value="" className="bg-black">
                        Select a subject
                      </option>
                      <option value="general" className="bg-black">
                        General Inquiry
                      </option>
                      <option value="support" className="bg-black">
                        Technical Support
                      </option>
                      <option value="billing" className="bg-black">
                        Billing Question
                      </option>
                      <option value="feedback" className="bg-black">
                        Feedback
                      </option>
                      <option value="partnership" className="bg-black">
                        Partnership
                      </option>
                    </select>
                  </div>

                  <div className="mb-6">
                    <label
                      htmlFor="message"
                      className="block text-sm font-medium text-gray-400 mb-2"
                    >
                      Message
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      required
                      rows={6}
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-purple-500/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 transition-all text-white placeholder-gray-500 resize-none"
                      placeholder="Tell us how we can help..."
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="group w-full relative px-8 py-4 rounded-xl overflow-hidden cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 transition-opacity"></div>
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <span className="relative flex items-center justify-center gap-2 font-bold text-white">
                      {isSubmitting ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                          Sending...
                        </>
                      ) : (
                        <>
                          <Send className="w-5 h-5" />
                          Send Message
                        </>
                      )}
                    </span>
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-16 px-6 border-t border-white/10">
        <div className="container mx-auto max-w-6xl">
          <div className="border-t border-white/10 pt-8 text-center text-gray-500 text-sm">
            <p>© 2025 MixMaster Studio. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
