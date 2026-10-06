"""
manage_collection.py - CLI Manajemen Sumber Daya Agent Retrieval (Vector Search 2.0)
Digunakan untuk memeriksa status collection serverless, membuat, menghapus, atau mengelola koleksi di GCP.

Penggunaan:
    python manage_collection.py status     # Cek status Collection di GCP
    python manage_collection.py create     # Buat Collection jika belum ada
    python manage_collection.py delete     # Hapus Collection dari GCP
    python manage_collection.py reingest   # Jalankan ulang ingesti data
"""

import json
import logging
import sys
from pathlib import Path

from google.api_core.exceptions import NotFound
from google.cloud import vectorsearch_v1beta as vs
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import (
    COLLECTION_ID,
    PROJECT_ID,
    LOCATION,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    TEXT_TEMPLATE,
    CHUNKS_CACHE_FILE,
)

logging.basicConfig(level=logging.WARNING)
console = Console()


def get_collection_path() -> str:
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION_ID}"


def get_parent_location_path() -> str:
    return f"projects/{PROJECT_ID}/locations/{LOCATION}"


def get_client() -> vs.VectorSearchServiceClient:
    return vs.VectorSearchServiceClient()


def get_collection_info() -> dict:
    """Mengembalikan metadata status Collection untuk digunakan oleh server.py dan CLI."""
    col_path = get_collection_path()
    client = get_client()

    chunk_count = 0
    if CHUNKS_CACHE_FILE.exists():
        try:
            with open(CHUNKS_CACHE_FILE, "r", encoding="utf-8") as f:
                chunk_count = len(json.load(f))
        except Exception:
            pass

    try:
        col = client.get_collection(name=col_path)
        return {
            "exists": True,
            "resource_name": col.name,
            "display_name": col.display_name or COLLECTION_ID,
            "description": col.description,
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "collection_id": COLLECTION_ID,
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimensions": EMBEDDING_DIMENSIONS,
            "text_template": TEXT_TEMPLATE,
            "chunk_count": chunk_count,
            "type": "Serverless Collection (Auto-Embedding + Text Storage)",
            "status": "ACTIVE",
        }
    except NotFound:
        return {
            "exists": False,
            "resource_name": col_path,
            "display_name": COLLECTION_ID,
            "description": "",
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "collection_id": COLLECTION_ID,
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimensions": EMBEDDING_DIMENSIONS,
            "text_template": TEXT_TEMPLATE,
            "chunk_count": chunk_count,
            "type": "Serverless Collection",
            "status": "NOT_FOUND",
        }
    except Exception as e:
        return {
            "exists": False,
            "error": str(e),
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "collection_id": COLLECTION_ID,
            "chunk_count": chunk_count,
            "status": "ERROR",
        }


def show_status():
    """Menampilkan status tabel Rich di terminal."""
    console.print(
        Panel(
            "[bold cyan]Status Infrastruktur Agent Retrieval (Skenario 2: Versi Indonesia)[/bold cyan]\n"
            f"[dim]Project: {PROJECT_ID} | Region: {LOCATION} | Collection: {COLLECTION_ID}[/dim]",
            expand=False,
        )
    )

    info = get_collection_info()

    table = Table(title="Komponen & Sumber Daya Serverless GCP", show_header=True, header_style="bold magenta")
    table.add_column("Komponen", style="bold", width=22)
    table.add_column("Nama / Resource", width=32)
    table.add_column("Status", width=16)
    table.add_column("Keterangan Tambahan", width=35)

    if info.get("status") == "ACTIVE":
        col_status = "[bold green]TERHUBUNG (ACTIVE)[/bold green]"
        col_desc = (
            f"Model: {info.get('embedding_model', EMBEDDING_MODEL)} ({info.get('embedding_dimensions', EMBEDDING_DIMENSIONS)}d)\n"
            f"Chunks Terindeks: {info.get('chunk_count', 0)} DataObjects\n"
            "Hosting: Serverless (Instant, Pay-per-query)"
        )
    elif info.get("status") == "NOT_FOUND":
        col_status = "[bold red]BELUM DIBUAT[/bold red]"
        col_desc = "Jalankan `python manage_collection.py create` atau `python ingest.py`"
    else:
        col_status = f"[bold yellow]{info.get('status', 'UNKNOWN')}[/bold yellow]"
        col_desc = info.get("error", "")

    table.add_row(
        "Agent Retrieval Collection",
        f"{COLLECTION_ID}\n[dim]{info.get('resource_name', '')[:30]}...[/dim]",
        col_status,
        col_desc,
    )

    chunk_cnt = info.get("chunk_count", 0)
    cache_status = f"[green]{chunk_cnt} Chunks Tersedia[/green]" if chunk_cnt > 0 else "[yellow]Kosong[/yellow]"
    table.add_row(
        "Local Document Cache",
        "chunks_cache.json",
        cache_status,
        f"Lokasi: {CHUNKS_CACHE_FILE.name}",
    )

    console.print(table)


def create_collection():
    """Membuat collection jika belum ada."""
    from ingest import ensure_collection
    client = get_client()
    col_name = ensure_collection(client)
    console.print(f"[bold green]✅ Collection siap digunakan:[/bold green] {col_name}")


def delete_collection():
    """Menghapus collection dari GCP."""
    client = get_client()
    col_path = get_collection_path()
    console.print(f"[bold red]Menghapus collection:[/bold red] {col_path}...")
    try:
        op = client.delete_collection(name=col_path)
        console.print("[yellow]Menunggu proses penghapusan selesai di GCP...[/yellow]")
        op.result()
        console.print(f"[bold green]✅ Collection '{COLLECTION_ID}' berhasil dihapus dari GCP.[/bold green]")
    except NotFound:
        console.print(f"[yellow]Collection '{COLLECTION_ID}' sudah tidak ada di GCP.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Gagal menghapus collection:[/bold red] {e}")


def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Gunakan salah satu perintah berikut:[/bold red]")
        console.print("  python manage_collection.py status")
        console.print("  python manage_collection.py create")
        console.print("  python manage_collection.py delete")
        console.print("  python manage_collection.py reingest")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        show_status()
    elif cmd in ("create", "create-collection"):
        create_collection()
    elif cmd in ("delete", "delete-collection"):
        delete_collection()
    elif cmd == "reingest":
        from ingest import main as run_ingest
        run_ingest()
    else:
        console.print(f"[bold red]Perintah tidak dikenal:[/bold red] {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
