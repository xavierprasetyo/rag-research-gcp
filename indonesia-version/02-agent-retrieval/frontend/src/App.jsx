import React, { useState, useEffect } from 'react'
import {
  Search,
  Sparkles,
  BookOpen,
  BarChart3,
  Layers,
  Clock,
  Cpu,
  CheckCircle2,
  FileText,
  ChevronRight,
  RefreshCw,
  Sliders,
  Send,
  HelpCircle,
  ShieldCheck,
  Server
} from 'lucide-react'

const GOLDEN_QUERIES = [
  {
    id: "Q1-ID",
    category: "Semantik",
    title: "Cuti Pendampingan Istri Melahirkan",
    query: "Istri saya baru saja melahirkan. Saya dapat libur berapa hari?",
    expected_doc: "01_Kebijakan_Cuti_Karyawan.pdf",
    tag: "Semantic Search",
    tagColor: "bg-blue-100 text-blue-800 border-blue-200"
  },
  {
    id: "Q2-ID",
    category: "Kode & Singkatan",
    title: "Formulir PDN-402B & SPPD",
    query: "Formulir PDN-402B itu untuk apa, dan berapa lama batas pengajuannya setelah SPPD selesai?",
    expected_doc: "03_Kebijakan_Perjalanan_Dinas_dan_Reimburse.pdf",
    tag: "Hybrid BM25 + Vector",
    tagColor: "bg-amber-100 text-amber-800 border-amber-200"
  },
  {
    id: "Q3-ID",
    category: "Tabel Multikolom",
    title: "Plafon Staf vs Manajer",
    query: "Bandingkan plafon rawat jalan per tahun dan tunjangan persalinan caesar antara level Staf dan Manajer.",
    expected_doc: "02_Panduan_Tunjangan_dan_Kesehatan_2026.pdf",
    tag: "Table Parsing",
    tagColor: "bg-emerald-100 text-emerald-800 border-emerald-200"
  },
  {
    id: "Q4-ID",
    category: "Agentik + Policy",
    title: "Aturan & Kuota WFA",
    query: "Berapa hari maksimal WFA dalam negeri per tahun dan bagaimana aturan pengajuannya?",
    expected_doc: "04_FAQ_WFH_WFA_dan_Tunjangan_Peralatan.pdf",
    tag: "Policy Hybrid",
    tagColor: "bg-purple-100 text-purple-800 border-purple-200"
  }
]

