"""
manage_datastore.py - CLI Manajemen Sumber Daya Agent Search (Discovery Engine)
Digunakan untuk memeriksa status DataStore & Engine, membuat, atau memicu ingesti dokumen dari GCS.

Penggunaan:
    python manage_datastore.py status   # Cek status DataStore & Engine di GCP
    python manage_datastore.py create   # Buat DataStore, Engine, dan impor dokumen
    python manage_datastore.py import   # Picu ulang impor dokumen dari GCS
    python manage_datastore.py delete   # Hapus Engine dan DataStore
"""

import sys
import time
import logging
from google.api_core.exceptions import NotFound, AlreadyExists
from google.cloud import discoveryengine_v1 as discoveryengine
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import (
    PROJECT_ID,
    LOCATION,
    COLLECTION_ID,
    DATA_STORE_ID,
    ENGINE_ID,
    DATA_STORE_DISPLAY_NAME,
    ENGINE_DISPLAY_NAME,
    BUCKET_NAME,
    GCS_PREFIX,
    GCS_URI_PATTERN,
)

logging.basicConfig(level=logging.WARNING)
console = Console()


def get_datastore_path() -> str:
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION_ID}/dataStores/{DATA_STORE_ID}"


def get_engine_path() -> str:
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION_ID}/engines/{ENGINE_ID}"


def get_branch_path() -> str:
    return f"{get_datastore_path()}/branches/0"


def get_serving_config_path() -> str:
    # Prefer engine serving config if engine exists, else datastore serving config
    return f"{get_engine_path()}/servingConfigs/default_search"


def get_datastore_client() -> discoveryengine.DataStoreServiceClient:
    return discoveryengine.DataStoreServiceClient()


def get_engine_client() -> discoveryengine.EngineServiceClient:
    return discoveryengine.EngineServiceClient()


def get_document_client() -> discoveryengine.DocumentServiceClient:
    return discoveryengine.DocumentServiceClient()


def get_datastore_info() -> dict:
    ds_client = get_datastore_client()
    eng_client = get_engine_client()
    doc_client = get_document_client()

    info = {
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "collection_id": COLLECTION_ID,
        "datastore_id": DATA_STORE_ID,
        "engine_id": ENGINE_ID,
        "datastore_exists": False,
        "engine_exists": False,
        "document_count": 0,
        "state": "NOT_FOUND",
        "serving_config": get_serving_config_path(),
    }

    try:
        ds = ds_client.get_data_store(name=get_datastore_path())
        info["datastore_exists"] = True
        info["datastore_display_name"] = ds.display_name
        info["industry_vertical"] = ds.industry_vertical.name
        info["content_config"] = ds.content_config.name
        info["state"] = "DATASTORE_READY"
    except NotFound:
        return info
    except Exception as e:
        info["error"] = str(e)
        return info

    try:
        eng = eng_client.get_engine(name=get_engine_path())
        info["engine_exists"] = True
        info["engine_display_name"] = eng.display_name
        info["state"] = "READY"
    except NotFound:
        info["state"] = "ENGINE_MISSING"
    except Exception as e:
        info["engine_error"] = str(e)

    # Check documents in default branch
    try:
        docs = list(doc_client.list_documents(parent=get_branch_path(), page_size=10))
        info["document_count"] = len(docs)
    except Exception:
        pass

    return info


def print_status():
    info = get_datastore_info()
    table = Table(title="[bold blue]Status Agen Search / Discovery Engine (Indonesia)[/bold blue]")
    table.add_column("Properti", style="cyan")
    table.add_column("Nilai", style="green")

    table.add_row("Project ID", info["project_id"])
    table.add_row("Location", info["location"])
    table.add_row("Data Store ID", info["datastore_id"])
    table.add_row("Data Store Status", "✅ Aktif" if info["datastore_exists"] else "❌ Belum dibuat")
    table.add_row("Search Engine ID", info["engine_id"])
    table.add_row("Search Engine Status", "✅ Aktif" if info["engine_exists"] else "❌ Belum dibuat")
    table.add_row("Serving Config", info["serving_config"])
    table.add_row("Dokumen Terindeks", str(info.get("document_count", "0+")))
    table.add_row("GCS Source Pattern", GCS_URI_PATTERN)

    console.print(table)


