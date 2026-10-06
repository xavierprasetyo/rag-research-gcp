import React, { useState } from 'react';
import {
  FolderInput,
  FileSearch,
  SplitSquareVertical,
  Binary,
  Database,
  Sparkles,
  Search,
  SlidersHorizontal,
  MessageSquareCheck,
  Server,
  CheckCircle2,
  Code2,
  Layers,
  ArrowRight,
  AlertCircle,
  HelpCircle,
  Table,
  LayoutGrid
} from 'lucide-react';

export default function GenerativeSearchArchitecture({ onSelectScenario }) {
  const [activeScenario, setActiveScenario] = useState('all'); // 'all', 'diff', 's1', 's2', 's3', 's4', 's5'
  const [viewMode, setViewMode] = useState('pipeline'); // 'pipeline' | 'matrix'

  // The 10 canonical steps of a modern generative search system (strictly product-agnostic titles & definitions)
  const ingestionSteps = [
    {
      id: 'connect',
      stepNum: '01',
      title: 'Connect to your data',
      processDefinition: 'Ingesting raw documents, database records, and streaming enterprise feeds into the pipeline',
      question: 'How do I get my data, from wherever it is, into the pipeline?',
      icon: FolderInput,
      scenarioMapping: {
        s1: {
          type: 'customer',
          label: 'Customer Built: Custom upload pipeline pushing PDF files into cloud storage buckets manually.',
        },
        s2: {
          type: 'customer',
          label: 'Customer Built: Custom application client formatting and pushing raw JSON DataObjects into collections.',
        },
        s3: {
          type: 'managed',
          label: 'Google Managed: Direct Cloud Storage import synchronization and managed connector ingestion.',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: Turnkey enterprise connectors for Cloud Storage, BigQuery, and enterprise drives.',
        },
        s5: {
          type: 'managed',
          label: 'Google Managed: Turnkey document connector sync combined with live enterprise SQL database connectors.',
        },
      },
    },
    {
      id: 'parsing',
      stepNum: '02',
      title: 'Parsing / Understanding',
      processDefinition: 'Extracting clean text, structural layouts, tables, and media representations from raw formats',
      question: 'How do I process my data to extract information (tables, images etc) and to make it easier to be found later?',
      icon: FileSearch,
      scenarioMapping: {
        s1: {
          type: 'customer',
          label: 'Customer Built: Custom PyPDF parser with basic plaintext extraction (no OCR or table layout reconstruction).',
        },
        s2: {
          type: 'customer',
          label: 'Customer Built: Client-side parsing and text extraction before submitting DataObjects.',
        },
        s3: {
          type: 'managed',
          label: 'Google Managed: Cloud layout parser extracting structured headings, lists, and tabular data.',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: Managed document understanding with digital OCR, layout analysis, and multiformat parsing.',
        },
        s5: {
          type: 'managed',
          label: 'Google Managed: Managed document understanding via DataStore tools + schema reflection on relational DB.',
        },
      },
    },
    {
      id: 'chunking',
      stepNum: '03',
      title: 'Chunking',
      processDefinition: 'Segmenting content into coherent semantic passages while preserving context and metadata',
      question: 'How should I segment while preserving meaning?',
      icon: SplitSquareVertical,
      scenarioMapping: {
        s1: {
          type: 'customer',
          label: 'Customer Built: Custom sliding-window algorithm (500 chars, 80 overlap) without semantic boundary awareness.',
        },
        s2: {
          type: 'customer',
          label: 'Customer Built: Client-defined chunk boundaries and payload slicing prior to collection ingestion.',
        },
        s3: {
          type: 'managed',
          label: 'Google Managed: Automated managed chunking pipeline with configurable token limits and overlap ratios.',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: Intelligent layout-aware chunking preserving paragraph, section, and table boundaries.',
        },
        s5: {
          type: 'managed',
          label: 'Google Managed: Zero-configuration semantic chunking automatically maintained by the DataStore tool.',
        },
      },
    },
    {
      id: 'embedding',
      stepNum: '04',
      title: 'Embedding',
      processDefinition: 'Transforming textual passages into dense numerical vectors capturing semantic meaning',
      question: 'Which vector dimensions? How do I encode Multi-modal?',
      icon: Binary,
      scenarioMapping: {
        s1: {
          type: 'customer',
          label: 'Customer Built: Direct embedding API calls with manual task prefixes (RETRIEVAL_DOCUMENT), batches, and retries.',
        },
        s2: {
          type: 'managed',
          label: 'Google Managed: Automated serverless embedding generation triggered upon DataObject creation in the collection.',
        },
        s3: {
          type: 'managed',
          label: 'Google Managed: Managed embedding model pipeline running automatically on corpus document ingestion.',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: State-of-the-art multilingual dense semantic embeddings natively built into search engine.',
        },
        s5: {
          type: 'managed',
          label: 'Google Managed: Multilingual semantic embeddings natively managed across the search tool data store.',
        },
      },
    },
    {
      id: 'storage',
      stepNum: '05',
      title: 'Storage',
      processDefinition: 'Persisting dense vector indexes, chunk text payloads, and relational metadata for retrieval',
      question: 'How do I store my data to be able to retrieve it later?',
      icon: Database,
      scenarioMapping: {
        s1: {
          type: 'partial',
          label: 'Partially Managed: Vector Search manages the ANN Tree-AH vector index, but customer must manage external database (Firestore) for text & metadata.',
        },
        s2: {
          type: 'managed',
          label: 'Google Managed: Unified Serverless Collection storing both vectors and JSON payload (DataObjects) natively without an external DB.',
        },
        s3: {
          type: 'managed',
          label: 'Google Managed: Fully managed RAG Corpus holding text passages, chunk metadata, and vector representations.',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: Turnkey search data store indexing text, vectors, attributes, and access control policies.',
        },
        s5: {
          type: 'partial',
          label: 'Partially Managed: Managed search DataStore for unstructured documents + Enterprise SQL database for transactional HR records.',
        },
      },
    },
  ];

  const retrievalSteps = [
    {
      id: 'expansion',
      stepNum: '06',
      title: 'Query Expansion & Understanding',
      processDefinition: 'Analyzing user intent, correcting spelling, expanding synonyms, and rewriting search queries',
      question: 'Need to spell check? What about rewording? Extracting filters & rules, conversational search',
      icon: Sparkles,
      scenarioMapping: {
        s1: {
          type: 'customer',
          label: 'Customer Built: Exact query text lookup only; customer must build spellcheck, synonyms, and query rewriting.',
        },
        s2: {
          type: 'customer',
          label: 'Customer Built: Direct semantic/keyword lookup; no automatic intent parsing, typo tolerance, or query rewording.',
        },
        s3: {
          type: 'partial',
          label: 'Partially Managed: Semantic vector distance retrieval; customer must implement conversational query rewriting.',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: Enterprise Google spellcheck, entity extraction, synonym expansion, and intent rewording.',
        },
        s5: {
          type: 'managed',
          label: 'Google Managed: Autonomous agent reasoning loop: decomposes multi-part questions into targeted tool subqueries.',
        },
      },
    },
    {
      id: 'search',
      stepNum: '07',
      title: 'Search & Relevance',
      processDefinition: 'Matching user queries against stored data via dense semantic similarity and keyword algorithms',
      question: 'Find the most relevant list based on semantic search, keywords, filters',
      icon: Search,
      scenarioMapping: {
        s1: {
          type: 'customer',
          label: 'Customer Built: Approximate Nearest Neighbor (ANN) dense vector search only; customer must handle metadata filters.',
        },
        s2: {
          type: 'partial',
          label: 'Partially Managed: Serverless Dense SemanticSearch + Native Keyword TextSearch (BM25) + metadata filtering.',
        },
        s3: {
          type: 'managed',
          label: 'Google Managed: Managed context retrieval API with top-k nearest neighbors and similarity thresholding.',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: Turnkey true Hybrid Search combining dense semantic vectors + sparse BM25 keyword matching.',
        },
        s5: {
          type: 'managed',
          label: 'Google Managed: Autonomous multi-tool execution combining Hybrid Search DataStore + SQL relational query tools.',
        },
      },
    },
    {
      id: 'ranking',
      stepNum: '08',
      title: 'Ranking & Optimization',
      processDefinition: 'Re-ordering candidate results by relevance scoring, freshness, user signals, and business KPIs',
      question: 'Boost fresh results, rank based on user behavior, maximize business KPIs e.g. clicks / revenue',
      icon: SlidersHorizontal,
      scenarioMapping: {
        s1: {
          type: 'customer',
          label: 'Customer Built: Nearest-neighbor cosine distance sorting only; no cross-encoder re-ranking or freshness boosting.',
        },
        s2: {
          type: 'partial',
          label: 'Partially Managed: Supports Reciprocal Rank Fusion (RRF) across dense + keyword results; no cross-encoder re-ranker.',
        },
        s3: {
          type: 'partial',
          label: 'Partially Managed: Managed distance score thresholding and top-k filtering; no cross-encoder re-ranking.',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: Enterprise Google search ranking models, semantic cross-encoders, and freshness boosts.',
        },
        s5: {
          type: 'managed',
          label: 'Google Managed: Agentic self-critique loop: re-evaluates candidate evidence across tools before answering.',
        },
      },
    },
    {
      id: 'grounding',
      stepNum: '09',
      title: 'Grounding, Answer & Conversation',
      processDefinition: 'Synthesizing retrieved contexts into natural language answers with citations and multi-turn state',
      question: 'Prompt Engineering, Tuning, Citations, Agentic iterations, Actions',
      icon: MessageSquareCheck,
      scenarioMapping: {
        s1: {
          type: 'customer',
          label: 'Customer Built: Customer must design prompt templates, inject contexts, invoke LLM, and build citation mappings.',
        },
        s2: {
          type: 'customer',
          label: 'Customer Built: Customer orchestrates prompt engineering, context assembly, and LLM text generation.',
        },
        s3: {
          type: 'customer',
          label: 'Customer Built: RAG Engine itself only manages & retrieves corpus chunks. Customer must invoke the Gemini API separately (passing VertexRagStore directly to the model as a grounding source, or manually prompting with retrieval_query chunks).',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: Turnkey grounded summary generation with clickable inline citations and hallucination checks.',
        },
        s5: {
          type: 'managed',
          label: 'Google Managed: Autonomous agent multi-step reasoning, mathematical calculations, and tool-grounded synthesis.',
        },
      },
    },
    {
      id: 'serving',
      stepNum: '10',
      title: 'Serving',
      processDefinition: 'Serving the end-to-end search or agent application API with secure authentication, low latency, and scale',
      question: 'Will my serving API scale to demand? Is my infra secure?',
      icon: Server,
      scenarioMapping: {
        s1: {
          type: 'customer',
          label: 'Customer Built: Google serves the VM-backed index endpoint, but customer builds and hosts the end-to-end search/RAG API.',
        },
        s2: {
          type: 'customer',
          label: 'Customer Built: Google serves the serverless collection lookup, but customer develops, deploys, and scales the application search API.',
        },
        s3: {
          type: 'customer',
          label: 'Customer Built: Google serves the corpus retrieval API, but customer must build, deploy, and host the end-to-end search/answer API.',
        },
        s4: {
          type: 'managed',
          label: 'Google Managed: Turnkey search & answer endpoint fully hosted by Google with global SLA and auto-scaling.',
        },
        s5: {
          type: 'partial',
          label: 'Partially Managed: Google ADK provides the built-in Runner and session state management; customer hosts the agent application API.',
        },
      },
    },
  ];

  const allSteps = [...ingestionSteps, ...retrievalSteps];

  const scenarioTabs = [
    { id: 'all', label: 'All Architectures' },
    { id: 's1', label: 'S1: Vector Search 1.0 (Dedicated)' },
    { id: 's2', label: 'S2: Agent Retrieval (Serverless)' },
    { id: 's3', label: 'S3: RAG Engine (Corpus Retrieval)' },
    { id: 's4', label: 'S4: Agent Search API (Turnkey)' },
    { id: 's5', label: 'S5: Agent ADK (Multi-Tool)' },
  ];

  const renderBadge = (type) => {
    if (type === 'managed') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          Google Managed
        </span>
      );
    }
    if (type === 'partial') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40">
          <SlidersHorizontal className="w-3 h-3 text-amber-400" />
          Partially Managed
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
        <Code2 className="w-3 h-3 text-indigo-400" />
        Customer Built
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="border-b border-slate-800 pb-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <Layers className="w-5 h-5" />
              </span>
              <h2 className="text-xl md:text-2xl font-bold text-white tracking-tight">
                Steps of a Modern Generative Search
              </h2>
            </div>
            <p className="text-sm text-slate-400 mt-1 max-w-3xl">
              Generic product-agnostic lifecycle separating{' '}
              <span className="text-indigo-300 font-semibold">Data Ingestion (Preparation)</span> from{' '}
              <span className="text-emerald-300 font-semibold">Data Retrieval & Serving (Runtime)</span>.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* View Mode Toggle */}
            <div className="inline-flex p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              <button
                onClick={() => setViewMode('pipeline')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                  viewMode === 'pipeline'
                    ? 'bg-slate-700 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <LayoutGrid className="w-3.5 h-3.5" /> Pipeline View
              </button>
              <button
                onClick={() => setViewMode('matrix')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                  viewMode === 'matrix'
                    ? 'bg-slate-700 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Table className="w-3.5 h-3.5" /> Side-by-Side Diff
              </button>
            </div>
          </div>
        </div>

        {/* Scenario Filter Bar */}
        <div className="mt-4 flex flex-wrap items-center gap-1.5">
          {scenarioTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveScenario(tab.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeScenario === tab.id
                  ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/40 ring-1 ring-indigo-400'
                  : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Legend Ribbon */}
        <div className="mt-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-slate-400 font-semibold">
            <HelpCircle className="w-4 h-4 text-indigo-400" />
            <span>Responsibility Color Code:</span>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50"></span>
              <span className="text-slate-300 font-medium">Google Managed</span>
              <span className="text-[11px] text-slate-500 hidden sm:inline">(Turnkey platform automation)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50"></span>
              <span className="text-slate-300 font-medium">Partially Managed</span>
              <span className="text-[11px] text-slate-500 hidden sm:inline">(Co-managed / split responsibility)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-indigo-500 shadow-sm shadow-indigo-500/50"></span>
              <span className="text-slate-300 font-medium">Customer Built</span>
              <span className="text-[11px] text-slate-500 hidden sm:inline">(Requires developer code & ops)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Critical Architecture Distinctions Banner */}
      <div className="p-4 rounded-2xl bg-slate-900/80 border border-indigo-500/30 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div className="flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-amber-300">Application Serving vs. Storage (S1 vs. S2):</span>
            <p className="text-slate-300 leading-relaxed">
              Step 10 (<strong>Serving</strong>) measures serving the end-to-end search or agent application API, which is <strong>Customer Built</strong> in S1 &amp; S2. Meanwhile, <strong>Storage (Step 05)</strong> moves from <strong>Partially Managed</strong> in S1 (index only; requires external Firestore for text) to <strong>Google Managed</strong> in S2 (unified serverless <code>DataObjects</code> storing both vectors and JSON payloads + native BM25/RRF).
            </p>
          </div>
        </div>
        <div className="flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-indigo-300">RAG Engine vs. Agent Search API (S3 vs. S4):</span>
            <p className="text-slate-300 leading-relaxed">
              Out-of-the-box, RAG Engine only manages &amp; retrieves corpus chunks; to generate answers, the customer must invoke the <strong>Gemini API separately</strong> (passing <code>VertexRagStore</code> directly to the model as a grounding source, or manually prompting with <code>retrieval_query</code> chunks). Agent Search API is <strong>turnkey</strong> with built-in answer generation &amp; hosted serving in one endpoint.
            </p>
          </div>
        </div>
      </div>

      {viewMode === 'pipeline' ? (
        /* 2-ROW PIPELINE VIEW */
        <div className="space-y-10">
          {/* ROW 1: PREPARATION (DATA INGESTION) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold tracking-wider uppercase">
                <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
                Preparation • Data Ingestion Pipeline
              </div>
              <span className="text-xs text-slate-400 hidden sm:inline">
                Steps 01 - 05: Raw enterprise inputs to indexed representations
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5">
              {ingestionSteps.map((step) => {
                const IconComponent = step.icon;
                const mapping = activeScenario !== 'all' ? step.scenarioMapping[activeScenario] : null;

                return (
                  <div
                    key={step.id}
                    className="rounded-2xl bg-slate-800/40 border border-slate-700/80 hover:border-indigo-500/60 p-4 flex flex-col justify-between transition-all group relative overflow-hidden"
                  >
                    <div className="space-y-2.5">
                      {/* Top Step Icon & Step Number */}
                      <div className="flex items-center justify-between">
                        <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:bg-indigo-500/20 group-hover:scale-105 transition-all">
                          <IconComponent className="w-4.5 h-4.5" />
                        </div>
                        <span className="text-[11px] font-mono text-slate-400">Step {step.stepNum}</span>
                      </div>

                      {/* Process Title */}
                      <div>
                        <h4 className="text-xs font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                          {step.title}
                        </h4>
                        {/* Brief Product-Agnostic Process Definition */}
                        <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                          {step.processDefinition}
                        </p>
                      </div>

                      {/* Guiding Question */}
                      <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                        <p className="text-[11px] text-slate-300 leading-relaxed italic">
                          "{step.question}"
                        </p>
                      </div>
                    </div>

                    {/* Scenario Implementation Details */}
                    {mapping && (
                      <div className="mt-3 pt-3 border-t border-slate-700/60 space-y-1.5">
                        <div className="flex items-center justify-between">
                          {renderBadge(mapping.type)}
                        </div>
                        <p className="text-[11px] text-slate-300 font-medium leading-snug">
                          {mapping.label}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Flow Connector Divider */}
          <div className="relative flex items-center justify-center my-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-dashed border-slate-700"></div>
            </div>
            <div className="relative px-4 bg-[#0b0f19] text-xs font-mono text-slate-400 flex items-center gap-2">
              <span>Offline Corpus Sync</span>
              <ArrowRight className="w-3.5 h-3.5 text-indigo-400" />
              <span>Online Serving Runtime</span>
            </div>
          </div>

          {/* ROW 2: RUNTIME (DATA RETRIEVAL & SERVING) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold tracking-wider uppercase">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                Runtime • Data Retrieval & Serving Pipeline
              </div>
              <span className="text-xs text-slate-400 hidden sm:inline">
                Steps 06 - 10: User intent to verified answer & agent actions
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5">
              {retrievalSteps.map((step) => {
                const IconComponent = step.icon;
                const mapping = activeScenario !== 'all' ? step.scenarioMapping[activeScenario] : null;

                return (
                  <div
                    key={step.id}
                    className="rounded-2xl bg-slate-800/40 border border-slate-700/80 hover:border-emerald-500/60 p-4 flex flex-col justify-between transition-all group relative overflow-hidden"
                  >
                    <div className="space-y-2.5">
                      {/* Top Step Icon & Step Number */}
                      <div className="flex items-center justify-between">
                        <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500/20 group-hover:scale-105 transition-all">
                          <IconComponent className="w-4.5 h-4.5" />
                        </div>
                        <span className="text-[11px] font-mono text-slate-400">Step {step.stepNum}</span>
                      </div>

                      {/* Process Title */}
                      <div>
                        <h4 className="text-xs font-bold text-slate-100 group-hover:text-emerald-300 transition-colors">
                          {step.title}
                        </h4>
                        {/* Brief Product-Agnostic Process Definition */}
                        <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                          {step.processDefinition}
                        </p>
                      </div>

                      {/* Guiding Question */}
                      <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                        <p className="text-[11px] text-slate-300 leading-relaxed italic">
                          "{step.question}"
                        </p>
                      </div>
                    </div>

                    {/* Scenario Implementation Details */}
                    {mapping && (
                      <div className="mt-3 pt-3 border-t border-slate-700/60 space-y-1.5">
                        <div className="flex items-center justify-between">
                          {renderBadge(mapping.type)}
                        </div>
                        <p className="text-[11px] text-slate-300 font-medium leading-snug">
                          {mapping.label}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : (
        /* SIDE-BY-SIDE MATRIX / DIFF VIEW */
        <div className="overflow-x-auto rounded-2xl border border-slate-700/80 bg-slate-900/60">
          <table className="w-full text-left text-xs text-slate-300 min-w-[950px]">
            <thead className="bg-slate-800 text-slate-300 uppercase tracking-wider text-[11px] border-b border-slate-700">
              <tr>
                <th className="py-3 px-4 font-semibold">Step / Process</th>
                <th className="py-3 px-3 font-semibold text-slate-300">S1: Vector Search 1.0</th>
                <th className="py-3 px-3 font-semibold text-slate-300">S2: Agent Retrieval</th>
                <th className="py-3 px-3 font-semibold text-slate-300">S3: RAG Engine</th>
                <th className="py-3 px-3 font-semibold text-slate-300">S4: Agent Search API</th>
                <th className="py-3 px-3 font-semibold text-slate-300">S5: Agent ADK</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {allSteps.map((step) => (
                <tr key={step.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-medium text-white max-w-[220px]">
                    <div className="flex items-center gap-1.5 font-bold">
                      <span className="text-[10px] text-indigo-400 font-mono">[{step.stepNum}]</span>
                      <span>{step.title}</span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5 line-clamp-2">
                      {step.processDefinition}
                    </div>
                  </td>
                  {['s1', 's2', 's3', 's4', 's5'].map((scId) => {
                    const m = step.scenarioMapping[scId];
                    return (
                      <td key={scId} className="py-3 px-3 align-top max-w-[190px]">
                        <div className="space-y-1">
                          {renderBadge(m.type)}
                          <p className="text-[10px] text-slate-300 leading-tight">
                            {m.label.split(':')[1] || m.label}
                          </p>
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