export default function App() {
  const [activeTab, setActiveTab] = useState('chat') // 'chat' | 'docs' | 'benchmark'
  const [query, setQuery] = useState('')
  const [searchMode, setSearchMode] = useState('hybrid') // 'hybrid' | 'semantic' | 'text'
  const [topK, setTopK] = useState(4)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [activeGoldenId, setActiveGoldenId] = useState(null)
  const [documents, setDocuments] = useState([])
  const [benchmarks, setBenchmarks] = useState([])
  const [backendHealth, setBackendHealth] = useState(null)

  // Fetch health and documents on initial load
  useEffect(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(data => setBackendHealth(data))
      .catch(err => console.error("Health check error:", err))

    fetch('/api/documents')
      .then(r => r.json())
      .then(data => setDocuments(data.documents || []))
      .catch(err => console.error("Docs load error:", err))

    fetch('/api/benchmark')
      .then(r => r.json())
      .then(data => setBenchmarks(data.results || []))
      .catch(err => console.error("Benchmark load error:", err))
  }, [])

  // Execute query function
  const handleSearch = async (queryText = query, mode = searchMode) => {
    const trimmed = (queryText || '').trim()
    if (!trimmed) return

    setLoading(true)
    setResult(null)

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: trimmed,
          mode: mode,
          top_k: topK
        })
      })

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${await response.text()}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      console.error("Query failed:", err)
      setResult({
        query: trimmed,
        mode: mode,
        answer: `Terjadi kesalahan saat memproses permintaan: ${err.message}`,
        chunks: [],
        retrieval_ms: 0,
        generation_ms: 0,
        total_ms: 0,
        error: true
      })
    } finally {
      setLoading(false)
    }
  }

  // 1-Click Golden Query Trigger
  const handleGoldenClick = (item) => {
    setQuery(item.query)
    setActiveGoldenId(item.id)
    setActiveTab('chat')
    handleSearch(item.query, searchMode)
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* --- TOP NAVBAR --- */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🇮🇩</span>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">PT Cymbal Indonesia</span>
                <span className="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full font-medium border border-blue-200">
                  Skenario 2: Agent Retrieval
                </span>
              </div>
              <p className="text-xs text-slate-500">Asisten Kebijakan HR Berbasis Google Cloud Vector Search 2.0</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 sm:space-x-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition ${
                activeTab === 'chat'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Search className="w-4 h-4" />
              <span>Tanya Jawab</span>
            </button>
            <button
              onClick={() => setActiveTab('docs')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition ${
                activeTab === 'docs'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>Dokumen ({documents.length})</span>
            </button>
            <button
              onClick={() => setActiveTab('benchmark')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition ${
                activeTab === 'benchmark'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Benchmark Golden Queries</span>
            </button>
          </nav>
        </div>
      </header>

      {/* --- SUB-HEADER: INFRASTRUCTURE BADGES --- */}
      <div className="bg-slate-900 text-slate-300 py-2.5 px-4 text-xs border-b border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-y-2">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-white font-medium">GCP Live:</span>
              <code className="text-blue-300">rag-research-sandbox</code> (us-central1)
            </span>
            <span className="hidden sm:inline text-slate-600">•</span>
            <span className="flex items-center space-x-1">
              <Layers className="w-3.5 h-3.5 text-blue-400" />
              <span>Collection:</span>
              <code className="text-slate-100">hr-faq-id</code>
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Auto-Embedding:</span>
              <span className="text-slate-100 font-medium">gemini-embedding-2 (768d)</span>
            </span>
            <span className="hidden sm:inline text-slate-600">•</span>
            <span className="flex items-center space-x-1">
              <Cpu className="w-3.5 h-3.5 text-emerald-400" />
              <span>LLM Engine:</span>
              <span className="bg-emerald-950 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-800 font-mono">
                gemini-3.5-flash-lite
              </span>
            </span>
          </div>
        </div>
      </div>

      {/* --- MAIN BODY --- */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ===================== TAB 1: CHAT & RETRIEVAL ===================== */}
        {activeTab === 'chat' && (
          <div className="space-y-8">
            {/* --- 1-CLICK GOLDEN QUERIES SECTION --- */}
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-amber-500" />
                  <h2 className="text-base font-bold text-slate-900">Uji Coba Cepat (1-Click Golden Queries)</h2>
                </div>
                <span className="text-xs text-slate-500 font-medium">Klik untuk langsung mengeksekusi retrieval & sintesis</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3.5">
                {GOLDEN_QUERIES.map((item) => {
                  const isSelected = activeGoldenId === item.id
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleGoldenClick(item)}
                      disabled={loading}
                      className={`text-left p-3.5 rounded-lg border transition duration-150 flex flex-col justify-between hover:shadow-md cursor-pointer ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50/60 ring-2 ring-blue-500/20'
                          : 'border-slate-200 bg-slate-50/50 hover:bg-white hover:border-slate-300'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="font-bold text-xs text-blue-700 bg-blue-100/70 px-2 py-0.5 rounded">
                            {item.id}
                          </span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium border ${item.tagColor}`}>
                            {item.category}
                          </span>
                        </div>
                        <h4 className="font-semibold text-sm text-slate-900 line-clamp-1">{item.title}</h4>
                        <p className="text-xs text-slate-600 mt-1 italic line-clamp-2">"{item.query}"</p>
                      </div>
                      <div className="mt-3 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-slate-500">
                        <span className="truncate max-w-[150px]">{item.expected_doc}</span>
                        <ChevronRight className="w-3.5 h-3.5 text-blue-600 shrink-0 ml-1" />
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* --- SEARCH QUERY & MODE SELECTOR BOX --- */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  handleSearch()
                }}
                className="space-y-4"
              >
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                    Pertanyaan Pengguna (Bahasa Indonesia)
                  </label>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Ketik pertanyaan atau klik salah satu Golden Query di atas..."
                        className="w-full pl-4 pr-10 py-3 rounded-lg border border-slate-300 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm shadow-xs"
                      />
                      {query && (
                        <button
                          type="button"
                          onClick={() => setQuery('')}
                          className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 text-xs px-1"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                    <button
                      type="submit"
                      disabled={loading || !query.trim()}
                      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-medium rounded-lg text-sm flex items-center space-x-2 transition shadow-xs cursor-pointer disabled:cursor-not-allowed"
                    >
                      {loading ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          <span>Memproses...</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          <span>Kirim</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Algorithmic Controls */}
                <div className="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-slate-100">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold text-slate-600">Mode Retrieval:</span>
                    <div className="inline-flex rounded-lg p-0.5 bg-slate-100 border border-slate-200">
                      <button
                        type="button"
                        onClick={() => setSearchMode('hybrid')}
                        className={`px-3 py-1 rounded-md text-xs font-medium transition ${
                          searchMode === 'hybrid'
                            ? 'bg-white text-blue-700 shadow-xs font-semibold'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        🔀 Hybrid (Semantic + BM25 RRF)
                      </button>
                      <button
                        type="button"
                        onClick={() => setSearchMode('semantic')}
                        className={`px-3 py-1 rounded-md text-xs font-medium transition ${
                          searchMode === 'semantic'
                            ? 'bg-white text-blue-700 shadow-xs font-semibold'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        🧠 Pure Semantic
                      </button>
                      <button
                        type="button"
                        onClick={() => setSearchMode('text')}
                        className={`px-3 py-1 rounded-md text-xs font-medium transition ${
                          searchMode === 'text'
                            ? 'bg-white text-blue-700 shadow-xs font-semibold'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        🔤 Keyword BM25
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 text-xs text-slate-600">
                    <Sliders className="w-3.5 h-3.5 text-slate-400" />
                    <span>Top-K:</span>
                    <select
                      value={topK}
                      onChange={(e) => setTopK(Number(e.target.value))}
                      className="bg-slate-50 border border-slate-300 rounded px-2 py-0.5 text-xs text-slate-800 font-medium"
                    >
                      <option value={2}>2 Chunks</option>
                      <option value={4}>4 Chunks (Default)</option>
                      <option value={6}>6 Chunks</option>
                      <option value={8}>8 Chunks</option>
                    </select>
                  </div>
                </div>
              </form>
            </div>

            {/* --- LOADING SKELETON --- */}
            {loading && (
              <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-xs text-center space-y-4 animate-pulse">
                <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto">
                  <RefreshCw className="w-6 h-6 animate-spin" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-slate-900">Menjalankan Agent Retrieval...</h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Mengambil embedding dari Collection <code className="text-blue-600">hr-faq-id</code> dan mensintesis jawaban via <span className="font-semibold text-slate-700">gemini-3.5-flash-lite</span>...
                  </p>
                </div>
              </div>
            )}

            {/* --- RESULTS DISPLAY --- */}
            {result && !loading && (
              <div className="space-y-6">
                {/* Latency & Performance Metric Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Mode Pencarian</span>
                    <div className="mt-1 flex items-center space-x-2">
                      <span className="text-base font-bold text-slate-900 uppercase">{result.mode}</span>
                    </div>
                    <span className="text-[11px] text-slate-500 mt-0.5 block">
                      {result.mode === 'hybrid' ? 'Semantic + BM25 RRF' : result.mode === 'semantic' ? 'gemini-embedding-2' : 'BM25 Exact Match'}
                    </span>
                  </div>

                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center justify-between">
                      <span>Retrieval Time</span>
                      <Clock className="w-3.5 h-3.5 text-blue-500" />
                    </span>
                    <div className="mt-1 text-2xl font-bold text-blue-600 font-mono">
                      {result.retrieval_ms} <span className="text-sm font-normal text-slate-500">ms</span>
                    </div>
                    <span className="text-[11px] text-slate-500 mt-0.5 block">Vector Search 2.0 Latency</span>
                  </div>

                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center justify-between">
                      <span>LLM Generation</span>
                      <Cpu className="w-3.5 h-3.5 text-emerald-500" />
                    </span>
                    <div className="mt-1 text-2xl font-bold text-emerald-600 font-mono">
                      {result.generation_ms} <span className="text-sm font-normal text-slate-500">ms</span>
                    </div>
                    <span className="text-[11px] text-slate-500 mt-0.5 block">gemini-3.5-flash-lite</span>
                  </div>

                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total End-to-End</span>
                    <div className="mt-1 text-2xl font-bold text-slate-900 font-mono">
                      {result.total_ms} <span className="text-sm font-normal text-slate-500">ms</span>
                    </div>
                    <span className="text-[11px] text-slate-500 mt-0.5 block">Retrieval + LLM Response</span>
                  </div>
                </div>

                {/* Synthesized Answer Box */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
                  <div className="bg-slate-50/80 px-6 py-3.5 border-b border-slate-200 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="w-4 h-4 text-amber-500" />
                      <h3 className="font-bold text-sm text-slate-800">Jawaban Asisten HR</h3>
                    </div>
                    <span className="text-xs text-slate-500 flex items-center space-x-1">
                      <ShieldCheck className="w-4 h-4 text-emerald-600" />
                      <span>Grounded via Collection 'hr-faq-id'</span>
                    </span>
                  </div>
                  <div className="p-6">
                    <div className="prose prose-slate max-w-none text-slate-800 leading-relaxed whitespace-pre-line text-sm sm:text-base">
                      {result.answer}
                    </div>
                  </div>
                </div>

                {/* Retrieved Chunks Inspector */}
                <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <Layers className="w-5 h-5 text-blue-600" />
                      <h3 className="font-bold text-base text-slate-900">
                        Konteks Chunk Ditemukan ({result.chunks?.length || 0})
                      </h3>
                    </div>
                    <span className="text-xs text-slate-500">
                      Disajikan untuk transparansi dan audit dokumen sumber
                    </span>
                  </div>

                  <div className="space-y-3">
                    {result.chunks && result.chunks.map((chunk, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-lg bg-slate-50 border border-slate-200 hover:border-blue-300 transition duration-150"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-200/70">
                          <div className="flex items-center space-x-2">
                            <span className="bg-blue-600 text-white text-xs font-bold px-2 py-0.5 rounded">
                              #{idx + 1}
                            </span>
                            <span className="font-semibold text-xs text-slate-800 flex items-center space-x-1">
                              <FileText className="w-3.5 h-3.5 text-slate-500" />
                              <span>{chunk.source_doc}</span>
                            </span>
                            <span className="text-xs text-slate-500 bg-slate-200/60 px-2 py-0.5 rounded">
                              Halaman {chunk.page_num}
                            </span>
                          </div>

                          <div className="flex items-center space-x-3 text-xs">
                            {chunk.rrf_score && (
                              <span className="font-mono text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                                RRF Score: <b>{chunk.rrf_score.toFixed(5)}</b>
                              </span>
                            )}
                            <code className="text-[11px] text-slate-500">ID: {chunk.chunk_id}</code>
                          </div>
                        </div>

                        <p className="text-xs text-slate-700 leading-relaxed font-mono bg-white p-3 rounded border border-slate-100">
                          "{chunk.text}"
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ===================== TAB 2: DOCUMENT LIBRARY ===================== */}
        {activeTab === 'docs' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
              <h2 className="text-lg font-bold text-slate-900 mb-2">Paket Kebijakan HR PT Cymbal Indonesia</h2>
              <p className="text-sm text-slate-600">
                Empat dokumen PDF resmi yang telah diuraikan menjadi 33 potongan teks (chunks) dan diindeks secara otomatis ke dalam Collection <code>hr-faq-id</code> menggunakan model auto-embedding <code>gemini-embedding-2</code>.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {documents.map((doc, idx) => (
                <div key={idx} className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="bg-blue-100 text-blue-800 text-xs font-mono font-semibold px-2 py-0.5 rounded">
                        {doc.code}
                      </span>
                      <span className="text-xs text-slate-500 font-medium">{doc.filename}</span>
                    </div>
                    <h3 className="text-base font-bold text-slate-900 mb-2">{doc.title}</h3>
                    <p className="text-xs text-slate-600 leading-relaxed mb-4">{doc.description}</p>
                  </div>

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    <span className="text-slate-500">Fokus Uji:</span>
                    <span className="font-semibold text-blue-700">{doc.test_target}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ===================== TAB 3: BENCHMARK RESULTS ===================== */}
        {activeTab === 'benchmark' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
              <h2 className="text-lg font-bold text-slate-900 mb-1">Hasil Evaluasi 4 Golden Queries (Skenario 2)</h2>
              <p className="text-sm text-slate-600">
                Data hasil uji benchmark terverifikasi dari eksekusi resmi <code>eval_golden.py</code> pada Google Cloud Project <code>rag-research-sandbox</code>.
              </p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs sm:text-sm">
                  <thead className="bg-slate-100 text-slate-700 uppercase font-semibold text-[11px] border-b border-slate-200">
                    <tr>
                      <th className="py-3.5 px-4">ID</th>
                      <th className="py-3.5 px-4">Kategori Uji</th>
                      <th className="py-3.5 px-4">Mode</th>
                      <th className="py-3.5 px-4">Status & Dokumen Terpilih</th>
                      <th className="py-3.5 px-4 text-right">Retrieval (ms)</th>
                      <th className="py-3.5 px-4 text-right">LLM (ms)</th>
                      <th className="py-3.5 px-4 text-right">Total (ms)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {benchmarks.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/80 transition">
                        <td className="py-3.5 px-4 font-bold text-blue-700">{row.id}</td>
                        <td className="py-3.5 px-4 font-medium text-slate-800">{row.category}</td>
                        <td className="py-3.5 px-4">
                          <span className="bg-slate-200/80 text-slate-800 text-[11px] font-mono px-2 py-0.5 rounded font-semibold uppercase">
                            {row.mode}
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          <div className="flex items-center space-x-1.5">
                            <span className="text-emerald-600 font-bold">{row.doc_matched}</span>
                            <span className="text-slate-600 text-xs truncate max-w-[220px]">{row.retrieved_doc}</span>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono font-medium text-slate-700">{row.retrieval_ms?.toFixed(1)}</td>
                        <td className="py-3.5 px-4 text-right font-mono font-medium text-slate-700">{row.generation_ms?.toFixed(1)}</td>
                        <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-900">{row.total_ms?.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* --- FOOTER --- */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        <p>PT Cymbal Indonesia · Demo Arsitektur Retrieval & Search Google Cloud · 2026</p>
      </footer>
    </div>
  )
}
