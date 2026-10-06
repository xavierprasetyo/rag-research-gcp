import React, { useState, useEffect } from 'react';
import {
  Bot,
  Sparkles,
  Clock,
  Database,
  FileText,
  User,
  CheckCircle2,
  AlertCircle,
  Cpu,
  RefreshCw,
  Search,
  ArrowRight,
  Terminal,
  Activity,
  Layers,
  ChevronRight,
  Calculator,
} from 'lucide-react';

export default function Scenario5View({ corpus = 'id' }) {
  const [employees, setEmployees] = useState([]);
  const [selectedEmpId, setSelectedEmpId] = useState('EMP-1042');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [goldenQueries, setGoldenQueries] = useState([]);
  const [showRawTrace, setShowRawTrace] = useState(false);

  useEffect(() => {
    // Reset state on corpus switch
    setResult(null);
    setError(null);
    setQuery('');

    // Load mock employees based on corpus
    fetch(`/api/s5/employees?corpus=${corpus}`)
      .then((res) => (res.ok ? res.json() : { employees: [] }))
      .then((data) => setEmployees(data.employees || []))
      .catch(() => {});

    // Load golden queries based on corpus
    fetch(`/api/s5/golden-queries?corpus=${corpus}`)
      .then((res) => (res.ok ? res.json() : { queries: [] }))
      .then((data) => setGoldenQueries(data.queries || []))
      .catch(() => {});
  }, [corpus]);

  const activeEmployee = employees.find((e) => e.employee_id === selectedEmpId) || employees[0];

  const handleQuery = async (queryText) => {
    const q = queryText || query;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch('/api/s5/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q.trim(),
          employee_id: selectedEmpId,
          corpus: corpus,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server returned HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to process agent query.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-purple-950/40 to-slate-900 border border-purple-500/40 p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1">
              <Bot className="w-3.5 h-3.5" />
              Scenario 5 • Google ADK Agent + Agent Search
            </span>
            <span className="text-xs text-slate-400 font-mono">Framework: google-adk v1.14.1</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 font-mono text-purple-300">
              Corpus: {corpus.toUpperCase()}
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">
            Intelligent HR Assistant with Multi-Tool Reasoning
          </h1>
          <p className="text-sm text-slate-300">
            Combines enterprise policy retrieval (<em>Discovery Engine DataStore</em>) and transactional HRIS lookups (<em>Live Employee Database</em>).
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-mono">
            Model: gemini-2.5-flash
          </div>
        </div>
      </div>

      {/* HRIS Employee Selector & Live Profile */}
      <div className="rounded-2xl bg-slate-800/40 border border-slate-700/80 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <User className="w-4 h-4 text-purple-400" />
            Employee Identity Simulator (Mock Enterprise HRIS Database)
          </label>
          <span className="text-[11px] text-slate-400">
            Select a profile to test personalized policy queries ({corpus === 'en' ? 'Q4' : 'Q4-ID'})
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {employees.map((emp) => {
            const isSelected = emp.employee_id === selectedEmpId;
            const empName = emp.name || emp.nama;
            const empTitle = emp.title || emp.jabatan;
            const empDiv = emp.division || emp.divisi;
            const ptoVal = emp.pto_balance !== undefined ? emp.pto_balance : emp.sisa_cuti_tahunan;
            const wfaVal = emp.wfa_days_used !== undefined ? emp.wfa_days_used : emp.hari_wfa_terpakai;

            return (
              <button
                key={emp.employee_id}
                onClick={() => setSelectedEmpId(emp.employee_id)}
                className={`p-3.5 rounded-xl text-left border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-purple-950/40 border-purple-500/80 ring-1 ring-purple-500 shadow-lg'
                    : 'bg-slate-800/60 border-slate-700 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-xs text-white flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                    {empName}
                  </span>
                  <span className="font-mono text-[11px] px-1.5 py-0.5 rounded bg-slate-700 text-purple-300">
                    {emp.employee_id}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 truncate">{empTitle} • {empDiv}</div>
                <div className="mt-2 pt-2 border-t border-slate-700/60 flex items-center justify-between text-[11px] font-mono">
                  <span className="text-emerald-400">
                    {corpus === 'en' ? `PTO: ${ptoVal} days` : `Sisa Cuti: ${ptoVal} hari`}
                  </span>
                  <span className="text-amber-400">
                    {corpus === 'en' ? `Remote Used: ${wfaVal} days` : `WFA Terpakai: ${wfaVal} hari`}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Preset Golden Query Selector */}
      <div className="space-y-3">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          Select Golden Query Case Study (Highlighting Multi-Tool {corpus === 'en' ? 'Q4' : 'Q4-ID'})
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {goldenQueries.map((gq) => {
            const isQ4 = gq.id === 'Q4' || gq.id === 'Q4-ID';
            return (
              <button
                key={gq.id}
                onClick={() => {
                  setQuery(gq.query);
                  handleQuery(gq.query);
                }}
                className={`p-3.5 rounded-xl text-left transition-all group flex flex-col justify-between border cursor-pointer ${
                  isQ4
                    ? 'bg-purple-900/20 hover:bg-purple-900/30 border-purple-500/60 ring-1 ring-purple-500/30'
                    : 'bg-slate-800/40 hover:bg-slate-800 border-slate-700/60 hover:border-purple-500/40'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span
                      className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                        isQ4
                          ? 'bg-purple-500/30 text-purple-200 border-purple-500/50'
                          : 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20'
                      }`}
                    >
                      {gq.id} • {gq.category}
                    </span>
                    {isQ4 && (
                      <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">
                        ★ Multi-Tool
                      </span>
                    )}
                  </div>
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-purple-300 transition-colors line-clamp-2">
                    {gq.title || gq.query}
                  </div>
                </div>
                <div className="mt-2 text-[10px] text-slate-400 truncate font-mono">
                  {gq.source_doc}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Query Bar */}
      <div className="p-4 rounded-2xl bg-slate-800/50 border border-slate-700 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
              placeholder="Ask an HR policy or personal entitlement question (e.g. 'I am employee EMP-1042 requesting 15 remote work days...')..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all"
            />
          </div>

          <button
            onClick={() => handleQuery()}
            disabled={loading || !query.trim()}
            className="px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 disabled:text-slate-500 text-sm font-semibold text-white transition-all shadow-md shadow-purple-600/30 flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed whitespace-nowrap"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Bot className="w-4 h-4" />
                Run Agent
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

      {/* Latency & Metrics Cards */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400">
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
              <div className="text-[11px] text-slate-400 uppercase font-semibold">Tools Invoked</div>
              <div className="text-lg font-bold text-slate-200">
                {result.tools_called?.length || 0} Tools
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 uppercase font-semibold">Reasoning Steps</div>
              <div className="text-lg font-bold text-slate-200">
                {result.trace?.length || 0} Steps
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 uppercase font-semibold">LLM Synthesis</div>
              <div className="text-lg font-bold text-slate-200">
                {result.generation_ms ? `${result.generation_ms.toFixed(1)} ms` : '—'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Answer Section */}
      {result && (
        <div className="rounded-2xl bg-slate-800/50 border border-purple-500/40 p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-700/70 pb-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Agent Final Decision & Grounded Synthesis
            </h2>
            <div className="flex items-center gap-1.5 text-xs text-purple-300 font-mono">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              Verified by ADK Runner
            </div>
          </div>

          <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed whitespace-pre-wrap">
            {result.answer}
          </div>
        </div>
      )}

      {/* RICH AGENT EXECUTION INSPECTOR (Reasoning Trace) */}
      {result?.trace && result.trace.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Activity className="w-4 h-4 text-purple-400" />
              Rich Agent Execution Inspector — Step-by-Step Multi-Turn Trace
            </h3>
            <button
              onClick={() => setShowRawTrace(!showRawTrace)}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1 font-mono cursor-pointer"
            >
              <Terminal className="w-3.5 h-3.5" />
              {showRawTrace ? 'Hide Raw JSON' : 'View Raw JSON'}
            </button>
          </div>

          {showRawTrace && (
            <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-purple-300 overflow-x-auto leading-relaxed">
              {JSON.stringify(result.trace, null, 2)}
            </pre>
          )}

          <div className="space-y-3">
            {result.trace.map((step, idx) => {
              const isUser = step.type === 'USER_INPUT';
              const isToolCall = step.type === 'TOOL_CALL';
              const isObs = step.type === 'OBSERVATION';
              const isThought = step.type === 'THOUGHT';
              const isFinal = step.type === 'FINAL_SYNTHESIS';

              return (
                <div
                  key={idx}
                  className={`p-4 rounded-xl border transition-all ${
                    isUser
                      ? 'bg-slate-900 border-slate-700'
                      : isToolCall
                      ? 'bg-indigo-950/30 border-indigo-500/40'
                      : isObs
                      ? 'bg-emerald-950/30 border-emerald-500/40'
                      : isThought
                      ? 'bg-amber-950/30 border-amber-500/40'
                      : 'bg-purple-950/30 border-purple-500/40'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold font-mono text-slate-300">
                        {step.step || idx + 1}
                      </span>
                      <span
                        className={`text-xs font-bold px-2 py-0.5 rounded font-mono ${
                          isUser
                            ? 'bg-slate-700 text-slate-200'
                            : isToolCall
                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                            : isObs
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : isThought
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                        }`}
                      >
                        {step.type}
                      </span>
                      <span className="text-xs text-slate-300 font-medium">
                        {step.description || (isToolCall ? `Function Invocation: ${step.tool}` : '')}
                      </span>
                    </div>

                    {isToolCall && (
                      <span className="text-xs font-mono text-indigo-400">
                        Tool: {step.tool}
                      </span>
                    )}
                  </div>

                  {/* Step Body Content */}
                  <div className="text-xs text-slate-200 pl-8">
                    {isUser && (
                      <div className="p-2.5 rounded bg-slate-950 border border-slate-800 font-mono text-slate-300">
                        "{step.content}"
                      </div>
                    )}

                    {isToolCall && (
                      <div className="space-y-1">
                        <div className="text-[11px] text-slate-400">Function Input Arguments:</div>
                        <pre className="p-2.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-indigo-300 overflow-x-auto">
                          {JSON.stringify(step.arguments, null, 2)}
                        </pre>
                      </div>
                    )}

                    {isObs && (
                      <div className="space-y-1">
                        <div className="text-[11px] text-slate-400">Tool Observation Result:</div>
                        <pre className="p-2.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-emerald-300 overflow-x-auto whitespace-pre-wrap">
                          {typeof step.result === 'object' ? JSON.stringify(step.result, null, 2) : step.result}
                        </pre>
                      </div>
                    )}

                    {isThought && (
                      <div className="p-3 rounded bg-amber-950/20 border border-amber-500/30 text-amber-200 flex items-start gap-2">
                        <Calculator className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                        <div className="leading-relaxed whitespace-pre-wrap">{step.thought}</div>
                      </div>
                    )}

                    {isFinal && (
                      <div className="p-3 rounded bg-purple-950/20 border border-purple-500/30 text-purple-200 leading-relaxed whitespace-pre-wrap">
                        {step.content}
                      </div>
                    )}
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
