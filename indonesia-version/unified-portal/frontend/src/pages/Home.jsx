import React, { useState, useEffect } from 'react';
import {
  Layers,
  Cpu,
  Server,
  Database,
  Search,
  Bot,
  Zap,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ArrowRight,
  ShieldCheck,
  Code2,
  DollarSign,
  Activity,
  FileText,
  Sparkles,
} from 'lucide-react';
import GenerativeSearchArchitecture from '../components/GenerativeSearchArchitecture';


export default function Home({ onSelectScenario, overviewData, corpus, setCorpus }) {
  const [healthStatus, setHealthStatus] = useState({
    s1: null,
    s2: null,
    s3: null,
    s4: null,
    s5: null,
  });

  useEffect(() => {
    // Check health for all 5 scenarios
    ['s1', 's2', 's3', 's4', 's5'].forEach((s) => {
      fetch(`/api/${s}/health`)
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          setHealthStatus((prev) => ({
            ...prev,
            [s]: data && (data.status === 'online' || data.status === 'healthy'),
          }));
        })
        .catch(() => {
          setHealthStatus((prev) => ({ ...prev, [s]: false }));
        });
    });
  }, []);

  const scenarios = overviewData?.scenarios || [];
  const goldenQueries = overviewData?.golden_queries || [];

  return (
    <div className="space-y-12 pb-16">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 p-8 md:p-12 shadow-2xl">
        <div className="max-w-4xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold tracking-wide uppercase">
            <Sparkles className="w-3.5 h-3.5" />
            Google Cloud Retrieval Benchmark • Enterprise Architecture Comparison
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
            5 Retrieval & Search Architectures on Google Cloud
          </h1>
          <p className="text-slate-300 text-base md:text-lg leading-relaxed">
            Comparative analysis from pure infrastructure control (<em>Vector Search 1.0</em>) to autonomous multi-tool reasoning agents (<em>Google ADK + Agent Search</em>), benchmarked live against real-world enterprise HR policy case studies.
          </p>

          <div className="pt-2 flex flex-wrap gap-4 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Project: <span className="text-slate-200">rag-research-sandbox</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700">
              Region: <span className="text-slate-200">us-central1 / global</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700">
              Active Corpus: <span className="text-indigo-300 font-semibold">{corpus === 'en' ? 'Global English HR Policies (10 Master Policies)' : 'Indonesian HR Policies (10 Master Policies)'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* GCP Live Resource Status Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {[
          { id: 's1', name: 'S1: Vector Search 1.0', type: 'Dedicated ANN + Firestore' },
          { id: 's2', name: 'S2: Agent Retrieval', type: 'Serverless Collections' },
          { id: 's3', name: 'S3: RAG Engine', type: 'Managed File Corpus' },
          { id: 's4', name: 'S4: Agent Search API', type: 'Turnkey Search & Answer' },
          { id: 's5', name: 'S5: Agent ADK', type: 'Multi-Tool Reasoning' },
        ].map((item) => {
          const isUp = healthStatus[item.id];
          return (
            <button
              key={item.id}
              onClick={() => onSelectScenario(item.id)}
              className="text-left p-3.5 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60 hover:border-indigo-500/50 transition-all group cursor-pointer"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-semibold text-xs text-slate-200 group-hover:text-indigo-400 transition-colors">
                  {item.name}
                </span>
                <span
                  className={`w-2 h-2 rounded-full ${
                    isUp === true
                      ? 'bg-emerald-400 shadow-sm shadow-emerald-500/50'
                      : isUp === false
                      ? 'bg-amber-400'
                      : 'bg-slate-600 animate-pulse'
                  }`}
                />
              </div>
              <div className="text-[11px] text-slate-400 truncate">{item.type}</div>
            </button>
          );
        })}
      </div>

      {/* Section 1: Visual Architecture Pipeline (Steps of Modern Generative Search) */}
      <GenerativeSearchArchitecture onSelectScenario={onSelectScenario} />

      {/* Section 2: What Google Manages vs What Customer Controls */}
      <div className="space-y-6">
        <div className="border-b border-slate-800 pb-4">
          <h2 className="text-xl md:text-2xl font-bold text-white flex items-center gap-2.5">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            Division of Responsibility: Google Managed vs. Customer Built
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Transparently inspect which components are managed automatically by Google Cloud vs. what requires engineering effort from your developers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {scenarios.map((sc) => (
            <div
              key={sc.id}
              className="rounded-2xl bg-slate-800/40 border border-slate-700/70 p-5 space-y-4 flex flex-col justify-between hover:border-slate-600 transition-all"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-700/60 text-slate-300">
                    {sc.name}
                  </span>
                  <span className="text-[11px] font-medium text-slate-400">{sc.badge}</span>
                </div>
                <h3 className="font-semibold text-slate-100 text-sm">{sc.subtitle}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{sc.description}</p>

                {/* Google Managed List */}
                <div className="pt-2">
                  <div className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Managed by Google
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {sc.managed_by_google.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-emerald-500 font-bold mt-0.5">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Customer Controls List */}
                <div className="pt-2">
                  <div className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Code2 className="w-3.5 h-3.5" /> Customer Built / Controlled
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {sc.customer_controls.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-indigo-400 font-bold mt-0.5">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-700/50">
                <button
                  onClick={() => onSelectScenario(sc.id)}
                  className="w-full py-2 px-3 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  Test {sc.name} <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 3: Comprehensive Trade-off Matrix */}
      <div className="space-y-6">
        <div className="border-b border-slate-800 pb-4">
          <h2 className="text-xl md:text-2xl font-bold text-white flex items-center gap-2.5">
            <DollarSign className="w-6 h-6 text-amber-400" />
            Architectural Decision Trade-off Matrix
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Comparative decision framework based on developer effort, latency profile, cost model, fine-grained control, and multi-tool agentic capabilities.
          </p>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-slate-700/80 bg-slate-800/30">
          <table className="w-full text-left text-xs text-slate-300 min-w-[700px]">
            <thead className="bg-slate-800/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-700">
              <tr>
                <th className="py-3 px-4 font-semibold text-slate-200">Scenario</th>
                <th className="py-3 px-4 font-semibold text-slate-200">Developer Effort</th>
                <th className="py-3 px-4 font-semibold text-slate-200">Latency Profile</th>
                <th className="py-3 px-4 font-semibold text-slate-200">Cost Model</th>
                <th className="py-3 px-4 font-semibold text-slate-200">Internal Control</th>
                <th className="py-3 px-4 font-semibold text-slate-200">Multi-Tool / Agent Support</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/60">
              {scenarios.map((sc) => (
                <tr key={sc.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="py-3.5 px-4 font-medium text-white whitespace-nowrap">
                    <div className="font-semibold">{sc.name}</div>
                    <div className="text-[11px] text-slate-400">{sc.badge}</div>
                  </td>
                  <td className="py-3.5 px-4">{sc.tradeoffs.developer_effort}</td>
                  <td className="py-3.5 px-4">{sc.tradeoffs.latency_profile}</td>
                  <td className="py-3.5 px-4">{sc.tradeoffs.cost_model}</td>
                  <td className="py-3.5 px-4">{sc.tradeoffs.fine_grained_control}</td>
                  <td className="py-3.5 px-4">{sc.tradeoffs.multitool_agentic}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 4: Golden Query Capability Showcase */}
      <div className="space-y-6">
        <div className="border-b border-slate-800 pb-4">
          <h2 className="text-xl md:text-2xl font-bold text-white flex items-center gap-2.5">
            <Activity className="w-6 h-6 text-purple-400" />
            Enterprise Golden Queries & Benchmark ({goldenQueries.length} Scenarios • {corpus === 'en' ? 'Global English Policies' : 'Indonesian Policies'})
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Curated evaluation queries testing semantic search, multi-column tables, codes, hybrid regulations, and agentic calculations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {goldenQueries.map((gq) => (
            <div key={gq.id} className="rounded-2xl bg-slate-800/40 border border-slate-700 p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {gq.id} • {gq.category}
                </span>
                <span className="text-[11px] text-slate-400 font-mono truncate max-w-[200px]">
                  {gq.source_doc}
                </span>
              </div>
              <h3 className="font-semibold text-slate-100 text-sm">"{gq.query}"</h3>
              <p className="text-xs text-emerald-400 bg-emerald-950/30 p-2.5 rounded-lg border border-emerald-500/20">
                <span className="font-semibold">Official Ground Truth:</span> {gq.solution}
              </p>

              {/* Suitability per scenario */}
              <div className="pt-2 border-t border-slate-700/60 space-y-1.5 text-xs">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Scenario Suitability Analysis:
                </div>
                {scenarios.map((sc) => (
                  <div key={sc.id} className="flex items-center justify-between py-0.5">
                    <span className="text-slate-300 font-medium">{sc.name}:</span>
                    <span className="text-slate-400 text-right">{sc.golden_query_fit[gq.id] || 'Compatible'}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 5: Enterprise Document Corpus Library */}
      <div className="space-y-6">
        <div className="border-b border-slate-800 pb-4">
          <h2 className="text-xl md:text-2xl font-bold text-white flex items-center gap-2.5">
            <FileText className="w-6 h-6 text-indigo-400" />
            Enterprise HR Policy Corpus Library (10 Master Documents)
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Complete set of active policy documents indexed across all 5 search backends in Google Cloud.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {(overviewData?.documents || []).map((doc, idx) => (
            <div
              key={doc.filename}
              className="rounded-2xl bg-slate-800/40 border border-slate-700/80 p-5 space-y-3 flex flex-col justify-between hover:border-indigo-500/50 transition-all"
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    Doc #{idx + 1} • {doc.code}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">PDF Document</span>
                </div>
                <h3 className="font-semibold text-slate-100 text-sm leading-snug">
                  {doc.title}
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {doc.description}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-700/60">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">Benchmark Target:</span>
                  <span className="font-medium text-emerald-400 truncate max-w-[180px]">
                    {doc.test_target}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

