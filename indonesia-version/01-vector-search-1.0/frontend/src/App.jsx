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
  AlertTriangle,
  FileText,
  ChevronRight,
  RefreshCw,
  Database,
  Sliders,
  Send,
  HelpCircle,
  ShieldCheck,
  Server,
  ArrowRight,
  Terminal,
  ExternalLink,
} from 'lucide-react'

const GOLDEN_QUERIES = [
  {
    id: "Q1-ID",
    category: "Semantik Murni",
    title: "Cuti Pendampingan Istri Melahirkan",
    query: "Istri saya baru saja melahirkan. Saya dapat libur berapa hari?",
    expected_doc: "01_Kebijakan_Cuti_Karyawan.pdf",
    tag: "Pure Dense Vector",
    tagColor: "bg-amber-100 text-amber-800 border-amber-200",
    description: "Menguji semantic bridging dari bahasa sehari-hari ke 'cuti pendampingan persalinan' (5 hari)."
  },
  {
    id: "Q2-ID",
    category: "Kode & Singkatan",
    title: "Formulir PDN-402B & SPPD",
    query: "Formulir PDN-402B itu untuk apa, dan berapa lama batas pengajuannya setelah SPPD selesai?",
    expected_doc: "03_Kebijakan_Perjalanan_Dinas_dan_Reimburse.pdf",
    tag: "Dense vs Keyword Limit",
    tagColor: "bg-red-100 text-red-800 border-red-200",
    description: "Menguji batas dense vector murni (tanpa BM25) dalam mengenali kode formulir dan singkatan SPPD (14 hari)."
  },
  {
    id: "Q3-ID",
    category: "Tabel Multikolom",
    title: "Plafon Staf vs Manajer",
    query: "Bandingkan plafon rawat jalan per tahun dan tunjangan persalinan caesar antara level Staf dan Manajer.",
    expected_doc: "02_Panduan_Tunjangan_dan_Kesehatan_2026.pdf",
    tag: "Table Parsing (pypdf)",
    tagColor: "bg-emerald-100 text-emerald-800 border-emerald-200",
    description: "Menguji parsing tabel multikolom hasil ekstraksi teks pypdf mentah vs pemahaman Gemini."
  },
  {
    id: "Q4-ID",
    category: "Aturan Kebijakan",
    title: "Aturan & Kuota WFA",
    query: "Berapa hari maksimal WFA dalam negeri per tahun dan bagaimana aturan pengajuannya?",
    expected_doc: "04_FAQ_WFH_WFA_dan_Tunjangan_Peralatan.pdf",
    tag: "Dense Policy Match",
    tagColor: "bg-purple-100 text-purple-800 border-purple-200",
    description: "Menguji aturan WFA dalam negeri (maksimal 20 hari kerja/tahun, pengajuan H-7)."
  }
]

