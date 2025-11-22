#!/bin/bash
# =============================================================================
# Setup Minikube Cluster for AI Chat Application
# =============================================================================
# This script creates a Minikube cluster and enables required addons.
#
# Usage: ./scripts/setup-cluster.sh
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Configuration - can be overridden with environment variables
CLUSTER_NAME="${CLUSTER_NAME:-ai-chat-cluster}"
MINIKUBE_MEMORY="${MINIKUBE_MEMORY:-4096}"
MINIKUBE_CPUS="${MINIKUBE_CPUS:-2}"

# -----------------------------------------------------------------------------
# Pre-flight checks
# -----------------------------------------------------------------------------

log "Running pre-flight checks..."

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    error "minikube is not installed. Please install it first:
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube"
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    error "kubectl is not installed. Please install it first:
    curl -LO https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
    sudo install kubectl /usr/local/bin/kubectl"
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    error "Docker is not running. Please start Docker first."
fi

# -----------------------------------------------------------------------------
# Create or start Minikube cluster
# -----------------------------------------------------------------------------

log "Setting up Minikube cluster: $CLUSTER_NAME"

# Check if cluster already exists
if minikube status -p "$CLUSTER_NAME" &> /dev/null; then
    log "Cluster '$CLUSTER_NAME' already exists. Starting it..."
    minikube start -p "$CLUSTER_NAME"
else
    log "Creating new Minikube cluster..."
    minikube start \
        --profile="$CLUSTER_NAME" \
        --memory="$MINIKUBE_MEMORY" \
        --cpus="$MINIKUBE_CPUS" \
        --driver=docker
fi

# -----------------------------------------------------------------------------
# Enable required addons
# -----------------------------------------------------------------------------

log "Enabling ingress addon..."
minikube addons enable ingress -p "$CLUSTER_NAME"

log "Waiting for ingress controller to be ready..."
sleep 10

# -----------------------------------------------------------------------------
# Configure kubectl context
# -----------------------------------------------------------------------------

log "Setting kubectl context to '$CLUSTER_NAME'..."
kubectl config use-context "$CLUSTER_NAME"

# -----------------------------------------------------------------------------
# Get cluster info
# -----------------------------------------------------------------------------

MINIKUBE_IP=$(minikube ip -p "$CLUSTER_NAME")

log "============================================"
log "Cluster setup complete!"
log ""
log "Minikube IP: $MINIKUBE_IP"
log ""
log "IMPORTANT: Add this line to your /etc/hosts file:"
echo -e "${YELLOW}$MINIKUBE_IP    ai-chat${NC}"
log ""
log "Run this command:"
echo -e "${YELLOW}echo '$MINIKUBE_IP    ai-chat' | sudo tee -a /etc/hosts${NC}"
log ""
log "Then run: ./scripts/deploy.sh"
log "============================================"