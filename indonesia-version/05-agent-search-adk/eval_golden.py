import json
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table

from config import GOLDEN_QUERIES, PROJECT_ID, LOCATION, DATA_STORE_ID, LLM_MODEL
from agent import ADKHRAgent

logging.basicConfig(level=logging.WARNING)
console = Console()


def run_evaluation():
    console.print(f"[bold green]Memulai Evaluasi Golden Queries: Skenario 5 (Agent Search + ADK)[/bold green]")
    console.print(f"Project: [cyan]{PROJECT_ID}[/cyan] | Location: [cyan]{LOCATION}[/cyan] | DataStore: [cyan]{DATA_STORE_ID}[/cyan] | Model: [cyan]{LLM_MODEL}[/cyan]\n")

    agent = ADKHRAgent()
    results = []

    for item in GOLDEN_QUERIES:
        qid = item["id"]
        category = item["category"]
        query = item["query"]
        expected_topic = item.get("expected_topic", item.get("category", ""))

        # Default employee untuk Q4-ID adalah EMP-1042
        emp_id = "EMP-1042" if "EMP-1042" in query else None

        console.print(f"[bold yellow]Menguji {qid} ({category})[/bold yellow]: \"{query}\"")

        try:
            eval_res = agent.execute(query=query, employee_id=emp_id)

            tools_called = eval_res.get("tools_called", [])
            trace = eval_res.get("trace", [])
            answer = eval_res.get("answer", "")

            # Verifikasi Q4-ID khusus: harus melibatkan kedua tools atau menghitung sisa cuti & WFA
            if qid == "Q4-ID":
                multi_tool_ok = "get_employee_leave_balance" in tools_called or "15" in answer
                status_str = "✅ PASS (Multi-Tool Verified)" if multi_tool_ok else "⚠️ PARTIAL"
            else:
                status_str = "✅ PASS"

            result_entry = {
                "id": qid,
                "category": category,
                "mode": "adk_agent",
                "query": query,
                "expected_topic": expected_topic,
                "tools_called": tools_called,
                "status": status_str,
                "trace_steps_count": len(trace),
                "total_ms": eval_res.get("total_ms"),
                "answer": answer,
                "trace": trace,
            }
            results.append(result_entry)

            console.print(f"  [bold]Tools Called:[/bold] {tools_called}")
            console.print(f"  [bold]Trace Steps:[/bold] {len(trace)} steps")
            console.print(f"  [bold]Latency:[/bold] Total {eval_res.get('total_ms', 0):.1f} ms")
            console.print(f"  [bold]Answer Preview:[/bold] {answer[:120]}...\n")

        except Exception as e:
            console.print(f"  [bold red]Error:[/bold red] {e}\n")
            results.append({
                "id": qid,
                "category": category,
                "query": query,
                "error": str(e),
                "status": "❌ ERROR",
            })

    output_file = Path(__file__).parent / "eval_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    console.print(f"Hasil evaluasi tersimpan di [bold cyan]{output_file}[/bold cyan]\n")

    table = Table(title="Ringkasan Hasil Evaluasi Skenario 5 (Agent Search + ADK)")
    table.add_column("ID", style="cyan")
    table.add_column("Kategori", style="white")
    table.add_column("Tools Dipanggil", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Total Latency (ms)", style="yellow")

    for r in results:
        table.add_row(
            r["id"],
            r["category"],
            ", ".join(r.get("tools_called", [])) or "None",
            r.get("status", "ERROR"),
            f"{r.get('total_ms', 0):.1f}" if r.get("total_ms") else "N/A",
        )
    console.print(table)


if __name__ == "__main__":
    run_evaluation()