def create_resources():
    info = get_datastore_info()
    ds_client = get_datastore_client()
    eng_client = get_engine_client()
    doc_client = get_document_client()

    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION_ID}"

    # 1. Create DataStore if not exists
    if not info["datastore_exists"]:
        console.print(f"[yellow]▶ Membuat DataStore: {DATA_STORE_ID}...[/yellow]")
        data_store = discoveryengine.DataStore(
            display_name=DATA_STORE_DISPLAY_NAME,
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        )
        operation = ds_client.create_data_store(
            parent=parent,
            data_store=data_store,
            data_store_id=DATA_STORE_ID,
        )
        console.print("   Menunggu inisialisasi DataStore...")
        operation.result(timeout=180)
        console.print("   ✅ DataStore berhasil dibuat.")
    else:
        console.print("   ✅ DataStore sudah ada.")

    # 2. Create Engine if not exists
    if not info["engine_exists"]:
        console.print(f"[yellow]▶ Membuat Search Engine: {ENGINE_ID}...[/yellow]")
        try:
            engine = discoveryengine.Engine(
                display_name=ENGINE_DISPLAY_NAME,
                solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
                search_engine_config=discoveryengine.Engine.SearchEngineConfig(
                    search_tier=discoveryengine.SearchTier.SEARCH_TIER_ENTERPRISE,
                    search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM],
                ),
                data_store_ids=[DATA_STORE_ID],
            )
            op = eng_client.create_engine(
                parent=parent,
                engine=engine,
                engine_id=ENGINE_ID,
            )
            console.print("   Menunggu inisialisasi Engine...")
            op.result(timeout=180)
            console.print("   ✅ Search Engine berhasil dibuat.")
        except AlreadyExists:
            console.print("   ✅ Search Engine sudah ada.")
        except Exception as e:
            console.print(f"[bold red]   Peringatan saat membuat engine:[/bold red] {e}")
    else:
        console.print("   ✅ Search Engine sudah ada.")

    # 3. Import Documents from GCS
    trigger_import()


def trigger_import():
    doc_client = get_document_client()
    console.print(f"[yellow]▶ Memicu impor dokumen dari {GCS_URI_PATTERN}...[/yellow]")
    try:
        request = discoveryengine.ImportDocumentsRequest(
            parent=get_branch_path(),
            gcs_source=discoveryengine.GcsSource(
                input_uris=[GCS_URI_PATTERN],
                data_schema="content",
            ),
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
        )
        op = doc_client.import_documents(request=request)
        console.print(f"   Operasi impor berjalan: {op.operation.name}")
        console.print("   ✅ Impor dokumen berhasil dipicu ke Agent Search.")
    except Exception as e:
        console.print(f"[bold red]   Error saat memicu impor:[/bold red] {e}")


def delete_resources():
    ds_client = get_datastore_client()
    eng_client = get_engine_client()

    console.print(f"[red]▶ Menghapus Search Engine {ENGINE_ID}...[/red]")
    try:
        op = eng_client.delete_engine(name=get_engine_path())
        op.result(timeout=120)
        console.print("   ✅ Engine dihapus.")
    except NotFound:
        console.print("   Engine tidak ditemukan.")
    except Exception as e:
        console.print(f"   Error menghapus engine: {e}")

    console.print(f"[red]▶ Menghapus DataStore {DATA_STORE_ID}...[/red]")
    try:
        op = ds_client.delete_data_store(name=get_datastore_path())
        op.result(timeout=120)
        console.print("   ✅ DataStore dihapus.")
    except NotFound:
        console.print("   DataStore tidak ditemukan.")
    except Exception as e:
        console.print(f"   Error menghapus datastore: {e}")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "status":
        print_status()
    elif action == "create":
        create_resources()
    elif action == "import":
        trigger_import()
    elif action == "delete":
        delete_resources()
    else:
        print("Penggunaan: python manage_datastore.py [status|create|import|delete]")
