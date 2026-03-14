#!/usr/bin/env python3
"""Web UI: compile/test pipelines + KIND + KFP on Kubernetes + official KFP dashboard."""
import os
import subprocess
import sys

from flask import Flask, jsonify, request, send_from_directory

# Pipelines to compile and upload: (script, yaml_output, description)
PIPELINES_TO_UPLOAD = [
    ("hello_world_pipeline.py", "hello_world_pipeline.yaml", "Hello World pipeline"),
    ("iris_pipeline.py", "iris_pipeline.yaml", "Iris ML pipeline"),
    ("animal_species_pipeline.py", "animal_species_pipeline.yaml", "Animal Species pipeline"),
    ("nationality_type_pipeline.py", "nationality_type_pipeline.yaml", "Nationality type pipeline"),
    ("viruses_pipeline.py", "viruses_pipeline.yaml", "Viruses pipeline"),
    ("sentiment_check_pipeline.py", "sentiment_check_pipeline.yaml", "Sentiment Check pipeline"),
    ("data_summary_pipeline.py", "data_summary_pipeline.yaml", "Data Summary pipeline"),
]

app = Flask(__name__, static_folder="static")
ROOT = os.path.dirname(os.path.abspath(__file__))
KFP_DASHBOARD_PORT = 8080
_port_forward_proc = None


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Not found"}), 404
    return e


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": str(e)}), 500
    return e


def run_cmd(cmd, cwd=None, timeout=300, env=None):
    cwd = cwd or ROOT
    env = env or os.environ.copy()
    venv = os.path.join(ROOT, ".venv", "bin")
    if os.path.isdir(venv):
        env["PATH"] = venv + os.pathsep + env.get("PATH", "")
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def run_cmd_background(cmd, cwd=None, env=None):
    """Start a process in the background (e.g. port-forward)."""
    cwd = cwd or ROOT
    env = env or os.environ.copy()
    try:
        return subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except Exception as e:
        return None


@app.route("/api/health")
def api_health():
    """Return OK and API version so the UI can verify the server has all routes."""
    return jsonify({
        "ok": True,
        "message": "KFP UI backend",
        "routes": ["/api/compile", "/api/compile-hello", "/api/compile-animal", "/api/compile-nationality", "/api/compile-viruses", "/api/compile-sentiment", "/api/compile-summary", "/api/run-test", "/api/run-local", "/api/k8s/status", "/api/k8s/setup", "/api/k8s/port-forward", "/api/k8s/upload-pipelines"],
    })


@app.route("/")
def index():
    return send_from_directory(os.path.join(ROOT, "static"), "index.html")


@app.route("/api/compile", methods=["POST"])
def api_compile():
    code, out, err = run_cmd([sys.executable, "iris_pipeline.py"], timeout=60)
    return jsonify({"ok": code == 0, "stdout": out, "stderr": err, "exit_code": code})


@app.route("/api/compile-hello", methods=["POST"])
def api_compile_hello():
    code, out, err = run_cmd([sys.executable, "hello_world_pipeline.py"], timeout=60)
    return jsonify({"ok": code == 0, "stdout": out, "stderr": err, "exit_code": code})


@app.route("/api/compile-animal", methods=["POST"])
def api_compile_animal():
    code, out, err = run_cmd([sys.executable, "animal_species_pipeline.py"], timeout=60)
    return jsonify({"ok": code == 0, "stdout": out, "stderr": err, "exit_code": code})


@app.route("/api/compile-nationality", methods=["POST"])
def api_compile_nationality():
    code, out, err = run_cmd([sys.executable, "nationality_type_pipeline.py"], timeout=60)
    return jsonify({"ok": code == 0, "stdout": out, "stderr": err, "exit_code": code})


@app.route("/api/compile-viruses", methods=["POST"])
def api_compile_viruses():
    code, out, err = run_cmd([sys.executable, "viruses_pipeline.py"], timeout=60)
    return jsonify({"ok": code == 0, "stdout": out, "stderr": err, "exit_code": code})


