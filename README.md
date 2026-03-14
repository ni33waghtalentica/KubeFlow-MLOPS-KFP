# Kubeflow Pipelines — MLOps Project

*Created for Shankar's Assignments.*

## Project Idea

This repository demonstrates **Kubeflow Pipelines (KFP)** as the orchestration layer for machine learning workflows. The goal is to show how ML steps can be defined as **reusable, containerized pipeline components** and run in a reproducible way—**locally** (in-process or with Docker) or on a **Kubernetes** cluster using the official KFP dashboard (KIND + KFP).

### What This Project Contains

- **Web app** (`app.py`) — Flask UI to compile pipelines, run tests, and manage a local **KIND** cluster with Kubeflow Pipelines. Open **http://127.0.0.1:5050** after running `python app.py`.
- **Pipelines** (Python KFP v2 DSL, compiled to YAML):
  - **Hello World** — Single component that greets a name; good for verifying the setup.
  - **Iris ML** — Load Iris dataset → train Random Forest → report accuracy.
  - **Animal Species** — Demo pipeline for animal species (single step).
  - **Nationality type** — Demo pipeline for nationality classification.
  - **Viruses** — Demo pipeline for virus-related processing.
  - **Sentiment Check** — Demo pipeline for text sentiment (single step).
  - **Data Summary** — Demo pipeline for dataset summary (single step).

All pipelines can be **compiled** from the app or CLI, and **uploaded to the KFP dashboard** in one click from the app (server-side upload avoids browser "Failed to fetch" errors).

---

## Project Structure

```
KubeFlow-MLOPS-KFP-main/
├── README.md
├── app.py                          # Flask app: compile, run, KFP on Kubernetes
├── static/
│   └── index.html                  # Web UI
├── requirements.txt
├── hello_world_pipeline.py         # Hello World pipeline
├── hello_world_pipeline.yaml
├── iris_pipeline.py                # Iris ML pipeline (load_data → train_model)
├── iris_pipeline.yaml
├── animal_species_pipeline.py
├── animal_species_pipeline.yaml
├── nationality_type_pipeline.py
├── nationality_type_pipeline.yaml
├── viruses_pipeline.py
├── viruses_pipeline.yaml
├── sentiment_check_pipeline.py
├── sentiment_check_pipeline.yaml
├── data_summary_pipeline.py
├── data_summary_pipeline.yaml
├── test_pipeline_inprocess.py      # Run Iris in-process (no Docker)
├── run_local.py                    # Run Iris with KFP local + Docker
└── scripts/
    ├── setup_kind_kfp.sh           # Create KIND cluster + install KFP
    ├── verify_kfp.sh              # Wait for UI, apply fixes (MinIO, POD_NAMES)
    └── kind-config.yaml            # KIND config (fixed API port 36443)
```

---

## Prerequisites

