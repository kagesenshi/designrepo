# Kubernetes Deployment with Kustomize and ArgoCD

This directory contains Kustomize configuration for deploying the designrepo application to Kubernetes.

## Structure

```
k8s/
├── base/                          # Base Kubernetes manifests
│   ├── kustomization.yaml         # Base Kustomize config
│   ├── backend-deployment.yaml    # Backend deployment
│   ├── frontend-deployment.yaml   # Frontend deployment
│   ├── postgres-cluster.yaml      # CloudNativePG cluster
│   ├── backend-service.yaml       # Backend service
│   ├── frontend-service.yaml      # Frontend service
│   ├── configmap.yaml             # Application configuration
│   ├── secret.yaml                # Sensitive credentials
│   └── ingress.yaml               # Ingress with TLS
├── overlays/
│   └── production/                # Production overlay
│       ├── kustomization.yaml     # Production config
│       └── replica-patch.yaml     # Replica count patch
└── argocd-application.yaml        # ArgoCD Application manifest
```

## Quick Start

### Prerequisites

- Kubernetes cluster with:
  - CloudNativePG operator installed
  - Ingress controller (e.g., nginx-ingress)
  - cert-manager for TLS certificates
  - ArgoCD installed

### Deploy with ArgoCD

```bash
# Apply the ArgoCD Application
kubectl apply -f k8s/argocd-application.yaml

# Watch sync status
argocd app get designrepo
```

### Manual Deployment (without ArgoCD)

```bash
# Build and apply production configuration
kustomize build k8s/overlays/production | kubectl apply -f -

# Or using kubectl
kubectl apply -k k8s/overlays/production
```

## Configuration

### Update Before Deployment

1. **Ingress domain**: Edit `k8s/base/ingress.yaml` and replace `designrepo.example.com`
2. **S3 backup credentials**: Create secret for PostgreSQL backups
3. **Secrets**: Consider using Sealed Secrets or External Secrets Operator

### Image Tags

To deploy specific versions, edit `k8s/overlays/production/kustomization.yaml`:

```yaml
images:
- name: ghcr.io/kagesenshi/designrepo/backend
  newTag: v1.0.0
- name: ghcr.io/kagesenshi/designrepo/frontend
  newTag: v1.0.0
```

## Components

- **Backend**: Reflex application (3 replicas in production)
- **Frontend**: Nginx serving static files (3 replicas in production)
- **Database**: PostgreSQL via CloudNativePG (3 instances for HA)

## Documentation

See the [walkthrough document](../.gemini/antigravity/brain/ee1c209a-eb43-4671-bda4-73c6f698add0/walkthrough.md) for detailed deployment instructions.
