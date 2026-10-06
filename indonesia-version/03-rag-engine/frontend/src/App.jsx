import React, { useState, useEffect } from 'react'
import { Search, Clock, FileText, Layers, Server } from 'lucide-react'

const MODES = [
  { id: 'tool', label: 'Tool VertexRagStore', hint: 'Satu panggilan Gemini; Google yang mengambil chunk' },
  { id: 'retrieve', label: 'rag.retrieval_query', hint: 'Kita ambil chunk sendiri, lalu susun prompt' },
]

const fmt = (ms) => (ms == null ? 'n/a' : `${Math.round(ms)} ms`)

export default function App() {
  const [golden, setGolden] = useState([])
  const [health, setHealth] = useState(null)
  const [benchmark, setBenchmark] = useState([])
  const [query, setQuery] = useState('')
  const [mode, setMode] = useState('tool')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('/api/golden-queries').then((r) => r.json()).then((d) => setGolden(d.queries))
    fetch('/api/health').then((r) => r.json()).then(setHealth).catch(() => {})
    fetch('/api/benchmark').then((r) => r.json()).then((d) => setBenchmark(d.results))
  }, [])

  const ask = async (text = query, m = mode) => {
    if (!text.trim()) return
    setQuery(text)
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text, mode: m, top_k: 4 }),
      })
      if (!res.ok) throw new Error((await res.json()).detail || res.statusText)
      setResult(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold">Skenario 3: RAG Engine — Agen FAQ HR PT Cymbal Indonesia</h1>
        <p className="text-sm text-slate-600">
          Google melakukan parsing, chunking, embedding, dan penyimpanan dari GCS. Kita hanya mengatur corpus dan memanggil Gemini.
        </p>
        {health && (
          <p className="text-xs text-slate-500 flex items-center gap-1">
            <Server size={12} /> corpus <b>{health.corpus}</b> · embedding <b>{health.embedding_model}</b> · chunk {health.chunk_size}/{health.chunk_overlap} · LLM <b>{health.llm_model}</b>
          </p>
        )}
      </header>

      <section className="grid sm:grid-cols-2 gap-3">
        {golden.map((g) => (
          <button
            key={g.id}
            onClick={() => ask(g.query)}
            className="text-left p-3 rounded-lg border border-slate-200 bg-white hover:border-indigo-400 transition"
          >
            <div className="text-xs font-semibold text-indigo-700">{g.id} · {g.category}</div>
            <div className="text-sm mt-1">{g.query}</div>
          </button>
        ))}
      </section>

      <section className="space-y-2">
        <div className="flex gap-2">
          {MODES.map((m) => (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              title={m.hint}
              className={`px-3 py-1 rounded-full text-sm border ${mode === m.id ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white border-slate-300'}`}
            >
              {m.label}
            </button>
          ))}
        </div>
        <form onSubmit={(e) => { e.preventDefault(); ask() }} className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tanyakan kebijakan HR..."
            className="flex-1 border border-slate-300 rounded-lg px-3 py-2 bg-white"
          />
          <button disabled={loading} className="px-4 py-2 rounded-lg bg-indigo-600 text-white flex items-center gap-1 disabled:opacity-50">
            <Search size={16} /> {loading ? 'Mencari...' : 'Tanya'}
          </button>
        </form>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </section>

      {result && (
        <section className="space-y-4">
          <div className="grid grid-cols-3 gap-3 text-sm">
            {[['Retrieval', result.retrieval_ms], ['Generasi', result.generation_ms], ['Total', result.total_ms]].map(([k, v]) => (
              <div key={k} className="p-3 rounded-lg bg-white border border-slate-200">
                <div className="text-xs text-slate-500 flex items-center gap-1"><Clock size={12} /> {k}</div>
                <div className="font-bold">{fmt(v)}</div>
              </div>
            ))}
          </div>
          {result.mode === 'tool' && (
            <p className="text-xs text-slate-500">Mode tool: retrieval terjadi di dalam satu panggilan Gemini, jadi latensi hanya dilaporkan total.</p>
          )}
          <div className="p-4 rounded-lg bg-white border border-slate-200 whitespace-pre-wrap text-sm leading-relaxed">
            {result.answer}
          </div>
          <div className="space-y-2">
            <h2 className="font-semibold flex items-center gap-1"><Layers size={16} /> Chunk yang diambil ({result.chunks.length})</h2>
            {result.chunks.map((c, i) => (
              <div key={i} className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
                <div className="font-semibold flex items-center gap-1">
                  <FileText size={12} /> {c.source_doc}
                  {c.score != null && <span className="ml-auto font-normal text-slate-500">jarak: {c.score.toFixed(4)} (makin kecil makin dekat)</span>}
                </div>
                <div className="whitespace-pre-wrap text-slate-700">{c.text}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {benchmark.length > 0 && (
        <section className="space-y-2">
          <h2 className="font-semibold">Hasil benchmark terakhir</h2>
          <table className="w-full text-xs bg-white border border-slate-200">
            <thead className="bg-slate-100 text-left">
              <tr>{['ID', 'Mode', 'Dokumen benar', 'Retrieval', 'Generasi', 'Total'].map((h) => <th key={h} className="p-2">{h}</th>)}</tr>
            </thead>
            <tbody>
              {benchmark.map((r, i) => (
                <tr key={i} className="border-t border-slate-200">
                  <td className="p-2">{r.id}</td>
                  <td className="p-2">{r.mode}</td>
                  <td className="p-2">{r.doc_matched}</td>
                  <td className="p-2">{fmt(r.retrieval_ms)}</td>
                  <td className="p-2">{fmt(r.generation_ms)}</td>
                  <td className="p-2">{fmt(r.total_ms)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}