- **Python 3.10+** (recommended; project uses `python:3.10-slim` in components)
- **pip**: `pip install -r requirements.txt` (includes `kfp`, `flask`, `scikit-learn`, `pandas`, `docker` for local runs)
- **Optional — KFP on Kubernetes:** Docker Desktop, [kind](https://kind.sigs.k8s.io/docs/user/quick-start/), [kubectl](https://kubernetes.io/docs/tasks/tools/). On macOS: `brew install kind`.

---

## Quick Start (Web App)

1. **Install dependencies and start the app:**

   ```bash
   pip install -r requirements.txt
   python app.py
   ```

2. Open **http://127.0.0.1:5050** (or 5051/5052 if 5050 is in use).

3. In the UI you can:
   - **Compile** any pipeline (Iris, Hello World, Animal Species, Nationality type, Viruses, Sentiment Check, Data Summary) to YAML.
   - **Run test (in-process)** — Run the Iris workflow in-process (no Docker).
   - **Run pipeline (Docker)** — Run the Iris pipeline locally with KFP local + Docker.

4. **KFP on Kubernetes (KIND):**
   - Click **Setup KIND + KFP** to create a KIND cluster and install Kubeflow Pipelines (takes several minutes).
   - After pods are ready, click **Start KFP Dashboard** to port-forward the UI to **http://localhost:8080**.
   - Click **Upload all pipelines to KFP** to compile and register all pipelines from the app (avoids browser "Failed to fetch" when uploading from the dashboard).
   - In the KFP dashboard, create runs for any uploaded pipeline.

---

## Compile Pipelines (CLI)

Compilation produces YAML that can be uploaded to a KFP backend:

```bash
python hello_world_pipeline.py    # → hello_world_pipeline.yaml
python iris_pipeline.py           # → iris_pipeline.yaml
python animal_species_pipeline.py
python nationality_type_pipeline.py
python viruses_pipeline.py
python sentiment_check_pipeline.py
python data_summary_pipeline.py
```

---

## KFP on Kubernetes (KIND)

The project includes scripts to run the **official Kubeflow Pipelines UI** on a local Kubernetes cluster (KIND).

### Setup

From the project root:

```bash
bash scripts/setup_kind_kfp.sh
```

This will:

- Create a KIND cluster **kfp-demo** (using `scripts/kind-config.yaml` with API port 36443 to avoid conflicts).
- Install Kubeflow Pipelines **2.14.3** (cluster-scoped + platform-agnostic).
- Apply fixes: **MinIO** (official `minio/minio` image + `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD`), **DISABLE_GKE_METADATA** for the UI (non-GKE), and **POD_NAMES=v1** on the workflow-controller so pod log retrieval works in the UI.

Pods may take **3–5 minutes** to become Ready. Check:

```bash
kubectl get pods -n kubeflow
```

### Verify and open dashboard

```bash
bash scripts/verify_kfp.sh
```

Then start port-forward and open the UI:

```bash
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```

Open **http://localhost:8080** in your browser.

### Upload pipelines

- **From the app (recommended):** Click **Upload all pipelines to KFP** so the backend compiles and uploads all pipelines to the KFP API. This avoids "Pipeline version creation failed / Failed to fetch" in the browser.
- **From the dashboard:** Pipelines → + Upload pipeline → choose a compiled `.yaml` from the project folder (compile first via the app or CLI).

Ensure **Start KFP Dashboard** is running (port-forward active) before uploading from the app.

---

## Run Pipelines

- **In-process (no Docker):** Use **Run test (in-process)** in the app, or run `python test_pipeline_inprocess.py`.
- **Local with Docker:** Use **Run pipeline (Docker)** in the app, or run `python run_local.py` (requires Docker).
- **On Kubernetes:** After **Upload all pipelines to KFP**, open the KFP dashboard → Pipelines → select a pipeline → **Create run** → choose experiment (e.g. Default) → Start.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| **Address already in use** (KIND) | Run `kind delete cluster --name kfp-demo`, then run `bash scripts/setup_kind_kfp.sh` again. |
| **Port 5050 in use** | The app will try 5051, 5052. Use the URL printed when you start `python app.py`. |
| **Failed to fetch / Pipeline version creation failed** (upload in dashboard) | Use **Upload all pipelines to KFP** in the app instead; the server uploads to the KFP API and avoids browser/CORS issues. |
| **Failed to retrieve pod logs / podname argument is required** | The scripts set `POD_NAMES=v1` on the workflow-controller. If you installed KFP manually, run: `kubectl set env deployment/workflow-controller -n kubeflow POD_NAMES=v1`. New runs will then show logs. |
| **MinIO ImagePullBackOff** | The setup and verify scripts patch MinIO to use `minio/minio:latest` and add `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` from the existing secret. Re-run `bash scripts/verify_kfp.sh`. |
| **ml-pipeline API CrashLoopBackOff** | Usually because MinIO was not ready. Ensure MinIO is Running (`kubectl get pods -n kubeflow -l app=minio`), then delete the ml-pipeline pod so it restarts: `kubectl delete pod -n kubeflow -l app=ml-pipeline --force --grace-period=0`. |
| **Wrong cluster / connection refused** | Use the KIND context: `kubectl config use-context kind-kfp-demo`. |

---

## How Kubeflow Pipelines Fits Into MLOps

- **Orchestration** — DAG of components with clear order and data flow.
- **Reproducibility** — Versioned pipeline + component specs and container images.
- **Reusability** — Shared components across pipelines (e.g. load_data, train_model).
- **Isolation** — Each step runs in its own container.
- **Scalability** — Kubernetes-backed execution; configurable resources per step.
- **Experiment tracking** — Runs, inputs, and outputs tracked by the KFP backend.
- **Integration** — Fits with object storage (MinIO), model registries, and deployment (e.g. Kubeflow).

---

## References

- [Kubeflow Pipelines documentation](https://www.kubeflow.org/docs/components/pipelines/)
- [KFP Python SDK (v2)](https://www.kubeflow.org/docs/components/pipelines/sdk-v2/)
- [Pipeline YAML spec](https://www.kubeflow.org/docs/components/pipelines/reference/)
- [KIND](https://kind.sigs.k8s.io/docs/user/quick-start/)

---

## License

Use and modify as needed. Kubeflow Pipelines is open source under the Apache License 2.0.
