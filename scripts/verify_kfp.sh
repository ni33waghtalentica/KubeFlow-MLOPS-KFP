#!/usr/bin/env bash
# Verify KFP on KIND and wait for UI to be ready. Run from project root.
set -e

CLUSTER_NAME="${KFP_KIND_CLUSTER:-kfp-demo}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Using context kind-$CLUSTER_NAME ==="
kubectl config use-context "kind-$CLUSTER_NAME" || true

echo ""
echo "=== Applying MinIO fix (if needed: official image + root env) ==="
kubectl set image deployment/minio -n kubeflow minio=minio/minio:latest 2>/dev/null || true
kubectl patch deployment minio -n kubeflow --type=json -p='[{"op":"add","path":"/spec/template/spec/containers/0/env/-","value":{"name":"MINIO_ROOT_USER","valueFrom":{"secretKeyRef":{"name":"mlpipeline-minio-artifact","key":"accesskey"}}}},{"op":"add","path":"/spec/template/spec/containers/0/env/-","value":{"name":"MINIO_ROOT_PASSWORD","valueFrom":{"secretKeyRef":{"name":"mlpipeline-minio-artifact","key":"secretkey"}}}}]' 2>/dev/null || true
kubectl set env deployment/ml-pipeline-ui -n kubeflow DISABLE_GKE_METADATA=true 2>/dev/null || true
echo "Setting Argo workflow controller POD_NAMES=v1 (fixes 'podname argument is required' / Failed to retrieve pod logs)..."
kubectl set env deployment/workflow-controller -n kubeflow POD_NAMES=v1 2>/dev/null || true

echo ""
echo "=== Waiting for ml-pipeline-ui to be Running (up to 5 minutes) ==="
if kubectl wait --for=condition=ready pod -l app=ml-pipeline-ui -n kubeflow --timeout=300s 2>/dev/null; then
  echo "ml-pipeline-ui is Ready."
else
  echo "Still waiting or not ready. Current pods:"
  kubectl get pods -n kubeflow -l app=ml-pipeline-ui
  echo ""
  echo "Run: kubectl get pods -n kubeflow"
  echo "When ml-pipeline-ui is 1/1 Running, run: kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80"
  exit 1
fi

echo ""
echo "=== KFP UI is ready. Start port-forward with: ==="
echo "  kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80"
echo "Then open: http://localhost:8080"
echo ""
echo "Or click 'Start KFP Dashboard' in the web UI (http://127.0.0.1:5050)."