export default function App() {
  const [activeTab, setActiveTab] = useState('chat') // 'chat' | 'docs' | 'benchmark' | 'infra'
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(4)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [activeGoldenId, setActiveGoldenId] = useState(null)
  const [documents, setDocuments] = useState([])
  const [benchmarks, setBenchmarks] = useState([])
  const [backendHealth, setBackendHealth] = useState(null)
  const [infraStatus, setInfraStatus] = useState(null)
  const [refreshingStatus, setRefreshingStatus] = useState(false)

  const fetchStatus = () => {
    setRefreshingStatus(true)
    fetch('/api/health')
      .then(r => r.json())
      .then(data => setBackendHealth(data))
      .catch(err => console.error("Health check error:", err))

    fetch('/api/status')
      .then(r => r.json())
      .then(data => setInfraStatus(data))
      .catch(err => console.error("Status check error:", err))
      .finally(() => setRefreshingStatus(false))
  }

  useEffect(() => {
    fetchStatus()

    fetch('/api/documents')
      .then(r => r.json())
      .then(data => setDocuments(data.documents || []))
      .catch(err => console.error("Docs load error:", err))

    fetch('/api/benchmark')
      .then(r => r.json())
      .then(data => setBenchmarks(data.results || []))
      .catch(err => console.error("Benchmark load error:", err))
  }, [])

  const handleSearch = async (queryText = query) => {
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
          top_k: topK
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Server returned ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      console.error("Query failed:", err)
      setResult({
        query: trimmed,
        answer: `Terjadi kesalahan saat memproses permintaan: ${err.message}`,
        chunks: [],
        raw_datapoints: [],
        latency: {
          embedding_ms: 0,
          scann_ms: 0,
          firestore_ms: 0,
          llm_ms: 0,
          total_ms: 0
        },
        error: true
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGoldenClick = (item) => {
    setQuery(item.query)
    setActiveGoldenId(item.id)
    setActiveTab('chat')
    handleSearch(item.query)
  }

  const isDeployed = backendHealth?.is_deployed || infraStatus?.endpoint?.is_deployed

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
                <span className="bg-amber-100 text-amber-900 text-xs px-2.5 py-0.5 rounded-full font-semibold border border-amber-300">
                  Skenario 1: Vector Search 1.0 (ScaNN + Firestore)
                </span>
              </div>
              <p className="text-xs text-slate-500">Arsitektur RAG Terpisah: Index ANN Murni + Database Dokumen Eksternal</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 sm:space-x-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition ${
                activeTab === 'chat'
                  ? 'bg-amber-600 text-white shadow-xs'
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
                  ? 'bg-amber-600 text-white shadow-xs'
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
                  ? 'bg-amber-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Benchmark Golden Queries</span>
            </button>
            <button
              onClick={() => setActiveTab('infra')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition ${
                activeTab === 'infra'
                  ? 'bg-amber-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Server className="w-4 h-4" />
              <span>Infrastruktur & Kontrol</span>
            </button>
          </nav>
        </div>
      </header>

      {/* --- SUB-HEADER: INFRASTRUCTURE BADGES --- */}
      <div className="bg-slate-900 text-slate-300 py-2.5 px-4 text-xs border-b border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-y-2">
          <div className="flex items-center space-x-4 flex-wrap gap-y-1">
            <span className="flex items-center space-x-1.5">
              <span className="text-slate-500">Region:</span>
              <span className="font-mono text-amber-400 font-semibold">{backendHealth?.location || 'us-central1'}</span>
            </span>
            <span className="text-slate-700">|</span>
            <span className="flex items-center space-x-1.5">
              <span className="text-slate-500">Index:</span>
              <span className="font-mono text-slate-200">{backendHealth?.index_display_name || 'hr-faq-index-id'}</span>
            </span>
            <span className="text-slate-700">|</span>
            <span className="flex items-center space-x-1.5">
              <span className="text-slate-500">Endpoint VM:</span>
              {isDeployed ? (
                <span className="bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded text-[11px] font-semibold flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>ONLINE ({infraStatus?.endpoint?.machine_type || 'e2-standard-16'})</span>
                </span>
              ) : (
                <span className="bg-amber-950 text-amber-400 border border-amber-800 px-2 py-0.5 rounded text-[11px] font-semibold flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                  <span>UNDEPLOYED (VM Nonaktif)</span>
                </span>
              )}
            </span>
            <span className="text-slate-700">|</span>
            <span className="flex items-center space-x-1.5">
              <Database className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-slate-500">Payload DB:</span>
              <span className="font-mono text-blue-300">Firestore (hr-faq-chunks-id)</span>
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-slate-400">
              Embedding: <strong className="text-slate-200">gemini-embedding-2 (768d)</strong>
            </span>
            <span className="text-slate-700">|</span>
            <span className="text-slate-400">
              LLM: <strong className="text-slate-200">{backendHealth?.llm_model || 'gemini-3.5-flash-lite'}</strong>
            </span>
            <button
              onClick={fetchStatus}
              disabled={refreshingStatus}
              title="Segarkan Status Infrastruktur"
              className="p-1 hover:bg-slate-800 rounded transition text-slate-400 hover:text-white"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshingStatus ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* --- WARNING BANNER JIKA ENDPOINT VM BELUM DEPLOYED --- */}
      {!isDeployed && (
        <div className="bg-amber-500/10 border-b border-amber-500/30 px-4 py-3 text-amber-900 text-sm">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
              <span>
                <strong>Perhatian:</strong> MatchingEngineIndexEndpoint belum di-deploy ke node VM komputasi.
                Untuk mengaktifkan pencarian kueri live, jalankan perintah CLI:
                <code className="bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-mono text-xs ml-2">python manage_index.py deploy</code>
              </span>
            </div>
            <button
              onClick={() => setActiveTab('infra')}
              className="text-xs font-semibold text-amber-800 underline hover:text-amber-950 shrink-0 ml-4"
            >
              Lihat Panduan CLI &rarr;
            </button>
          </div>
        </div>
      )}

      {/* --- MAIN CONTENT AREA --- */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full">
        {/* ======================================================== */}
        {/* TAB 1: TANYA JAWAB (CHAT & INSPECTOR)                    */}
        {/* ======================================================== */}
        {activeTab === 'chat' && (
          <div className="space-y-6">
            {/* 1-Click Golden Test Query Cards */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wider flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  <span>1-Click Indonesian Golden Queries (Pertanyaan Uji Terstandarisasi)</span>
                </h2>
                <span className="text-xs text-slate-500">Klik salah satu kartu untuk langsung menguji pipeline 4-tahap</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                {GOLDEN_QUERIES.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => handleGoldenClick(item)}
                    className={`cursor-pointer border rounded-xl p-3.5 transition duration-150 hover:shadow-md ${
                      activeGoldenId === item.id
                        ? 'border-amber-500 bg-amber-50/50 ring-2 ring-amber-500/20'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-mono text-xs font-bold text-slate-500">{item.id}</span>
                      <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium border ${item.tagColor}`}>
                        {item.tag}
                      </span>
                    </div>
                    <h3 className="font-semibold text-sm text-slate-900 mb-1">{item.title}</h3>
                    <p className="text-xs text-slate-600 line-clamp-2 italic mb-2">"{item.query}"</p>
                    <div className="text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-100 pt-2">
                      <span className="truncate">{item.expected_doc.replace('.pdf', '')}</span>
                      <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Search Input Box */}
            <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  handleSearch()
                }}
                className="space-y-3"
              >
                <div className="relative flex items-center">
                  <Search className="w-5 h-5 text-slate-400 absolute left-4 pointer-events-none" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value)
                      setActiveGoldenId(null)
                    }}
                    placeholder="Ajukan pertanyaan mengenai kebijakan HR PT Cymbal Indonesia (misal: jatah cuti, plafon rawat jalan, PDN-402B)..."
                    className="w-full pl-11 pr-28 py-3 bg-slate-50 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 focus:bg-white transition"
                  />
                  <button
                    type="submit"
                    disabled={loading || !query.trim()}
                    className="absolute right-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 disabled:bg-slate-300 text-white rounded-lg text-sm font-medium flex items-center space-x-1.5 transition shadow-xs"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Mencari...</span>
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        <span>Tanya</span>
                      </>
                    )}
                  </button>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-500 px-1 pt-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-slate-700">Top-K Tetangga:</span>
                    <select
                      value={topK}
                      onChange={(e) => setTopK(Number(e.target.value))}
                      className="bg-slate-100 border border-slate-200 rounded px-2 py-1 text-slate-700 font-medium focus:outline-none"
                    >
                      <option value={2}>2 Chunks</option>
                      <option value={4}>4 Chunks (Default)</option>
                      <option value={6}>6 Chunks</option>
                      <option value={8}>8 Chunks</option>
                    </select>
                  </div>
                  <span className="italic text-slate-400">
                    Alur: Query &rarr; gemini-embedding-2 &rarr; ScaNN ANN &rarr; Firestore Resolution &rarr; Gemini Synthesis
                  </span>
                </div>
              </form>
            </div>

            {/* Loading Indicator */}
            {loading && (
              <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-3 shadow-xs animate-pulse">
                <div className="w-10 h-10 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto">
                  <RefreshCw className="w-5 h-5 animate-spin" />
                </div>
                <h3 className="font-semibold text-slate-800 text-sm">Menjalankan Pipeline 4-Tahap Vector Search 1.0...</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  1. Embed kueri &rarr; 2. Cari tetangga ScaNN di IndexEndpoint VM &rarr; 3. Ambil teks payload dari Cloud Firestore &rarr; 4. Sintesis jawaban dengan Gemini.
                </p>
              </div>
            )}

            {/* Results Display */}
            {result && !loading && (
              <div className="space-y-6">
                {/* 1. Grounded Answer Box */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <Sparkles className="w-5 h-5 text-amber-500" />
                        <h2 className="font-bold text-slate-900 text-base">Jawaban Asisten HR Cymbal Indonesia</h2>
                      </div>
                      <p className="text-xs text-slate-500 font-mono">Pertanyaan: "{result.query}"</p>
                    </div>

                    <div className="flex items-center space-x-2">
                      {result.is_live_vm === false && (
                        <span className="text-[11px] font-medium text-amber-700 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200" title="Endpoint VM sedang disiapkan di GCP. Resolusi teks & sintesis Gemini berjalan langsung dari Cloud Firestore & Vertex AI.">
                          ⚡ Mode Preview VM
                        </span>
                      )}
                      <span className="text-xs font-mono font-bold text-amber-700 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200">
                        Total: {result.latency?.total_ms || 0} ms
                      </span>
                    </div>
                  </div>

                  <div className="prose prose-slate max-w-none text-sm leading-relaxed bg-slate-50/70 p-4 rounded-xl border border-slate-100 whitespace-pre-wrap">
                    {result.answer}
                  </div>

                  {/* Latency Multi-Stage Visualizer */}
                  {result.latency && (
                    <div className="border-t border-slate-100 pt-4 space-y-2">
                      <div className="flex items-center justify-between text-xs font-medium text-slate-700">
                        <span className="flex items-center space-x-1">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          <span>Rincian Latensi 4 Tahap Pipeline:</span>
                        </span>
                        <span className="font-mono text-slate-500">Total: {result.latency.total_ms}ms</span>
                      </div>

                      {/* Horizontal progress bar */}
                      <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden flex">
                        <div
                          style={{ width: `${Math.max(5, (result.latency.embedding_ms / result.latency.total_ms) * 100)}%` }}
                          className="bg-blue-500"
                          title={`Query Embedding: ${result.latency.embedding_ms}ms`}
                        />
                        <div
                          style={{ width: `${Math.max(5, (result.latency.scann_ms / result.latency.total_ms) * 100)}%` }}
                          className="bg-amber-500"
                          title={`ScaNN Search: ${result.latency.scann_ms}ms`}
                        />
                        <div
                          style={{ width: `${Math.max(5, (result.latency.firestore_ms / result.latency.total_ms) * 100)}%` }}
                          className="bg-red-500"
                          title={`Firestore Lookup: ${result.latency.firestore_ms}ms`}
                        />
                        <div
                          style={{ width: `${Math.max(5, (result.latency.llm_ms / result.latency.total_ms) * 100)}%` }}
                          className="bg-emerald-500"
                          title={`Gemini LLM: ${result.latency.llm_ms}ms`}
                        />
                      </div>

                      {/* Latency metric pills */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-xs">
                        <div className="p-2 rounded-lg bg-blue-50 border border-blue-100">
                          <div className="flex items-center justify-between mb-0.5">
                            <span className="text-blue-700 font-medium">1. Embedding</span>
                            <span className="font-mono font-bold text-blue-900">{result.latency.embedding_ms}ms</span>
                          </div>
                          <span className="text-[10px] text-blue-600">gemini-embedding-2</span>
                        </div>

                        <div className="p-2 rounded-lg bg-amber-50 border border-amber-100">
                          <div className="flex items-center justify-between mb-0.5">
                            <span className="text-amber-700 font-medium">2. ScaNN Search</span>
                            <span className="font-mono font-bold text-amber-900">{result.latency.scann_ms}ms</span>
                          </div>
                          <span className="text-[10px] text-amber-600">Matching Engine VM</span>
                        </div>

                        <div className="p-2 rounded-lg bg-red-50 border border-red-100">
                          <div className="flex items-center justify-between mb-0.5">
                            <span className="text-red-700 font-medium">3. Firestore</span>
                            <span className="font-mono font-bold text-red-900">{result.latency.firestore_ms}ms</span>
                          </div>
                          <span className="text-[10px] text-red-600">Resolusi Teks Payload</span>
                        </div>

                        <div className="p-2 rounded-lg bg-emerald-50 border border-emerald-100">
                          <div className="flex items-center justify-between mb-0.5">
                            <span className="text-emerald-700 font-medium">4. Gemini LLM</span>
                            <span className="font-mono font-bold text-emerald-900">{result.latency.llm_ms}ms</span>
                          </div>
                          <span className="text-[10px] text-emerald-600">gemini-3.5-flash-lite</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* 2. Trade-off Visualizer: ScaNN Datapoint IDs vs Firestore Resolved Text */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
                        <Layers className="w-4 h-4 text-amber-600" />
                        <span>Trade-off Inti Vector Search 1.0: Pemisahan ID Vektor & Teks Payload</span>
                      </h3>
                      <p className="text-xs text-slate-500">
                        Vector Search 1.0 <strong>hanya mengembalikan ID</strong> dan jarak kemiripan. Teks aktual harus ditarik dari Cloud Firestore secara terpisah.
                      </p>
                    </div>
                    <span className="text-xs font-mono bg-slate-100 px-2 py-1 rounded text-slate-600">
                      {result.chunks?.length || 0} Chunks Terambil
                    </span>
                  </div>

                  {/* Dual Inspector Comparison */}
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                    {/* Left: Raw ScaNN Output */}
                    <div className="lg:col-span-4 bg-slate-900 text-slate-200 p-3.5 rounded-xl text-xs font-mono space-y-2 border border-slate-800">
                      <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-2">
                        <span className="font-bold text-amber-400">Tahap 2: Output ScaNN VM</span>
                        <span className="text-[10px]">Hanya ID & Distance</span>
                      </div>
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {result.raw_datapoints?.map((dp, idx) => (
                          <div key={idx} className="bg-slate-800/80 p-2 rounded border border-slate-700/60 space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="text-emerald-400 font-bold">#{idx + 1}</span>
                              <span className="text-slate-400 text-[10px]">Distance: {dp.distance.toFixed(4)}</span>
                            </div>
                            <div className="text-slate-300 break-all">{dp.id}</div>
                            <div className="text-[10px] text-amber-400/90 italic">⚠️ Payload teks tidak ada</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Right: Resolved Firestore Text */}
                    <div className="lg:col-span-8 space-y-3">
                      <div className="flex items-center space-x-2 text-xs font-bold text-slate-700 pb-1">
                        <Database className="w-3.5 h-3.5 text-blue-600" />
                        <span>Tahap 3: Teks yang Diresolusi dari Cloud Firestore</span>
                      </div>

                      <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
                        {result.chunks?.map((chunk, idx) => (
                          <div key={idx} className="border border-slate-200 rounded-xl p-3.5 bg-slate-50/50 space-y-2 text-xs">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <span className="bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded text-[11px]">
                                  #{idx + 1}
                                </span>
                                <span className="font-semibold text-slate-800">{chunk.source_doc}</span>
                                <span className="text-slate-400">· Halaman {chunk.page_num}</span>
                              </div>
                              <span className="font-mono text-slate-500 text-[11px]">
                                ID: <span className="text-slate-700 font-medium">{chunk.datapoint_id}</span>
                              </span>
                            </div>
                            <p className="text-slate-700 whitespace-pre-wrap leading-relaxed bg-white p-2.5 rounded border border-slate-100 font-sans">
                              {chunk.text}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* 3. Comparison with Scenario 2 */}
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-2xl p-5 text-xs text-amber-950 space-y-2">
                  <h4 className="font-bold text-sm text-amber-900 flex items-center space-x-2">
                    <ShieldCheck className="w-4 h-4 text-amber-700" />
                    <span>Catatan Arsitektur: Perbandingan Langsung dengan Skenario 2 (Agent Retrieval)</span>
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                    <div className="space-y-1">
                      <strong className="text-amber-900">Skenario 1 (Vector Search 1.0):</strong>
                      <p className="text-slate-700 leading-relaxed">
                        Memerlukan <strong>4 tahap terpisah</strong> (Embed client-side &rarr; ScaNN ANN &rarr; Firestore lookup &rarr; LLM).
                        Memerlukan pengelolaan VM dedicated (<code className="bg-amber-100 px-1 py-0.5 rounded font-mono">e2-standard-2</code>)
                        dengan waktu deploy 20–30 menit dan penagihan komputasi kontinu per jam.
                      </p>
                    </div>
                    <div className="space-y-1">
                      <strong className="text-blue-900">Skenario 2 (Agent Retrieval / VS 2.0):</strong>
                      <p className="text-slate-700 leading-relaxed">
                        Hanya <strong>2 tahap</strong> (Query &rarr; SearchDataObjects &rarr; LLM).
                        Payload teks tersimpan bersama vektor di dalam <code className="bg-blue-100 px-1 py-0.5 rounded font-mono">DataObject</code>,
                        dengan auto-embedding server-side dan arsitektur serverless instan tanpa biaya VM siaga.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 2: DOKUMEN SUMBER (4 PDF KEBIJAKAN CYMBAL INDONESIA)  */}
        {/* ======================================================== */}
        {activeTab === 'docs' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-900">Paket Kebijakan HR PT Cymbal Indonesia (Dataset Uji)</h2>
              <p className="text-xs text-slate-500">
                Empat dokumen PDF berbahasa Indonesia yang dirancang untuk menguji trade-off arsitektur pencarian semantik murni, kata kunci/kode, tabel multikolom, dan aturan jam kerja/WFA.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {documents.map((doc, idx) => (
                <div key={idx} className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2.5">
                      <div className="p-2 bg-amber-50 text-amber-700 rounded-lg">
                        <FileText className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-slate-900">{doc.title}</h3>
                        <span className="font-mono text-xs text-slate-400">{doc.code}</span>
                      </div>
                    </div>
                    <span className="text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium border border-slate-200">
                      {doc.filename}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed">{doc.description}</p>

                  <div className="border-t border-slate-100 pt-3 flex items-center justify-between text-xs">
                    <span className="text-slate-400">Sasaran Pengujian:</span>
                    <span className="font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 text-[11px]">
                      {doc.test_target}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 3: BENCHMARK GOLDEN QUERIES                          */}
        {/* ======================================================== */}
        {activeTab === 'benchmark' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-slate-900">Hasil Evaluasi Terstandarisasi: Golden Queries</h2>
                <p className="text-xs text-slate-500">
                  Data hasil uji otomatis dari skrip <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">eval_golden.py</code> pada Skenario 1.
                </p>
              </div>
              <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2.5 py-1 rounded">
                eval_results.json
              </span>
            </div>

            {benchmarks.length === 0 ? (
              <div className="bg-white rounded-xl border border-slate-200 p-8 text-center space-y-3">
                <BarChart3 className="w-8 h-8 text-slate-400 mx-auto" />
                <h3 className="text-sm font-semibold text-slate-700">Belum ada data evaluasi tersimpan</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Jalankan skrip evaluasi CLI di terminal untuk menghasilkan data benchmark:
                </p>
                <code className="inline-block bg-slate-900 text-emerald-400 px-3 py-1.5 rounded font-mono text-xs">
                  python eval_golden.py
                </code>
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                    <tr>
                      <th className="py-3 px-4">ID</th>
                      <th className="py-3 px-4">Kategori Uji</th>
                      <th className="py-3 px-4">Pertanyaan</th>
                      <th className="py-3 px-4">Dokumen Target</th>
                      <th className="py-3 px-4">Kecocokan</th>
                      <th className="py-3 px-4 text-right">ScaNN</th>
                      <th className="py-3 px-4 text-right">Firestore</th>
                      <th className="py-3 px-4 text-right">LLM</th>
                      <th className="py-3 px-4 text-right">Total Latensi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {benchmarks.map((b, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/70 transition">
                        <td className="py-3 px-4 font-mono font-bold text-slate-700">{b.id}</td>
                        <td className="py-3 px-4 font-medium text-slate-800">{b.category}</td>
                        <td className="py-3 px-4 text-slate-600 max-w-xs truncate italic">"{b.query}"</td>
                        <td className="py-3 px-4 text-slate-500">{b.expected_doc?.replace('.pdf', '')}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                            b.doc_matched?.includes('YA') ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {b.doc_matched}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-slate-600">{b.latency?.scann_ms}ms</td>
                        <td className="py-3 px-4 text-right font-mono text-slate-600">{b.latency?.firestore_ms}ms</td>
                        <td className="py-3 px-4 text-right font-mono text-slate-600">{b.latency?.llm_ms}ms</td>
                        <td className="py-3 px-4 text-right font-mono font-bold text-amber-700">{b.latency?.total_ms}ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 4: INFRASTRUKTUR & KONTROL (MANAGE_INDEX & RUNBOOK)  */}
        {/* ======================================================== */}
        {activeTab === 'infra' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-900">Manajemen Siklus Hidup Infrastruktur Vertex AI Vector Search 1.0</h2>
              <p className="text-xs text-slate-500">
                Panduan operasional dan perintah CLI untuk mengontrol pembuatan indeks, deployment node VM, dan pencegahan penagihan biaya kontinu.
              </p>
            </div>

            {/* Live Status Overview Card */}
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
              <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2">
                <Server className="w-4 h-4 text-amber-600" />
                <span>Status Sumber Daya GCP Aktual (Project: {backendHealth?.project_id})</span>
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                {/* Index Card */}
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-700">MatchingEngineIndex</span>
                    {infraStatus?.index?.exists ? (
                      <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded text-[10px] font-bold">DITEMUKAN</span>
                    ) : (
                      <span className="bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded text-[10px] font-bold">BELUM ADA</span>
                    )}
                  </div>
                  <div className="font-mono text-slate-800 text-[11px] truncate">{infraStatus?.index?.name}</div>
                  <div className="text-slate-500 text-[11px]">Stream Update · 768d · Dot Product</div>
                </div>

                {/* Endpoint Card */}
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-700">IndexEndpoint VM</span>
                    {infraStatus?.endpoint?.is_deployed ? (
                      <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded text-[10px] font-bold">DEPLOYED (ONLINE)</span>
                    ) : (
                      <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded text-[10px] font-bold">UNDEPLOYED</span>
                    )}
                  </div>
                  <div className="font-mono text-slate-800 text-[11px] truncate">{infraStatus?.endpoint?.name}</div>
                  <div className="text-slate-500 text-[11px]">Machine: {infraStatus?.endpoint?.machine_type} · Public Endpoint</div>
                </div>

                {/* Firestore Card */}
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-700">Cloud Firestore DB</span>
                    <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-[10px] font-bold">TERHUBUNG</span>
                  </div>
                  <div className="font-mono text-slate-800 text-[11px] truncate">{infraStatus?.firestore?.collection}</div>
                  <div className="text-slate-500 text-[11px]">{infraStatus?.firestore?.chunk_count} Chunks Dokumen Tersimpan</div>
                </div>
              </div>
            </div>

            {/* CLI Commands Runbook */}
            <div className="bg-slate-900 text-slate-200 rounded-xl p-5 shadow-xs space-y-4">
              <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
                <Terminal className="w-5 h-5 text-amber-400" />
                <h3 className="font-bold text-sm text-white">CLI Commands Cheat Sheet (`manage_index.py` & `ingest.py`)</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700/80 space-y-2">
                  <div className="text-emerald-400 font-bold"># 1. Periksa Status Infrastruktur</div>
                  <div className="text-slate-300">python manage_index.py status</div>
                  <p className="text-[11px] text-slate-400 font-sans">
                    Menampilkan tabel rich status indeks, status deployment VM endpoint, dan jumlah chunk di Firestore.
                  </p>
                </div>

                <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700/80 space-y-2">
                  <div className="text-emerald-400 font-bold"># 2. Buat Index & Endpoint GCP</div>
                  <div className="text-slate-300">python manage_index.py create-index</div>
                  <div className="text-slate-300">python manage_index.py create-endpoint</div>
                  <p className="text-[11px] text-slate-400 font-sans">
                    Membuat resource MatchingEngineIndex (STREAM_UPDATE) dan IndexEndpoint publik di us-central1.
                  </p>
                </div>

                <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700/80 space-y-2">
                  <div className="text-amber-400 font-bold"># 3. Deploy Index ke Endpoint VM (~20-30 mnt)</div>
                  <div className="text-slate-300">python manage_index.py deploy</div>
                  <p className="text-[11px] text-slate-400 font-sans">
                    Menyediakan dedicated node komputasi VM e2-standard-2 untuk melayani kueri ScaNN.
                  </p>
                </div>

                <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700/80 space-y-2">
                  <div className="text-red-400 font-bold"># 4. Undeploy Index (Hentikan Biaya VM)</div>
                  <div className="text-slate-300">python manage_index.py undeploy</div>
                  <p className="text-[11px] text-slate-400 font-sans">
                    Sangat penting! Melepas index dari endpoint agar penagihan biaya VM komputasi berhenti setelah demo.
                  </p>
                </div>

                <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700/80 space-y-2">
                  <div className="text-blue-400 font-bold"># 5. Jalankan Pipeline Ingesti Data</div>
                  <div className="text-slate-300">python ingest.py</div>
                  <p className="text-[11px] text-slate-400 font-sans">
                    Ekstrak PDF, simpan teks chunk ke Firestore, buat embedding gemini-embedding-2, dan upsert ke indeks.
                  </p>
                </div>

                <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700/80 space-y-2">
                  <div className="text-purple-400 font-bold"># 6. Jalankan Evaluasi Golden Queries</div>
                  <div className="text-slate-300">python eval_golden.py</div>
                  <p className="text-[11px] text-slate-400 font-sans">
                    Eksekusi Q1-ID s.d Q4-ID secara otomatis, ukur hit-rate dokumen, dan simpan latensi ke eval_results.json.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* --- FOOTER --- */}
      <footer className="bg-white border-t border-slate-200 py-4 px-4 text-xs text-slate-500 text-center">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-y-2">
          <span>PT Cymbal Indonesia · Demo Perbandingan Arsitektur Retrieval & Search Google Cloud</span>
          <span className="font-mono text-slate-400">Skenario 1: Vector Search 1.0 (Port 3001 / 8001)</span>
        </div>
      </footer>
    </div>
  )
}
