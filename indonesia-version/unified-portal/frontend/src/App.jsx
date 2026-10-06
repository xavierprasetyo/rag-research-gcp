import React, { useState, useEffect } from 'react';
import {
  Layers,
  Database,
  Search,
  Bot,
  Cpu,
  Home as HomeIcon,
  Globe,
  Shield,
  Activity,
  FileText,
} from 'lucide-react';

import Home from './pages/Home.jsx';
import ScenarioView from './pages/ScenarioView.jsx';
import Scenario5View from './pages/Scenario5View.jsx';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [corpus, setCorpus] = useState('id'); // 'id' or 'en'
  const [overviewData, setOverviewData] = useState(null);

  useEffect(() => {
    fetch(`/api/overview?corpus=${corpus}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setOverviewData(data))
      .catch(() => {});
  }, [corpus]);

  const navItems = [
    { id: 'home', label: 'Overview & Matrix', icon: HomeIcon },
    { id: 's1', label: '1. Vector Search 1.0', icon: Database, badge: 'Dedicated' },
    { id: 's2', label: '2. Agent Retrieval', icon: Layers, badge: 'Serverless' },
    { id: 's3', label: '3. RAG Engine', icon: FileText, badge: 'Managed' },
    { id: 's4', label: '4. Agent Search', icon: Search, badge: 'Turnkey' },
    { id: 's5', label: '5. Agent ADK', icon: Bot, badge: 'Agentic' },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#0b0f19] text-slate-100">
      {/* Top Banner & Header */}
      <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-4">
            {/* Logo */}
            <button
              onClick={() => setActiveTab('home')}
              className="flex items-center gap-3 text-left group"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="font-extrabold text-sm sm:text-base text-white tracking-tight flex items-center gap-2">
                  Cymbal HR FAQ Portal
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono">
                    5 Architectures
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">Google Cloud Architecture & Retrieval Benchmark</div>
              </div>
            </button>

            {/* Document Corpus Switcher Toggle & Environment Badges */}
            <div className="flex items-center gap-3 font-mono text-[11px]">
              {/* Corpus Switcher */}
              <div className="flex items-center bg-slate-800/90 p-1 rounded-xl border border-slate-700 shadow-inner">
                <button
                  onClick={() => setCorpus('id')}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                    corpus === 'id'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  title="Switch to Indonesian HR Policy Documents & Queries"
                >
                  <span className="text-sm">🇮🇩</span>
                  <span className="font-sans">ID Documents</span>
                </button>
                <button
                  onClick={() => setCorpus('en')}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                    corpus === 'en'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  title="Switch to Global / English HR Policy Documents & Queries"
                >
                  <span className="text-sm">🇺🇸</span>
                  <span className="font-sans">EN Documents</span>
                </button>
              </div>

              <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-slate-300">
                <Shield className="w-3.5 h-3.5 text-indigo-400" />
                rag-research-sandbox
              </div>
            </div>
          </div>

          {/* Navigation Bar */}
          <nav className="flex space-x-1 overflow-x-auto py-2 border-t border-slate-800/80 no-scrollbar">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                  {item.badge && (
                    <span
                      className={`text-[9px] px-1.5 py-0.2 rounded font-mono ${
                        isActive
                          ? 'bg-indigo-800 text-indigo-200'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Main Page Body */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {activeTab === 'home' && (
          <Home
            onSelectScenario={setActiveTab}
            overviewData={overviewData}
            corpus={corpus}
            setCorpus={setCorpus}
          />
        )}

        {activeTab === 's1' && (
          <ScenarioView
            scenarioId="s1"
            title="Scenario 1: Vector Search 1.0"
            subtitle="Dedicated ANN Index (Vertex ScaNN) + Firestore Text Chunk Payload"
            badge="Infrastructure Control"
            apiPrefix="/api/s1"
            corpus={corpus}
          />
        )}

        {activeTab === 's2' && (
          <ScenarioView
            scenarioId="s2"
            title="Scenario 2: Agent Retrieval"
            subtitle="Serverless Vector Collections + Reciprocal Rank Fusion Hybrid Search"
            badge="Serverless & Hybrid"
            apiPrefix="/api/s2"
            corpus={corpus}
          />
        )}

        {activeTab === 's3' && (
          <ScenarioView
            scenarioId="s3"
            title="Scenario 3: RAG Engine"
            subtitle="Managed RagCorpus Ingestion + VertexRagStore Native Grounding Tool"
            badge="Enterprise Document RAG"
            apiPrefix="/api/s3"
            corpus={corpus}
          />
        )}

        {activeTab === 's4' && (
          <ScenarioView
            scenarioId="s4"
            title="Scenario 4: Agent Search (Search API)"
            subtitle="Discovery Engine Turnkey Search & Answer with Grounded Citations"
            badge="Turnkey Search"
            apiPrefix="/api/s4"
            corpus={corpus}
          />
        )}

        {activeTab === 's5' && <Scenario5View corpus={corpus} />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950/60 py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            © 2026 Cymbal HR Systems • Google Cloud Architecture & Retrieval Benchmark
          </div>
          <div className="flex items-center gap-4 font-mono text-[11px]">
            <span>Active Corpus: <span className="text-indigo-400 font-bold">{corpus.toUpperCase()}</span></span>
            <span>API Docs: <a href="/docs" target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">/docs</a></span>
          </div>
        </div>
      </footer>
    </div>
  );
}

