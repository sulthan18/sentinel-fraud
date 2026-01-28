# GitOps Workflow with ArgoCD

## Overview

This directory contains ArgoCD configuration for automated ML model deployment using GitOps principles.

## Workflow

### 1. Initial Setup

Install ArgoCD in Kubernetes cluster:
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Access ArgoCD UI:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Username: admin
# Password: kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
```

### 2. Deploy Application

Apply the ArgoCD application:
```bash
kubectl apply -f argocd/application.yaml
```

ArgoCD will automatically:
- Clone the GitHub repository
- Render Helm templates
- Deploy to Kubernetes
- Monitor for changes

### 3. Update Model Version

To deploy a new model version via GitOps:

1. **Build new Docker image** with updated model:
   ```bash
   docker build -f infra/Dockerfile.inference -t sentinel-inference:v1.1 .
   docker push sentinel-inference:v1.1
   ```

2. **Update values.yaml** in Git:
   ```yaml
   inference:
     image:
       tag: v1.1  # Update version
     model:
       version: "v1.1"
   ```

3. **Commit and push**:
   ```bash
   git add helm/sentinel-ml/values.yaml
   git commit -m "Update model to v1.1"
   git push origin develop
   ```

4. **ArgoCD auto-syncs** (within 3 minutes):
   - Detects Git change
   - Performs rolling update
   - Maintains zero downtime

### 4. Rollback

If new model version has issues:

**Option A: Git revert**
```bash
git revert HEAD
git push origin develop
# ArgoCD will auto-deploy previous version
```

**Option B: ArgoCD UI**
- Navigate to application history
- Click "Rollback" on previous revision

### 5. Manual Sync

Force immediate sync:
```bash
argocd app sync sentinel-ml
```

## Benefits

✅ **Reproducibility**: Every deployment is tracked in Git  
✅ **Traceability**: Full audit log of model versions  
✅ **Rollback**: Easy revert to previous working state  
✅ **Automation**: No manual kubectl commands needed  
✅ **Consistency**: Declarative, version-controlled infrastructure

## Monitoring Sync Status

Check application health:
```bash
argocd app get sentinel-ml
```

Watch sync progress:
```bash
argocd app wait sentinel-ml
```
