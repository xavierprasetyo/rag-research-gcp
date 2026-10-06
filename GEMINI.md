# Repository Instructions & Memories: vector-search-gcp

- **Dedicated GCP Project:** `rag-research-sandbox` (Project Number: `1031440951381`)
- **Folder:** `default` (`535427245754`) under Organization `xavierprasetyo.altostrat.com` (`988773729671`)
- **Billing Account:** `0144CC-5C8DC9-05B66D` (Argolis Billing (xavierprasetyo))
- **GCP Account:** `admin@xavierprasetyo.altostrat.com`
- **Default Location / Region:** `us-central1`
- When testing the project, use commands that are not long-lived so they return values immediately.
- **Cloud Run Service:** `cymbal-hr-unified-portal` (Region: `us-central1`, IAM Locked Down: `user:admin@xavierprasetyo.altostrat.com`)
- **Cloud Run Proxy Command (for local authenticated web browsing):**
  ```bash
  gcloud run services proxy cymbal-hr-unified-portal \
    --region=us-central1 \
    --project=rag-research-sandbox \
    --port=8080 \
    --account=admin@xavierprasetyo.altostrat.com
  ```
  Then browse to `http://localhost:8080` (auto-injects identity token).
- **GitHub Repository:** `git@github.com:xavierprasetyo/rag-research-gcp.git`
