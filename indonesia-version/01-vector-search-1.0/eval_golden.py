#!/usr/bin/env python3
"""
eval_golden.py — Evaluasi Pertanyaan Baku (Golden Queries) untuk Skenario 1: Vector Search 1.0
Menjalankan pengujian otomatis untuk Q1-ID s.d Q4-ID, mencatat akurasi dokumen sumber,
rincian latensi 4-tahap, dan menyimpan hasil ke eval_results.json.
"""

import json
import logging
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config import (
    GOLDEN_QUERIES,
    PROJECT_ID,
    LOCATION,
    INDEX_DISPLAY_NAME,
    ENDPOINT_DISPLAY_NAME,
    DEPLOYED_INDEX_ID,
    FIRESTORE_COLLECTION,
    LLM_MODEL,
    EMBEDDING_MODEL,
)
from retriever import VS1Retriever

logging.basicConfig(level=logging.WARNING)
console = Console()
OUTPUT_FILE = Path(__file__).resolve().parent / "eval_results.json"


def run_evaluation():
    console.print(Panel.fit("[bold green]Mulai Evaluasi Golden Queries: Skenario 1 (Vector Search 1.0)[/bold green]"))
    console.print(
        f"GCP Project: [cyan]{PROJECT_ID}[/cyan] | Region: [cyan]{LOCATION}[/cyan] | Endpoint: [cyan]{ENDPOINT_DISPLAY_NAME}[/cyan]\n"
        f"Embedding: [cyan]{EMBEDDING_MODEL}[/cyan] | LLM: [cyan]{LLM_MODEL}[/cyan] | Firestore: [cyan]{FIRESTORE_COLLECTION}[/cyan]\n"
    )

    try:
        retriever = VS1Retriever()
        if not retriever.is_endpoint_deployed():
            console.print(
                "[yellow]PEMBERITAHUAN: MatchingEngineIndexEndpoint belum di-deploy ke VM.[/yellow]\n"
                "[dim]Melanjutkan evaluasi menggunakan Mode Preview (vektor terindeks + Cloud Firestore live + Gemini 3.5 Flash-Lite live)...\n"
                "Jalankan `python manage_index.py deploy` jika ingin mengaktifkan dedicated VM node di GCP.[/dim]\n"
            )
    except Exception as e:
        console.print(f"[bold red]Gagal menginisialisasi retriever:[/bold red] {e}")
        sys.exit(1)

    results = []

    for item in GOLDEN_QUERIES:
        qid = item["id"]
        category = item["category"]
        query = item["query"]
        expected_doc = item["source_doc"]
        expected_topic = item["expected_topic"]

        console.print(f"[bold yellow]Menjalankan {qid} ({category})[/bold yellow]: \"{query}\"")

        try:
            eval_res = retriever.generate_answer(query, top_k=4)
            top_chunk = eval_res["chunks"][0] if eval_res["chunks"] else {}
            top_doc = top_chunk.get("source_doc", "None")
            top_page = top_chunk.get("page_num", 0)
            doc_matched = (top_doc == expected_doc)

            latency = eval_res["latency"]

            result_entry = {
                "id": qid,
                "category": category,
                "query": query,
                "expected_doc": expected_doc,
                "expected_topic": expected_topic,
                "retrieved_doc": f"{top_doc} (Hal {top_page})",
                "doc_matched": "✅ YA" if doc_matched else "❌ BEDA",
                "datapoint_ids": [c["datapoint_id"] for c in eval_res["chunks"]],
                "latency": latency,
                "answer": eval_res["answer"],
                "chunks": eval_res["chunks"],
            }
            results.append(result_entry)

            match_status = "[green]PASS[/green]" if doc_matched else "[red]FAIL[/red]"
            console.print(f"  • Doc Match: {match_status} (Top: {top_doc} Hal {top_page})")
            console.print(
                f"  • Latency: Embed {latency['embedding_ms']}ms | "
                f"ScaNN {latency['scann_ms']}ms | "
                f"Firestore {latency['firestore_ms']}ms | "
                f"LLM {latency['llm_ms']}ms | "
                f"[bold]Total {latency['total_ms']}ms[/bold]\n"
            )

        except Exception as e:
            console.print(f"  [bold red]Error mengeksekusi {qid}:[/bold red] {e}\n")
            results.append({
                "id": qid,
                "category": category,
                "query": query,
                "expected_doc": expected_doc,
                "error": str(e),
            })

    # Simpan hasil evaluasi ke JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    console.print(f"[bold green]Hasil evaluasi disimpan ke:[/bold green] {OUTPUT_FILE}\n")

    # Tampilkan Tabel Ringkasan
    summary_table = Table(title="Ringkasan Hasil Evaluasi: Skenario 1 (Vector Search 1.0)")
    summary_table.add_column("ID", style="bold cyan")
    summary_table.add_column("Kategori", style="white")
    summary_table.add_column("Target Dokumen", style="dim")
    summary_table.add_column("Hasil Retrieval", style="white")
    summary_table.add_column("Kecocokan", style="bold")
    summary_table.add_column("ScaNN", justify="right")
    summary_table.add_column("Firestore", justify="right")
    summary_table.add_column("LLM", justify="right")
    summary_table.add_column("Total Latensi", justify="right", style="bold green")

    for r in results:
        if "error" in r:
            summary_table.add_row(r["id"], r["category"], r["expected_doc"], "ERROR", "[red]ERROR[/red]", "-", "-", "-", "-")
        else:
            lat = r["latency"]
            summary_table.add_row(
                r["id"],
                r["category"],
                r["expected_doc"].replace(".pdf", ""),
                r["retrieved_doc"].replace(".pdf", ""),
                r["doc_matched"],
                f"{lat['scann_ms']}ms",
                f"{lat['firestore_ms']}ms",
                f"{lat['llm_ms']}ms",
                f"{lat['total_ms']}ms",
            )

    console.print(summary_table)


if __name__ == "__main__":
    run_evaluation()
