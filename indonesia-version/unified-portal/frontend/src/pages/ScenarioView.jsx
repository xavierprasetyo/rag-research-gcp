import React, { useState, useEffect } from 'react';
import {
  Search,
  Sparkles,
  Clock,
  Database,
  FileText,
  CheckCircle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Cpu,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';

export default function ScenarioView({ scenarioId, title, subtitle, badge, apiPrefix, corpus = 'id' }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState(scenarioId === 's2' ? 'hybrid' : scenarioId === 's3' ? 'tool' : 'default');
  const [goldenQueries, setGoldenQueries] = useState([]);
  const [statusData, setStatusData] = useState(null);
  const [benchmarkData, setBenchmarkData] = useState([]);
  const [showStatus, setShowStatus] = useState(false);
  const [showBenchmark, setShowBenchmark] = useState(false);

  useEffect(() => {
    // Reset state on scenario/corpus change
    setResult(null);
    setError(null);
    setQuery('');

    // Load golden queries for active corpus
    fetch(`${apiPrefix}/golden-queries?corpus=${corpus}`)
      .then((res) => (res.ok ? res.json() : { queries: [] }))
      .then((data) => setGoldenQueries(data.queries || []))
      .catch(() => {});

    // Load status
    fetch(`${apiPrefix}/status`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setStatusData(data))
      .catch(() => {});

    // Load benchmark
    fetch(`${apiPrefix}/benchmark`)
      .then((res) => (res.ok ? res.json() : { results: [] }))
      .then((data) => setBenchmarkData(data.results || []))
      .catch(() => {});
  }, [scenarioId, apiPrefix, corpus]);

  const handleQuery = async (queryText) => {
    const q = queryText || query;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const body = { query: q.trim(), top_k: 4, corpus };
    if (scenarioId === 's2') body.mode = mode;
    if (scenarioId === 's3') body.mode = mode;

    try {
      const res = await fetch(`${apiPrefix}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server returned HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to process query.');
    } finally {
      setLoading(false);
    }
  };

  const chunks = result?.chunks || result?.snippets || result?.retrieved_chunks || [];
  const execMode = result?.execution_mode || 'live_gcp';
  const isFallbackMode =
    execMode.toLowerCase().includes('fallback') || execMode.toLowerCase().includes('cache');

  return (
    <div className="space-y-8 pb-16">
      {/* Scenario Header */}
      <div className="rounded-2xl bg-slate-800/60 border border-slate-700/80 p-6 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {badge}
            </span>
            <span className="text-xs text-slate-400 font-mono">API: {apiPrefix}</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-700 font-mono text-indigo-300">
              Corpus: {corpus.toUpperCase()}
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">{title}</h1>
          <p className="text-sm text-slate-300">{subtitle}</p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <button
            onClick={() => setShowStatus(!showStatus)}
            className="px-3 py-1.5 rounded-lg bg-slate-700/60 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-600 transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            Backend Status
          </button>
          <button
            onClick={() => setShowBenchmark(!showBenchmark)}
            className="px-3 py-1.5 rounded-lg bg-slate-700/60 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-600 transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            Benchmark Data
          </button>
        </div>
      </div>

      {/* Backend Status Drawer */}
      {showStatus && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-700 space-y-3 text-xs font-mono">
          <div className="flex items-center justify-between text-slate-400 font-sans font-semibold">
            <span>GCP Backend Status Details ({scenarioId.toUpperCase()})</span>
            <button onClick={() => setShowStatus(false)} className="hover:text-white cursor-pointer">✕</button>
          </div>
          <pre className="p-3 rounded bg-slate-950 overflow-x-auto text-emerald-400 text-[11px] leading-relaxed">
            {JSON.stringify(statusData, null, 2) || 'Loading backend status...'}
          </pre>
        </div>
      )}

      {/* Benchmark Drawer */}
      {showBenchmark && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-700 space-y-3 text-xs">
          <div className="flex items-center justify-between text-slate-400 font-semibold">
            <span>Latest Golden Queries Evaluation Results ({scenarioId.toUpperCase()})</span>
            <button onClick={() => setShowBenchmark(false)} className="hover:text-white cursor-pointer">✕</button>
          </div>
          {benchmarkData && benchmarkData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border border-slate-800">
                <thead className="bg-slate-800 text-slate-300">
                  <tr>
                    <th className="p-2 border border-slate-700">ID</th>
                    <th className="p-2 border border-slate-700">Category</th>
                    <th className="p-2 border border-slate-700">Status</th>
                    <th className="p-2 border border-slate-700">Total Latency</th>
                    <th className="p-2 border border-slate-700">Retrieval</th>
                  </tr>
                </thead>
                <tbody>
                  {benchmarkData.map((b, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40">
                      <td className="p-2 border border-slate-800 font-bold">{b.id}</td>
                      <td className="p-2 border border-slate-800">{b.category}</td>
                      <td className="p-2 border border-slate-800 font-semibold text-emerald-400">{b.status}</td>
                      <td className="p-2 border border-slate-800">{b.total_ms ? `${b.total_ms.toFixed(1)} ms` : '—'}</td>
                      <td className="p-2 border border-slate-800">{b.retrieval_ms ? `${b.retrieval_ms.toFixed(1)} ms` : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-slate-400 italic">No eval_results.json found for this scenario yet.</div>
          )}
        </div>
      )}

      {/* Preset Golden Query Selector */}
      <div className="space-y-3">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          Select Golden Query Case Study ({corpus === 'en' ? 'Global English Policies' : 'Indonesian Policies'})
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {goldenQueries.map((gq) => (
            <button
              key={gq.id}
              onClick={() => {
                setQuery(gq.query);
                handleQuery(gq.query);
              }}
              className="p-3.5 rounded-xl bg-slate-800/40 hover:bg-slate-800 border border-slate-700/60 hover:border-indigo-500/50 text-left transition-all group flex flex-col justify-between cursor-pointer"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    {gq.id} • {gq.category}
                  </span>
                </div>
                <div className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors line-clamp-2">
                  {gq.title || gq.query}
                </div>
              </div>
              <div className="mt-2 text-[10px] text-slate-400 truncate font-mono">
                {gq.source_doc}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Query Bar & Controls */}
      <div className="p-4 rounded-2xl bg-slate-800/50 border border-slate-700 space-y-4">
        {/* Scenario-specific mode toggles */}
        {scenarioId === 's2' && (
          <div className="flex flex-wrap items-center gap-2 border-b border-slate-700/60 pb-3 text-xs">
            <span className="text-slate-400 font-medium mr-2">Search Mode:</span>
            {[
              { id: 'hybrid', label: 'Hybrid (Dense + BM25 RRF)' },
              { id: 'dense', label: 'Pure Semantic (Dense Only)' },
              { id: 'bm25', label: 'Pure Keyword (BM25 Only)' },
            ].map((m) => (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={`px-3 py-1 rounded-lg transition-colors cursor-pointer ${
                  mode === m.id
                    ? 'bg-emerald-600 text-white font-semibold'
                    : 'bg-slate-700/60 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
        )}

        {scenarioId === 's3' && (
          <div className="flex flex-wrap items-center gap-2 border-b border-slate-700/60 pb-3 text-xs">
            <span className="text-slate-400 font-medium mr-2">Execution Mode:</span>
            {[
              { id: 'tool', label: 'Native VertexRagStore Tool' },
              { id: 'retrieval_api', label: 'API rag.retrieval_query' },
            ].map((m) => (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={`px-3 py-1 rounded-lg transition-colors cursor-pointer ${
                  mode === m.id
                    ? 'bg-blue-600 text-white font-semibold'
                    : 'bg-slate-700/60 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
              placeholder="Ask an HR policy query in English or Indonesian..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all"
            />
          </div>

          <button
            onClick={() => handleQuery()}
            disabled={loading || !query.trim()}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-sm font-semibold text-white transition-all shadow-md shadow-indigo-600/30 flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed whitespace-nowrap"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Submit Query
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/50 text-rose-200 text-xs flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-rose-300">An Error Occurred:</div>
            <div>{error}</div>
          </div>
        </div>
      )}

      {/* Latency Breakdown Cards */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 uppercase font-semibold">Total Latency</div>
              <div className="text-lg font-bold text-white">
                {result.total_ms ? `${result.total_ms.toFixed(1)} ms` : '—'}
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 uppercase font-semibold">Retrieval Latency</div>
              <div className="text-lg font-bold text-slate-200">
                {result.retrieval_ms ? `${result.retrieval_ms.toFixed(1)} ms` : '—'}
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 uppercase font-semibold">LLM Generation Latency</div>
              <div className="text-lg font-bold text-slate-200">
                {result.generation_ms ? `${result.generation_ms.toFixed(1)} ms` : '—'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Answer Section */}
      {result && (
        <div className="rounded-2xl bg-slate-800/50 border border-slate-700 p-6 space-y-4 shadow-xl">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-700/70 pb-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              Synthesized Grounded Answer
            </h2>
            <div className="flex items-center gap-2.5">
              {isFallbackMode ? (
                <span
                  title={
                    result.fallback_reason
                      ? `Execution mode: ${execMode} (${result.fallback_reason})`
                      : `Execution mode: ${execMode} — Served via local cache or simulation fallback`
                  }
                  className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/40 flex items-center gap-1.5"
                >
                  <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                  Fallback / Local Cache Simulation ({execMode})
                </span>
              ) : (
                <span
                  title={`Execution mode: ${execMode} — Served live from Google Cloud endpoint`}
                  className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5"
                >
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  Live GCP Endpoint
                </span>
              )}
              {result.citations && (
                <span className="text-xs text-slate-400 font-mono">
                  {result.citations.length} Verified Citations
                </span>
              )}
            </div>
          </div>

          <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed whitespace-pre-wrap">
            {result.answer}
          </div>

          {result.citations && result.citations.length > 0 && (
            <div className="pt-4 border-t border-slate-700/60 space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Official Citation Sources:
              </div>
              <div className="flex flex-wrap gap-2">
                {result.citations.map((c, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded bg-slate-700/50 border border-slate-600 text-xs text-indigo-300 font-mono"
                  >
                    [{idx + 1}] {c.title || c.uri || c}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Retrieved Chunks / DataObjects Section */}
      {chunks && chunks.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <FileText className="w-4 h-4 text-indigo-400" />
            Retrieved Context Chunks (Top {chunks.length} Segments)
          </h3>

          <div className="grid grid-cols-1 gap-3">
            {chunks.map((chunk, idx) => {
              const titleText = chunk.doc_name || chunk.title || chunk.document || `Segment #${idx + 1}`;
              const scoreText = chunk.score !== undefined ? `Score: ${chunk.score.toFixed(4)}` : null;
              const pageText = chunk.page ? `Page ${chunk.page}` : null;
              const contentText = chunk.text || chunk.content || chunk.snippet || '';

              return (
                <div key={idx} className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/70 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-indigo-300 font-mono flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5" />
                      {titleText} {pageText && <span className="text-slate-400">({pageText})</span>}
                    </span>
                    {scoreText && (
                      <span className="px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-mono text-[11px]">
                        {scoreText}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                    {contentText}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
