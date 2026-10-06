#!/usr/bin/env python3
"""
manage_index.py — Vertex AI Vector Search 1.0 Infrastructure Lifecycle Manager
Mengelola pembuatan Index, IndexEndpoint, deployment VM, dan undeployment untuk Skenario 1.
"""

import argparse
import logging
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from google.cloud import aiplatform
from google.cloud import firestore

from config import (
    PROJECT_ID,
    LOCATION,
    INDEX_DISPLAY_NAME,
    ENDPOINT_DISPLAY_NAME,
    DEPLOYED_INDEX_ID,
    MACHINE_TYPE,
    DISTANCE_MEASURE_TYPE,
    EMBEDDING_DIMENSIONS,
    APPROXIMATE_NEIGHBORS_COUNT,
    LEAF_NODE_EMBEDDING_COUNT,
    LEAF_NODES_TO_SEARCH_PERCENT,
    FIRESTORE_COLLECTION,
    FIRESTORE_DATABASE,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("manage_index")
console = Console()


def init_aiplatform():
    """Initializes Vertex AI SDK with project and region."""
    aiplatform.init(project=PROJECT_ID, location=LOCATION)


def find_index():
    """Finds existing MatchingEngineIndex by display name."""
    init_aiplatform()
    indexes = aiplatform.MatchingEngineIndex.list(project=PROJECT_ID, location=LOCATION)
    for idx in indexes:
        if idx.display_name == INDEX_DISPLAY_NAME:
            return idx
    return None


def find_endpoint():
    """Finds existing MatchingEngineIndexEndpoint by display name."""
    init_aiplatform()
    endpoints = aiplatform.MatchingEngineIndexEndpoint.list(project=PROJECT_ID, location=LOCATION)
    for ep in endpoints:
        if ep.display_name == ENDPOINT_DISPLAY_NAME:
            # Re-instantiate with full resource name to initialize _public_match_client
            return aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=ep.resource_name)
    return None


def get_firestore_chunk_count() -> int:
    """Returns number of chunks currently stored in Firestore."""
    try:
        db = firestore.Client(project=PROJECT_ID, database=FIRESTORE_DATABASE)
        docs = db.collection(FIRESTORE_COLLECTION).stream()
        return sum(1 for _ in docs)
    except Exception as e:
        logger.warning("Could not read Firestore collection '%s': %s", FIRESTORE_COLLECTION, e)
        return -1


