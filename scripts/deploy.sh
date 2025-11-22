#!/bin/bash
# =============================================================================
# Deploy AI Chat Application to Kubernetes
# =============================================================================
# This script deploys all components in the correct order.
#
# Usage: ./scripts/deploy.sh
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Get script directory (to find k8s/ folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$SCRIPT_DIR/../k8s"

# -----------------------------------------------------------------------------
# Pre-flight checks
# -----------------------------------------------------------------------------

log "Running pre-flight checks..."

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    error "kubectl is not configured. Run ./scripts/setup-cluster.sh first."
fi

# Check if k8s directory exists
if [ ! -d "$K8S_DIR" ]; then
    error "k8s directory not found at $K8S_DIR"
fi

# -----------------------------------------------------------------------------
# Deploy resources
# -----------------------------------------------------------------------------

log "Starting deployment..."

# 1. Create namespace
log "Creating namespace..."
kubectl apply -f "$K8S_DIR/namespace.yaml"

# 2. Deploy Ollama
log "Deploying Ollama..."
kubectl apply -f "$K8S_DIR/ollama-deployment.yaml"
kubectl apply -f "$K8S_DIR/ollama-service.yaml"

# 3. Wait for Ollama to be ready
log "Waiting for Ollama to be ready (this may take a minute)..."
kubectl wait --for=condition=available --timeout=180s deployment/ollama -n ai-chat || {
    warn "Ollama deployment timed out. Checking status..."
    kubectl get pods -n ai-chat
    kubectl describe deployment ollama -n ai-chat
}

# 4. Pull the LLM model
log "Starting model pull job (this may take several minutes)..."
kubectl apply -f "$K8S_DIR/ollama-init-job.yaml"

log "Waiting for model to download..."
kubectl wait --for=condition=complete --timeout=600s job/ollama-model-pull -n ai-chat || {
    warn "Model pull job timed out. Checking status..."
    kubectl logs job/ollama-model-pull -n ai-chat
}

# 5. Deploy webapp
log "Deploying webapp..."
kubectl apply -f "$K8S_DIR/webapp-deployment.yaml"
kubectl apply -f "$K8S_DIR/webapp-service.yaml"

# 6. Configure ingress
log "Configuring ingress..."
kubectl apply -f "$K8S_DIR/ingress.yaml"

# 7. Wait for webapp to be ready
log "Waiting for webapp to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/ai-chat-webapp -n ai-chat || {
    warn "Webapp deployment timed out. Checking status..."
    kubectl get pods -n ai-chat
}

# -----------------------------------------------------------------------------
# Show status
# -----------------------------------------------------------------------------

log "============================================"
log "Deployment complete!"
log ""
log "Resources:"
kubectl get all -n ai-chat
log ""
log "Ingress:"
kubectl get ingress -n ai-chat
log ""
log "============================================"
log "Access the application at: http://ai-chat"
log ""
log "Useful commands:"
log "  kubectl get pods -n ai-chat"
log "  kubectl logs -f deployment/ai-chat-webapp -n ai-chat"
log "  kubectl logs -f deployment/ollama -n ai-chat"
log "============================================"