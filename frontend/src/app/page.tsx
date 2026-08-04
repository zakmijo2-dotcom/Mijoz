"use client";

import { useState } from "react";

export default function Home() {
  const [selectedAgent, setSelectedAgent] = useState("claude_code");

  const agents = [
    { id: "claude_code", name: "Claude Code", icon: "🤖" },
    { id: "codex", name: "Codex", icon: "💻" },
    { id: "opencode", name: "OpenCode", icon: "🔓" },
    { id: "pi_agent", name: "Pi Agent", icon: "🧠" },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-foreground">
            🚀 Unified AI Agents Platform
          </h1>
          <nav className="flex gap-4">
            <a href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground">
              Dashboard
            </a>
            <a href="/providers" className="text-sm text-muted-foreground hover:text-foreground">
              Providers
            </a>
            <a href="/projects" className="text-sm text-muted-foreground hover:text-foreground">
              Projects
            </a>
            <a href="/settings" className="text-sm text-muted-foreground hover:text-foreground">
              Settings
            </a>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Agent Selection */}
          <aside className="lg:col-span-1 space-y-4">
            <div className="bg-card rounded-lg border p-4">
              <h2 className="text-lg font-semibold mb-4">Select Agent</h2>
              <div className="space-y-2">
                {agents.map((agent) => (
                  <button
                    key={agent.id}
                    onClick={() => setSelectedAgent(agent.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-md transition-colors ${
                      selectedAgent === agent.id
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted hover:bg-accent"
                    }`}
                  >
                    <span className="text-xl">{agent.icon}</span>
                    <span className="font-medium">{agent.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Provider Status */}
            <div className="bg-card rounded-lg border p-4">
              <h2 className="text-lg font-semibold mb-4">Active Providers</h2>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span>Groq</span>
                  <span className="text-green-500">● Active</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>OpenRouter</span>
                  <span className="text-green-500">● Active</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Together AI</span>
                  <span className="text-yellow-500">● Rate Limited</span>
                </div>
              </div>
            </div>
          </aside>

          {/* Main Editor Area */}
          <section className="lg:col-span-3 space-y-4">
            {/* Toolbar */}
            <div className="bg-card rounded-lg border p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <select className="bg-background border rounded-md px-3 py-2 text-sm">
                  <option>llama-3.1-70b-versatile (Groq)</option>
                  <option>mixtral-8x7b (OpenRouter)</option>
                  <option>gemini-pro (Google AI)</option>
                </select>
                <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90">
                  Run Agent
                </button>
              </div>
              <div className="flex items-center gap-2">
                <button className="p-2 hover:bg-accent rounded-md">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                </button>
                <button className="p-2 hover:bg-accent rounded-md">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Code Editor Placeholder */}
            <div className="bg-card rounded-lg border overflow-hidden">
              <div className="border-b px-4 py-2 bg-muted flex items-center justify-between">
                <span className="text-sm font-medium">editor.py</span>
                <span className="text-xs text-muted-foreground">Python</span>
              </div>
              <div className="p-4 font-mono text-sm min-h-[400px] bg-background">
                <pre className="text-muted-foreground">
{`# Welcome to the Unified AI Agents Platform!
# Select an agent and start coding.

def main():
    print("Hello, AI Assistant!")
    
if __name__ == "__main__":
    main()`}
                </pre>
              </div>
            </div>

            {/* Terminal Placeholder */}
            <div className="bg-card rounded-lg border overflow-hidden">
              <div className="border-b px-4 py-2 bg-muted">
                <span className="text-sm font-medium">Terminal</span>
              </div>
              <div className="p-4 font-mono text-sm h-48 bg-black text-green-400">
                <pre>{`$ python editor.py
Hello, AI Assistant!
$ `}</pre>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