@app.route("/api/compile-sentiment", methods=["POST"])
def api_compile_sentiment():
    code, out, err = run_cmd([sys.executable, "sentiment_check_pipeline.py"], timeout=60)
    return jsonify({"ok": code == 0, "stdout": out, "stderr": err, "exit_code": code})


@app.route("/api/compile-summary", methods=["POST"])
def api_compile_summary():
    code, out, err = run_cmd([sys.executable, "data_summary_pipeline.py"], timeout=60)
    return jsonify({"ok": code == 0, "stdout": out, "stderr": err, "exit_code": code})


@app.route("/api/run-test", methods=["POST"])
def api_run_test():
    code, out, err = run_cmd(
        [sys.executable, "test_pipeline_inprocess.py"], timeout=60
    )
    return jsonify({"ok": code == 0, "stdout": out, "stderr": err, "exit_code": code})


@app.route("/api/run-local", methods=["POST"])
def api_run_local():
    code, out, err = run_cmd([sys.executable, "run_local.py"], timeout=300)
    return jsonify({"ok": code == 0, "stdout": out, "stderr": err, "exit_code": code})


# ---- KFP on Kubernetes (KIND + official dashboard) ----

@app.route("/api/k8s/status", methods=["GET"])
def api_k8s_status():
    """Check Docker, kind, kubectl, cluster, kubeflow namespace and pods."""
    status = {
        "docker": False,
        "kind": False,
        "kubectl": False,
        "cluster": None,
        "kubeflow_ns": False,
        "kfp_pods": [],
        "kfp_ui_service": False,
        "dashboard_url": f"http://localhost:{KFP_DASHBOARD_PORT}",
    }
    # Docker
    code, _, _ = run_cmd(["docker", "info"], timeout=5)
    status["docker"] = code == 0
    # kind
    code, out, _ = run_cmd(["kind", "get", "clusters"], timeout=5)
    status["kind"] = code == 0
    if code == 0 and out.strip():
        clusters = [c.strip() for c in out.strip().split("\n") if c.strip()]
        status["cluster"] = clusters[0] if clusters else None
    # kubectl
    code, _, _ = run_cmd(["kubectl", "version", "--client"], timeout=5)
    status["kubectl"] = code == 0
    if not status["kubectl"]:
        return jsonify(status)
    # kubeflow namespace and pods
    code, out, _ = run_cmd(["kubectl", "get", "namespace", "kubeflow"], timeout=10)
    status["kubeflow_ns"] = code == 0
    if status["kubeflow_ns"]:
        code, out, _ = run_cmd(
            ["kubectl", "get", "pods", "-n", "kubeflow", "-o", "name"],
            timeout=10,
        )
        if code == 0 and out.strip():
            status["kfp_pods"] = [p.strip().replace("pod/", "") for p in out.strip().split("\n")[:15]]
        code, _, _ = run_cmd(
            ["kubectl", "get", "svc", "ml-pipeline-ui", "-n", "kubeflow"],
            timeout=10,
        )
        status["kfp_ui_service"] = code == 0
    return jsonify(status)


@app.route("/api/k8s/setup", methods=["POST"])
def api_k8s_setup():
    """Create KIND cluster and install KFP (long-running)."""
    script = os.path.join(ROOT, "scripts", "setup_kind_kfp.sh")
    if not os.path.isfile(script):
        return jsonify({
            "ok": False,
            "stdout": "",
            "stderr": f"Setup script not found: {script}",
            "exit_code": -1,
        })
    # Run with bash; script uses network to pull images
    code, out, err = run_cmd(
        ["bash", script],
        cwd=ROOT,
        timeout=600,
    )
    return jsonify({
        "ok": code == 0,
        "stdout": out,
        "stderr": err,
        "exit_code": code,
    })


