#!/usr/bin/env bash
# Setup KIND cluster and install Kubeflow Pipelines (KFP).
# Requires: Docker, kind, kubectl. Run from project root or scripts/.
set -e

CLUSTER_NAME="${KFP_KIND_CLUSTER:-kfp-demo}"
PIPELINE_VERSION="${PIPELINE_VERSION:-2.14.3}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Checking prerequisites ==="
if ! command -v docker &>/dev/null; then
  echo "ERROR: docker not found. Install Docker Desktop first."
  exit 1
fi
if ! docker info &>/dev/null; then
  echo "ERROR: Docker is not running. Start Docker Desktop."
  exit 1
fi
if ! command -v kind &>/dev/null; then
  echo "ERROR: kind not found. Install from https://kind.sigs.k8s.io/docs/user/quick-start/"
  exit 1
fi
if ! command -v kubectl &>/dev/null; then
  echo "ERROR: kubectl not found. Install kubectl."
  exit 1
fi
echo "Docker, kind, kubectl: OK"

echo ""
echo "=== Creating KIND cluster: $CLUSTER_NAME ==="
if kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
  echo "Cluster $CLUSTER_NAME already exists."
else
  KIND_CONFIG="$SCRIPT_DIR/kind-config.yaml"
  if [[ -f "$KIND_CONFIG" ]]; then
    echo "Using fixed API port (36443) to avoid port conflicts."
    kind create cluster --name "$CLUSTER_NAME" --config "$KIND_CONFIG"
  else
    kind create cluster --name "$CLUSTER_NAME"
  fi
fi

echo ""
echo "=== Setting kubectl context to $CLUSTER_NAME ==="
export KUBECONFIG=""
kubectl config use-context "kind-$CLUSTER_NAME" 2>/dev/null || true

echo ""
echo "=== Installing Kubeflow Pipelines (version $PIPELINE_VERSION) ==="
echo "Applying cluster-scoped resources..."
kubectl apply -k "https://github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
echo "Waiting for CRD..."
kubectl wait --for=condition=established --timeout=120s crd/applications.app.k8s.io 2>/dev/null || true

echo "Applying KFP (platform-agnostic for better compatibility)..."
kubectl apply -k "https://github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=$PIPELINE_VERSION" || {
  echo "platform-agnostic failed, trying env/dev..."
  kubectl apply -k "https://github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$PIPELINE_VERSION"
}

echo "Waiting for kubeflow namespace..."
for i in $(seq 1 30); do
  if kubectl get namespace kubeflow &>/dev/null; then break; fi
  sleep 2
done
sleep 15
echo "Applying MinIO fix (official image + root env; avoids ImagePullBackOff and API connection refused)..."
kubectl set image deployment/minio -n kubeflow minio=minio/minio:latest 2>/dev/null || true
kubectl patch deployment minio -n kubeflow --type=json -p='[{"op":"add","path":"/spec/template/spec/containers/0/env/-","value":{"name":"MINIO_ROOT_USER","valueFrom":{"secretKeyRef":{"name":"mlpipeline-minio-artifact","key":"accesskey"}}}},{"op":"add","path":"/spec/template/spec/containers/0/env/-","value":{"name":"MINIO_ROOT_PASSWORD","valueFrom":{"secretKeyRef":{"name":"mlpipeline-minio-artifact","key":"secretkey"}}}}]' 2>/dev/null || true
echo "Disabling GKE metadata in UI (required for non-GKE clusters)..."
kubectl set env deployment/ml-pipeline-ui -n kubeflow DISABLE_GKE_METADATA=true 2>/dev/null || true
echo "Setting Argo workflow controller POD_NAMES=v1 (fixes pod log retrieval in UI)..."
kubectl set env deployment/workflow-controller -n kubeflow POD_NAMES=v1 2>/dev/null || true

echo ""
echo "=== KFP installation submitted. Pods may take 3–5 minutes to become Ready. ==="
echo "Check status: kubectl get pods -n kubeflow"
echo "When ready, click 'Start KFP Dashboard' in the UI, then 'Open KFP Dashboard'."
echo "Done."
