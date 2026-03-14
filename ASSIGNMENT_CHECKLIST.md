# Assignment Checklist — KubeFlow Pipelines Zero to Hero

This checklist maps the [YouTube video](https://www.youtube.com/watch?v=5iOQcGfcZe4) (**KubeFlow Pipelines Zero to Hero with a Realtime MLOps Project** by Abhishek Veeramalla) and the [GitHub Gist](https://gist.github.com/iam-veeramalla/0e569b5e9da68736e51eda78a895212d) to what this project contains and what you have done.

---

## What the video asks for

### 1. Concepts (theory)
- What is Kubeflow, why Kubeflow, ML lifecycle, MLOps
- Kubeflow components (KFP, KServe, Notebooks, Katib, etc.)
- **KFP** = Kubeflow Pipelines — like CI/CD for ML (data load → train → evaluate)
- Pipelines: Python + DSL → compile to YAML → run as pods on Kubernetes

| Asked in video | Done / Where |
|----------------|--------------|
| Understand MLOps & KFP role | ✓ README and project docs |

### 2. Installation (video steps)
- Install **Docker Desktop**
- Install **KIND** (Kubernetes in Docker)
- Create cluster: `kind create cluster --name kfp-demo-yt`
- Install **KFP on Kubernetes** (CRDs + `kubectl apply` from [Kubeflow docs](https://www.kubeflow.org/docs/components/pipelines/operator-guides/installation/))
- Port-forward ML Pipeline UI to access dashboard (e.g. localhost:80)

| Asked in video | Done in this repo |
|----------------|-------------------|
| KIND cluster + KFP on K8s + official UI | ❌ Not in this repo. You would do this on your machine with Docker + KIND. |
| Python venv + `pip install kfp==2.9.0` | ✓ We use `.venv` and `requirements.txt` (kfp version may differ for Python 3.14). |

### 3. Hello World pipeline (video + Gist)
- Write **hello_pipeline.py**: `@dsl.component` for `say_hello(name)`, `@dsl.pipeline` for `hello_pipeline(recipient)`
- Compile: `python hello_pipeline.py` → **hello_world_pipeline.yaml**
- Upload YAML to KFP dashboard → Create run → Pass parameter (e.g. "abhishek") → See "Hello abhishek" in logs

| Asked in video / Gist | Done in this repo |
|------------------------|-------------------|
| hello_pipeline.py with say_hello + hello_pipeline | ✓ **hello_world_pipeline.py** added (matches Gist 02-hello_pipeline.py) |
| Compile to hello_world_pipeline.yaml | ✓ Run `python hello_world_pipeline.py` to generate it |
| Upload to KFP UI and run with parameter | ⚠️ Requires KFP installed on K8s (step 2). Our **Flask UI** can compile; for “upload and run on cluster” you use the real KFP dashboard. |

### 4. Iris ML pipeline (video + Gist)
- Write **iris_pipeline.py**:  
  - Component **load_data** (Iris dataset, pandas + scikit-learn)  
  - Component **train_model** (RandomForest, train/test split, accuracy)  
  - `@dsl.component` with `base_image` and `packages_to_install`  
  - `@dsl.pipeline` that runs load_data → train_model
- Compile to **iris_pipeline.yaml**
- Upload to KFP dashboard → Create run → See DAG (load-data, train-model) and logs (e.g. accuracy 0.9)

| Asked in video / Gist | Done in this repo |
|------------------------|-------------------|
| iris_pipeline.py (load_data + train_model + pipeline) | ✓ **iris_pipeline.py** (same logic; we use python:3.10-slim for kfp 2.16 compatibility) |
| Compile to iris_pipeline.yaml | ✓ **iris_pipeline.yaml** present; compile via `python iris_pipeline.py` or “Compile pipeline” in UI |
| Upload to KFP UI and run on cluster | ⚠️ Same as above: use real KFP dashboard when you have K8s + KFP. |
| Run pipeline (see accuracy) | ✓ **Run test (in-process)** and **Run pipeline (Docker)** in our Flask UI run the same workflow and show output/accuracy. |

---

## What we have in this folder (summary)

| Item | Status |
|------|--------|
| **iris_pipeline.py** | ✓ Matches video/Gist Iris pipeline (load_data, train_model, compile). |
| **iris_pipeline.yaml** | ✓ Compiled Iris pipeline; regenerate with `python iris_pipeline.py`. |
| **hello_world_pipeline.py** | ✓ Added to match video/Gist hello world example. |
| **hello_world_pipeline.yaml** | ✓ Generate with `python hello_world_pipeline.py`. |
| **README.md** | ✓ Describes KFP, MLOps, project structure, usage. |
| **requirements.txt** | ✓ kfp, flask, docker, scikit-learn. |
| **Compile pipelines** | ✓ From CLI or via UI “Compile pipeline” (Iris); you can add Hello compile in UI if needed. |
| **Run Iris workflow** | ✓ “Run test (in-process)” and “Run pipeline (Docker)” in UI. |
| **Web UI (Flask)** | ✓ Professional UI at http://127.0.0.1:5050 to compile and run (no K8s required). |
| **KIND + KFP on Kubernetes** | ❌ Not automated here; follow video + [Kubeflow installation docs](https://www.kubeflow.org/docs/components/pipelines/operator-guides/installation/) and [Gist 01-Installation.md](https://gist.github.com/iam-veeramalla/0e569b5e9da68736e51eda78a895212d). |
| **Official KFP dashboard** | ❌ Use when you have KFP installed on a cluster; then upload hello_world_pipeline.yaml and iris_pipeline.yaml and create runs as in the video. |

---

## How to complete the “video way” (upload + run on cluster)

1. **Install (as in video)**  
   Docker → KIND → create cluster → install KFP on Kubernetes (see [Gist – Installation](https://gist.github.com/iam-veeramalla/0e569b5e9da68736e51eda78a895212d) and [Kubeflow Pipelines installation](https://www.kubeflow.org/docs/components/pipelines/operator-guides/installation/)).

2. **Port-forward and open UI**  
   e.g. `kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80` → open http://localhost:8080.

3. **Hello World**  
   - Run `python hello_world_pipeline.py` in this repo.  
   - In KFP UI: Upload pipeline → choose **hello_world_pipeline.yaml** → Create run → set `recipient` (e.g. "abhishek") → Start → Check logs for “Hello abhishek”.

4. **Iris**  
   - Run `python iris_pipeline.py` in this repo.  
   - In KFP UI: Upload pipeline → choose **iris_pipeline.yaml** → Create run → Start → See DAG and logs with accuracy.

---

## Short answers

- **Have we done it like the video?**  
  **Partly.** We have the same **pipelines** (Hello World + Iris), **DSL usage**, and **compile to YAML**. We added a **local Flask UI** to compile and run without Kubernetes. The **exact** video flow (KIND + KFP on K8s + upload YAML to official UI) you do on your side with Docker/KIND and the steps above.

- **What is asked in the video?**  
  Install KFP on Kubernetes, write Hello World and Iris pipelines with KFP DSL, compile to YAML, upload to the KFP dashboard, and run pipelines (Hello with a parameter, Iris to see accuracy).

- **What have we done here?**  
  Implemented both pipelines (Hello World + Iris), compile to YAML, a professional UI to compile and run the Iris pipeline locally (in-process and Docker), and this checklist so you can align with the video and Gist step by step.