def show_status():
    """Prints comprehensive infrastructure status."""
    console.print(Panel.fit("[bold cyan]Status Infrastruktur Vertex AI Vector Search 1.0 (Skenario 1)[/bold cyan]"))
    init_aiplatform()

    index = find_index()
    endpoint = find_endpoint()
    firestore_count = get_firestore_chunk_count()

    table = Table(title="Komponen & Sumber Daya GCP")
    table.add_column("Komponen", style="cyan", no_wrap=True)
    table.add_column("Nama / Resource", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Keterangan Tambahan", style="dim")

    # Index Status
    if index:
        table.add_row(
            "MatchingEngineIndex",
            f"{index.display_name}\n({index.resource_name})",
            "[green]DITEMUKAN[/green]",
            f"Dimensi: {EMBEDDING_DIMENSIONS} | Stream Update"
        )
    else:
        table.add_row(
            "MatchingEngineIndex",
            INDEX_DISPLAY_NAME,
            "[yellow]BELUM ADA[/yellow]",
            "Jalankan: python manage_index.py create-index"
        )

    # Endpoint Status & Deployment Status
    is_deployed = False
    deployed_info = ""
    if endpoint:
        deployed_indexes = endpoint.deployed_indexes
        for d in deployed_indexes:
            if d.id == DEPLOYED_INDEX_ID:
                is_deployed = True
                deployed_info = f"Deployed ID: {d.id} (Index: {d.index})"
                break

        status_text = "[green]ONLINE (DEPLOYED)[/green]" if is_deployed else "[yellow]CREATED (UNDEPLOYED)[/yellow]"
        table.add_row(
            "MatchingEngineIndexEndpoint",
            f"{endpoint.display_name}\n({endpoint.resource_name})",
            status_text,
            deployed_info or f"VM Machine Type: {MACHINE_TYPE} (undeployed)"
        )
    else:
        table.add_row(
            "MatchingEngineIndexEndpoint",
            ENDPOINT_DISPLAY_NAME,
            "[yellow]BELUM ADA[/yellow]",
            "Jalankan: python manage_index.py create-endpoint"
        )

    # Firestore Status
    if firestore_count >= 0:
        table.add_row(
            "Cloud Firestore",
            f"Collection: {FIRESTORE_COLLECTION}",
            f"[green]{firestore_count} Chunks Tersimpan[/green]",
            f"Database: {FIRESTORE_DATABASE}"
        )
    else:
        table.add_row(
            "Cloud Firestore",
            f"Collection: {FIRESTORE_COLLECTION}",
            "[red]GAGAL TERHUBUNG[/red]",
            "Periksa autentikasi atau inisialisasi database Firestore"
        )

    console.print(table)

    if is_deployed:
        console.print("[bold red]PERINGATAN BIAYA:[/bold red] Endpoint sedang aktif dan menagih komputasi per jam. Jalankan `python manage_index.py undeploy` jika demo selesai untuk menghentikan VM.")
    elif endpoint and index:
        console.print("[dim]Endpoint belum di-deploy ke VM. Jalankan `python manage_index.py deploy` untuk mengaktifkan node pencarian (~20-30 menit).[/dim]")


def create_index():
    """Creates a MatchingEngineIndex configured for stream updates and gemini-embedding-2."""
    init_aiplatform()
    index = find_index()
    if index:
        console.print(f"[green]Index '{INDEX_DISPLAY_NAME}' sudah ada:[/green] {index.resource_name}")
        return index

    console.print(f"[bold yellow]Membuat MatchingEngineIndex '{INDEX_DISPLAY_NAME}'...[/bold yellow]")
    console.print(f"Project: {PROJECT_ID} | Region: {LOCATION} | Dimensi: {EMBEDDING_DIMENSIONS}")

    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=INDEX_DISPLAY_NAME,
        dimensions=EMBEDDING_DIMENSIONS,
        approximate_neighbors_count=APPROXIMATE_NEIGHBORS_COUNT,
        distance_measure_type=DISTANCE_MEASURE_TYPE,
        index_update_method="STREAM_UPDATE",
        leaf_node_embedding_count=LEAF_NODE_EMBEDDING_COUNT,
        leaf_nodes_to_search_percent=LEAF_NODES_TO_SEARCH_PERCENT,
        description="Indeks Vector Search 1.0 untuk Dokumen HR PT Cymbal Indonesia",
        sync=True,
    )
    console.print(f"[bold green]Index berhasil dibuat:[/bold green] {index.resource_name}")
    return index


def create_endpoint():
    """Creates a public MatchingEngineIndexEndpoint."""
    init_aiplatform()
    endpoint = find_endpoint()
    if endpoint:
        console.print(f"[green]Endpoint '{ENDPOINT_DISPLAY_NAME}' sudah ada:[/green] {endpoint.resource_name}")
        return endpoint

    console.print(f"[bold yellow]Membuat MatchingEngineIndexEndpoint '{ENDPOINT_DISPLAY_NAME}' (public_endpoint_enabled=True)...[/bold yellow]")
    endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=ENDPOINT_DISPLAY_NAME,
        description="Public Index Endpoint untuk Agen FAQ HR Indonesia",
        public_endpoint_enabled=True,
        sync=True,
    )
    console.print(f"[bold green]Endpoint berhasil dibuat:[/bold green] {endpoint.resource_name}")
    return endpoint


def deploy_index(sync: bool = True):
    """Deploys the index to the endpoint with e2-standard-2 VM machine type."""
    init_aiplatform()
    index = find_index()
    if not index:
        console.print("[bold red]Index belum dibuat. Jalankan `create-index` terlebih dahulu.[/bold red]")
        sys.exit(1)

    endpoint = find_endpoint()
    if not endpoint:
        console.print("[bold red]Endpoint belum dibuat. Jalankan `create-endpoint` terlebih dahulu.[/bold red]")
        sys.exit(1)

    # Check if already deployed
    for d in endpoint.deployed_indexes:
        if d.id == DEPLOYED_INDEX_ID:
            console.print(f"[green]Index sudah ter-deploy di endpoint dengan ID: '{DEPLOYED_INDEX_ID}'[/green]")
            return

    console.print(f"[bold yellow]Memulai deployment index ke endpoint VM ({MACHINE_TYPE})...[/bold yellow]")
    console.print("[dim]Proses penyediaan VM pada Vector Search 1.0 membutuhkan waktu sekitar 20–30 menit.[/dim]")

    endpoint.deploy_index(
        index=index,
        deployed_index_id=DEPLOYED_INDEX_ID,
        display_name=f"{INDEX_DISPLAY_NAME}-deployment",
        machine_type=MACHINE_TYPE,
        min_replica_count=1,
        max_replica_count=1,
        sync=sync,
    )
    if sync:
        console.print(f"[bold green]Index berhasil di-deploy ke endpoint![/bold green] Deployed Index ID: {DEPLOYED_INDEX_ID}")
    else:
        console.print(f"[bold green]Operasi deployment telah dikirim ke GCP (LRO Async)![/bold green] VM {MACHINE_TYPE} sedang disiapkan (~20-30 mnt). Jalankan `python manage_index.py status` untuk memantau.")


