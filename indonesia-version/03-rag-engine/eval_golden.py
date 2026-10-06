import json
import logging
import sys
from pathlib import Path
import time
from tabulate import tabulate
from rich.console import Console
from rich.table import Table

from config import GOLDEN_QUERIES, LLM_MODEL, CORPUS_DISPLAY_NAME, PROJECT_ID, LOCATION
from retriever import RagEngineRetriever

logging.basicConfig(level=logging.WARNING)
console = Console()


def run_evaluation():
    console.print(f"[bold green]Starting Golden Queries Evaluation: Scenario 3 (RAG Engine)[/bold green]")
    console.print(f"Project: [cyan]{PROJECT_ID}[/cyan] | Location: [cyan]{LOCATION}[/cyan] | Corpus: [cyan]{CORPUS_DISPLAY_NAME}[/cyan] | LLM: [cyan]{LLM_MODEL}[/cyan]\n")

    retriever = RagEngineRetriever()
    results = []

    for item in GOLDEN_QUERIES:
        qid = item["id"]
        category = item["category"]
        query = item["query"]
        expected_doc = item["source_doc"]

        # "tool" is the native VertexRagStore path; "retrieve" exposes retrieval vs. generation latency
        modes_to_test = ["tool", "retrieve"]

        for mode in modes_to_test:
            mode_label = f"{mode.upper()}"
            console.print(f"[bold yellow]Evaluating {qid} ({category}) [[{mode_label}]][/bold yellow]: \"{query}\"")

            eval_res = retriever.generate_answer(query, mode=mode, top_k=4)

            docs = [c["source_doc"] for c in eval_res["chunks"]]
            top_doc = docs[0] if docs else "None"
            doc_matched = expected_doc in docs

            result_entry = {
                "id": qid,
                "category": category,
                "mode": mode,
                "query": query,
                "expected_doc": expected_doc,
                "retrieved_doc": top_doc,
                "doc_matched": "✅ YA" if doc_matched else "❌ BEDA",
                "retrieval_ms": eval_res["retrieval_ms"],
                "generation_ms": eval_res["generation_ms"],
                "total_ms": eval_res["total_ms"],
                "answer": eval_res["answer"],
                "chunks": eval_res["chunks"],
            }
            results.append(result_entry)

            console.print(f"  [bold]Doc Match:[/bold] {'[green]PASS[/green]' if doc_matched else '[red]FAIL[/red]'} (Top: {top_doc})")
            console.print(f"  [bold]Latency:[/bold] Retrieval {eval_res['retrieval_ms'] or 'n/a'} ms | Generation {eval_res['generation_ms'] or 'n/a'} ms | Total {eval_res['total_ms']} ms")
            console.print(f"  [bold]Jawaban:[/bold] {eval_res['answer']}\n")

    # Summary table
    table = Table(title="Hasil Evaluasi Golden Queries (Versi Indonesia)", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Kategori", width=18)
    table.add_column("Mode", width=10)
    table.add_column("Dokumen Benar (top-4)", width=18)
    table.add_column("Retrieval (ms)", justify="right", width=14)
    table.add_column("LLM (ms)", justify="right", width=12)
    table.add_column("Total (ms)", justify="right", width=12)

    for r in results:
        table.add_row(
            r["id"],
            r["category"],
            r["mode"].upper(),
            f"{r['doc_matched']} {r['retrieved_doc'][:16]}...",
            str(r["retrieval_ms"]),
            str(r["generation_ms"]),
            f"{r['total_ms']:.1f}",
        )

    console.print(table)

    # Save output to JSON
    output_path = str(Path(__file__).parent / "eval_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    console.print(f"\n[green]Hasil evaluasi lengkap disimpan ke:[/green] {output_path}")

    return results


if __name__ == "__main__":
    run_evaluation()
