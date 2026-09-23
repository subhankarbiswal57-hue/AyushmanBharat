# Deployment & Cloud Infrastructure

## Local Development (Docker Compose)
```bash
docker-compose up --build
```
Services spin up on:
- API Gateway: `localhost:8000`
- Auth Service: `localhost:8001`
- Core Backend: `localhost:8002`
- Audit Service: `localhost:8003`
- AI/ML Engine: `localhost:8004`

## Production Deployment Blueprint
1. **Container Registry**: Push images to GCR / Docker Hub.
2. **Kubernetes (GKE / EKS)**: Helm charts under `infra/k8s/` with horizontal pod autoscaling.
3. **Database**: Managed PostgreSQL (Cloud SQL / RDS) with automated daily backups.
4. **Secrets**: Vault / GCP Secret Manager for JWT keys, DB credentials, and ABDM client secrets.
5. **CDN & WAF**: Cloudflare or AWS CloudFront for patient-facing PWA assets.

## Disaster Recovery
- **RPO**: 1 hour (WAL-based continuous archival).
- **RTO**: 30 minutes (warm standby with automated failover).