def undeploy_index(sync: bool = True):
    """Undeploys the index to stop VM compute charges."""
    init_aiplatform()
    endpoint = find_endpoint()
    if not endpoint:
        console.print("[yellow]Endpoint tidak ditemukan.[/yellow]")
        return

    is_deployed = any(d.id == DEPLOYED_INDEX_ID for d in endpoint.deployed_indexes)
    if not is_deployed:
        console.print(f"[yellow]Index dengan ID '{DEPLOYED_INDEX_ID}' tidak sedang ter-deploy di endpoint.[/yellow]")
        return

    console.print(f"[bold yellow]Meng-undeploy index '{DEPLOYED_INDEX_ID}' dari endpoint untuk menghentikan VM...[/bold yellow]")
    endpoint.undeploy_index(deployed_index_id=DEPLOYED_INDEX_ID, sync=sync)
    if sync:
        console.print("[bold green]Index berhasil di-undeploy. Biaya VM komputasi telah dihentikan.[/bold green]")
    else:
        console.print("[bold green]Permintaan undeploy terkirim (LRO Async). Biaya komputasi akan segera dihentikan.[/bold green]")


def delete_endpoint():
    """Deletes the MatchingEngineIndexEndpoint (must be undeployed first)."""
    init_aiplatform()
    endpoint = find_endpoint()
    if not endpoint:
        console.print("[yellow]Endpoint tidak ditemukan.[/yellow]")
        return

    if endpoint.deployed_indexes:
        console.print("[bold red]Endpoint masih memiliki deployed index. Jalankan `undeploy` terlebih dahulu.[/bold red]")
        return

    console.print(f"[bold yellow]Menghapus MatchingEngineIndexEndpoint '{endpoint.display_name}'...[/bold yellow]")
    endpoint.delete(sync=True)
    console.print("[bold green]Endpoint berhasil dihapus dari GCP.[/bold green]")


def delete_index():
    """Deletes the MatchingEngineIndex."""
    init_aiplatform()
    index = find_index()
    if not index:
        console.print("[yellow]Index tidak ditemukan.[/yellow]")
        return

    console.print(f"[bold yellow]Menghapus MatchingEngineIndex '{index.display_name}'...[/bold yellow]")
    index.delete(sync=True)
    console.print("[bold green]Index berhasil dihapus dari GCP.[/bold green]")


def main():
    parser = argparse.ArgumentParser(description="Kelola Siklus Hidup Vertex AI Vector Search 1.0")
    subparsers = parser.add_subparsers(dest="command", help="Perintah yang tersedia")

    subparsers.add_parser("status", help="Periksa status Index, Endpoint, dan Firestore")
    subparsers.add_parser("create-index", help="Buat MatchingEngineIndex (STREAM_UPDATE, 768d)")
    subparsers.add_parser("create-endpoint", help="Buat MatchingEngineIndexEndpoint (public)")

    deploy_parser = subparsers.add_parser("deploy", help="Deploy index ke endpoint VM (memerlukan waktu ~20-30 mnt)")
    deploy_parser.add_argument("--async", "--no-wait", dest="async_mode", action="store_true", help="Jalankan operasi deployment secara asynchronous di latar belakang")

    undeploy_parser = subparsers.add_parser("undeploy", help="Undeploy index dari endpoint untuk menghemat biaya VM")
    undeploy_parser.add_argument("--async", "--no-wait", dest="async_mode", action="store_true", help="Jalankan operasi undeploy secara asynchronous di latar belakang")

    subparsers.add_parser("delete-endpoint", help="Hapus MatchingEngineIndexEndpoint (harus undeployed)")
    subparsers.add_parser("delete-index", help="Hapus MatchingEngineIndex")

    args = parser.parse_args()

    if args.command == "status" or not args.command:
        show_status()
    elif args.command == "create-index":
        create_index()
    elif args.command == "create-endpoint":
        create_endpoint()
    elif args.command == "deploy":
        deploy_index(sync=not getattr(args, "async_mode", False))
    elif args.command == "undeploy":
        undeploy_index(sync=not getattr(args, "async_mode", False))
    elif args.command == "delete-endpoint":
        delete_endpoint()
    elif args.command == "delete-index":
        delete_index()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
