import json
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table

from config import GOLDEN_QUERIES, PROJECT_ID, LOCATION, DATA_STORE_ID, ENGINE_ID
from retriever import AgentSearchRetriever

logging.basicConfig(level=logging.WARNING)
console = Console()


def run_evaluation():
    console.print(f"[bold green]Memulai Evaluasi Golden Queries: Skenario 4 (Agent Search API)[/bold green]")
    console.print(f"Project: [cyan]{PROJECT_ID}[/cyan] | Location: [cyan]{LOCATION}[/cyan] | DataStore: [cyan]{DATA_STORE_ID}[/cyan] | Engine: [cyan]{ENGINE_ID}[/cyan]\n")

    retriever = AgentSearchRetriever()
    results = []

    for item in GOLDEN_QUERIES:
        qid = item["id"]
        category = item["category"]
        query = item["query"]
        expected_doc = item["source_doc"]

        console.print(f"[bold yellow]Menguji {qid} ({category})[/bold yellow]: \"{query}\"")

        try:
            eval_res = retriever.search_and_answer(query, top_k=4)

            docs = [c["source_doc"] for c in eval_res.get("chunks", [])]
            top_doc = docs[0] if docs else "None"
            doc_matched = any(expected_doc in d for d in docs)

            result_entry = {
                "id": qid,
                "category": category,
                "mode": "turnkey",
                "query": query,
                "expected_doc": expected_doc,
                "retrieved_doc": top_doc,
                "doc_matched": "✅ YA" if doc_matched else "❌ BEDA",
                "retrieval_ms": eval_res.get("retrieval_ms"),
                "generation_ms": eval_res.get("generation_ms"),
                "total_ms": eval_res.get("total_ms"),
                "answer": eval_res.get("answer"),
                "chunks": eval_res.get("chunks", []),
                "citations": eval_res.get("citations", []),
            }
            results.append(result_entry)

            console.print(f"  [bold]Doc Match:[/bold] {'[green]PASS[/green]' if doc_matched else '[red]FAIL[/red]'} (Top: {top_doc})")
            console.print(f"  [bold]Latency:[/bold] Total {eval_res.get('total_ms', 0):.1f} ms")
            console.print(f"  [bold]Answer:[/bold] {eval_res.get('answer', '')[:120]}...\n")

        except Exception as e:
            console.print(f"  [bold red]Error:[/bold red] {e}\n")
            results.append({
                "id": qid,
                "category": category,
                "mode": "turnkey",
                "query": query,
                "expected_doc": expected_doc,
                "error": str(e),
                "doc_matched": "❌ ERROR",
            })

    output_file = Path(__file__).parent / "eval_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    console.print(f"Hasil evaluasi tersimpan di [bold cyan]{output_file}[/bold cyan]\n")

    # Tampilkan Ringkasan Tabel
    table = Table(title="Ringkasan Hasil Evaluasi Skenario 4 (Agent Search API)")
    table.add_column("ID", style="cyan")
    table.add_column("Kategori", style="white")
    table.add_column("Dokumen Ditemukan", style="magenta")
    table.add_column("Match", style="green")
    table.add_column("Total Latency (ms)", style="yellow")

    for r in results:
        table.add_row(
            r["id"],
            r["category"],
            r.get("retrieved_doc", "N/A"),
            r.get("doc_matched", "ERROR"),
            f"{r.get('total_ms', 0):.1f}" if r.get("total_ms") else "N/A",
        )
    console.print(table)


if __name__ == "__main__":
    run_evaluation()