@app.route("/api/k8s/port-forward", methods=["POST"])
def api_k8s_port_forward():
    """Start kubectl port-forward for KFP UI in background (only if KFP is installed)."""
    global _port_forward_proc
    if _port_forward_proc is not None and _port_forward_proc.poll() is None:
        return jsonify({
            "ok": True,
            "url": f"http://localhost:{KFP_DASHBOARD_PORT}",
            "message": "Port-forward already running.",
        })
    # Require KFP to be installed (kubeflow ns and ml-pipeline-ui svc exist)
    code, _, _ = run_cmd(["kubectl", "get", "svc", "ml-pipeline-ui", "-n", "kubeflow"], timeout=10)
    if code != 0:
        return jsonify({
            "ok": False,
            "url": "",
            "message": "KFP is not installed. Install kind (https://kind.sigs.k8s.io/docs/user/quick-start/), then run 'Setup KIND + KFP' and wait for it to complete before starting the dashboard.",
        })
    cmd = [
        "kubectl", "port-forward",
        "-n", "kubeflow",
        "svc/ml-pipeline-ui",
        f"{KFP_DASHBOARD_PORT}:80",
    ]
    _port_forward_proc = run_cmd_background(cmd)
    if _port_forward_proc is None:
        return jsonify({
            "ok": False,
            "url": "",
            "message": "Failed to start port-forward.",
        })
    return jsonify({
        "ok": True,
        "url": f"http://localhost:{KFP_DASHBOARD_PORT}",
        "message": "KFP dashboard port-forward started. Open the URL in your browser.",
    })


@app.route("/api/k8s/upload-pipelines", methods=["POST"])
def api_k8s_upload_pipelines():
    """Compile all pipelines and upload them to the KFP API (avoids browser 'Failed to fetch')."""
    kfp_host = os.environ.get("KFP_API_URL", f"http://localhost:{KFP_DASHBOARD_PORT}")
    results = []
    compiled = []

    # Step 1: compile all pipelines
    for script, yaml_name, _ in PIPELINES_TO_UPLOAD:
        path = os.path.join(ROOT, script)
        if not os.path.isfile(path):
            results.append({"pipeline": yaml_name, "ok": False, "error": f"Script not found: {script}"})
            continue
        code, out, err = run_cmd([sys.executable, script], timeout=60)
        if code != 0:
            results.append({"pipeline": yaml_name, "ok": False, "error": f"Compile failed: {err or out}"})
            continue
        yaml_path = os.path.join(ROOT, yaml_name)
        if not os.path.isfile(yaml_path):
            results.append({"pipeline": yaml_name, "ok": False, "error": f"YAML not produced: {yaml_name}"})
            continue
        compiled.append((yaml_path, yaml_name, _))

    # Step 2: upload via KFP client (server-side avoids browser CORS/fetch issues)
    try:
        import kfp
        client = kfp.Client(host=kfp_host)
    except Exception as e:
        return jsonify({
            "ok": False,
            "results": results,
            "message": f"Cannot create KFP client: {e}. Start 'Start KFP Dashboard' so the API is at {kfp_host}.",
        })

    for yaml_path, yaml_name, description in compiled:
        try:
            client.upload_pipeline(
                pipeline_package_path=yaml_path,
                pipeline_name=None,
                description=description,
            )
            results.append({"pipeline": yaml_name, "ok": True})
        except Exception as e:
            results.append({"pipeline": yaml_name, "ok": False, "error": str(e)})

    all_ok = all(r.get("ok") for r in results)
    return jsonify({
        "ok": all_ok,
        "results": results,
        "message": "All pipelines uploaded." if all_ok else "Some pipelines failed to upload. Start KFP Dashboard (port-forward) and try again.",
    })


if __name__ == "__main__":
    import socket
    port = 5050
    for p in [5050, 5051, 5052]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", p))
            port = p
            break
        except OSError:
            continue
    print("Starting KFP UI at http://127.0.0.1:{} (all API routes loaded)".format(port))
    app.run(host="0.0.0.0", port=port, debug=False)
