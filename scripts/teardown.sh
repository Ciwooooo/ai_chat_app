#!/bin/bash
# =============================================================================
# Teardown AI Chat Application
# =============================================================================
# This script removes all deployed resources and optionally the cluster.
#
# Usage: ./scripts/teardown.sh
# =============================================================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

CLUSTER_NAME="${CLUSTER_NAME:-ai-chat-cluster}"

# -----------------------------------------------------------------------------
# Delete namespace (removes all resources)
# -----------------------------------------------------------------------------

log "Deleting ai-chat namespace and all resources..."
kubectl delete namespace ai-chat --ignore-not-found

log "Namespace deleted."

# -----------------------------------------------------------------------------
# Optionally stop or delete cluster
# -----------------------------------------------------------------------------

log "============================================"
log "Teardown complete!"
log ""
log "The Minikube cluster is still running."
log ""
log "To stop the cluster:"
echo -e "${YELLOW}minikube stop -p $CLUSTER_NAME${NC}"
log ""
log "To delete the cluster completely:"
echo -e "${YELLOW}minikube delete -p $CLUSTER_NAME${NC}"
log ""
log "To remove the /etc/hosts entry:"
echo -e "${YELLOW}sudo sed -i '/ai-chat/d' /etc/hosts${NC}"
log "============================================"