# 🚀 Enterprise Deployment Guide

Complete guide to deploying DevSecOps Agent at enterprise scale across AWS, Azure, GCP, and on-premise environments.

---

## 📋 Pre-Deployment Checklist

### Infrastructure Requirements

```
✅ Kubernetes Cluster (1.24+)
   - Minimum 3 nodes (HA)
   - 4GB RAM per node
   - 20GB storage per node
   - Network policies enabled

✅ PostgreSQL Database (13+)
   - High availability setup
   - Automated backups (daily)
   - Multi-region replication (optional)
   - PITR (Point-in-Time Recovery)

✅ Message Queue (Optional, for scale)
   - RabbitMQ or AWS SQS
   - Topic-based routing
   - Dead letter queue handling

✅ Secret Management
   - HashiCorp Vault OR
   - AWS Secrets Manager OR
   - Azure Key Vault

✅ Observability Stack
   - Prometheus (metrics)
   - Grafana (dashboards)
   - Loki/ELK (logs)
   - Jaeger (tracing)

✅ Networking
   - VPC/VNet configured
   - Security groups/NSGs
   - TLS certificates (signed)
   - Load balancer (L7)
```

### Security Requirements

```
✅ Network Security
   - Ingress: TLS 1.3+, port 443 only
   - Egress: Whitelist trusted hosts
   - Blocked: Port 22 (SSH), 3306 (MySQL), 5432 (direct DB)
   - Encryption: All data in transit & at rest

✅ IAM & RBAC
   - Service accounts with minimal permissions
   - Pod security policies enforced
   - Role-based access control configured
   - Audit logging enabled

✅ Data Protection
   - Encryption key rotation schedules
   - Secrets not stored in code/configs
   - PII data classification
   - Backup encryption verified

✅ Compliance
   - Audit trail immutability
   - Change management procedures
   - Incident response plan
   - Disaster recovery plan
```

---

## 🏗️ AWS Deployment

### Option 1: EKS (Recommended for Enterprise)

```bash
# 1. Create EKS cluster
aws eks create-cluster \
  --name devsecops-prod \
  --version 1.27 \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/eks-service-role \
  --resources-vpc-config subnetIds=subnet-xxx,subnet-yyy

# 2. Create node group
aws eks create-nodegroup \
  --cluster-name devsecops-prod \
  --nodegroup-name prod-nodes \
  --subnets subnet-xxx subnet-yyy \
  --capacity-type on-demand \
  --scaling-config minSize=3,maxSize=100,desiredSize=5 \
  --instance-types t3.large

# 3. Create RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier devsecops-db \
  --engine postgres \
  --engine-version 15.1 \
  --db-instance-class db.r6i.2xlarge \
  --allocated-storage 100 \
  --storage-type gp3 \
  --multi-az \
  --backup-retention-period 30

# 4. Create Secrets Manager entries
aws secretsmanager create-secret \
  --name devsecops/prod/db-password \
  --secret-string '{"username":"admin","password":"SECURE_PASSWORD"}'

# 5. Get kubeconfig
aws eks update-kubeconfig \
  --name devsecops-prod \
  --region us-east-1

# 6. Install NVIDIA Operator (if using GPU for LLM)
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm install nvidia-device-plugin nvidia/nvidia-device-plugin \
  --namespace kube-system
```

### Helm Installation (AWS)

```bash
# 1. Add Helm repository
helm repo add devsecops https://charts.devsecops-agent.io
helm repo update

# 2. Create namespace
kubectl create namespace devsecops
kubectl label namespace devsecops name=devsecops

# 3. Create secrets
kubectl create secret generic devsecops-secrets \
  --from-literal=db-password=SECURE_PASSWORD \
  --from-literal=api-key=SECURE_API_KEY \
  -n devsecops

# 4. Deploy with values
helm install devsecops devsecops/agent \
  --namespace devsecops \
  --values - <<EOF
environment: production
replicas: 3

database:
  host: devsecops-db.c5r3fqwnjz.us-east-1.rds.amazonaws.com
  port: 5432
  name: devsecops_prod
  ssl: true

secrets:
  provider: aws-secrets-manager
  region: us-east-1

observability:
  prometheus:
    enabled: true
    retention: 90d
  grafana:
    enabled: true
    adminPassword: SECURE_PASSWORD

aws:
  cloudwatch:
    enabled: true
    namespace: DevsecopsAgent
  costanomaly:
    enabled: true
    alertTopicArn: arn:aws:sns:us-east-1:ACCOUNT_ID:devsecops-alerts

ingress:
  enabled: true
  className: alb
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS-1-2-2017-01
  hosts:
    - host: devsecops.mycompany.com
      paths:
        - path: /
          pathType: Prefix

podSecurityPolicy:
  enabled: true
  restrictedPolicy: true

networkPolicy:
  enabled: true
  policyTypes:
    - Ingress
    - Egress
EOF
```

### CloudFormation (Alternative)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'DevSecOps Agent CloudFormation Stack'

Parameters:
  ClusterName:
    Type: String
    Default: devsecops-prod
  DBPassword:
    Type: String
    NoEcho: true
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]

Resources:
  # EKS Cluster
  DevsecopsCluster:
    Type: AWS::EKS::Cluster
    Properties:
      Name: !Ref ClusterName
      Version: '1.27'
      RoleArn: !GetAtt EKSRole.Arn
      ResourcesVpcConfig:
        SubnetIds:
          - !Ref PrivateSubnet1
          - !Ref PrivateSubnet2
          - !Ref PrivateSubnet3

  # RDS Database
  DevsecopsDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub '${ClusterName}-db'
      Engine: postgres
      EngineVersion: '15.1'
      DBInstanceClass: db.r6i.2xlarge
      AllocatedStorage: 100
      StorageType: gp3
      StorageEncrypted: true
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      DBName: devsecops_prod
      MultiAZ: true
      BackupRetentionPeriod: 30
      EnableCloudwatchLogsExports:
        - postgresql
      EnableIAMDatabaseAuthentication: true
      DeletionProtection: true

  # Secrets Manager
  DBSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub 'devsecops/${Environment}/db-credentials'
      SecretString: !Sub |
        {
          "username": "admin",
          "password": "${DBPassword}",
          "host": "${DevsecopsDatabase.Endpoint.Address}",
          "port": 5432,
          "dbname": "devsecops_prod"
        }

  # IAM Role for EKS
  EKSRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: eks.amazonaws.com
            Action: 'sts:AssumeRole'
      ManagedPolicyArns:
        - 'arn:aws:iam::aws:policy/AmazonEKSClusterPolicy'

Outputs:
  ClusterName:
    Value: !Ref DevsecopsCluster
  DBEndpoint:
    Value: !GetAtt DevsecopsDatabase.Endpoint.Address
  SecretsArn:
    Value: !GetAtt DBSecret.Arn
```

---

## ☁️ Azure Deployment

### AKS Setup

```bash
# 1. Create resource group
az group create \
  --name devsecops-prod \
  --location eastus

# 2. Create AKS cluster
az aks create \
  --resource-group devsecops-prod \
  --name devsecops-aks \
  --vm-set-type VirtualMachineScaleSets \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-managed-identity \
  --network-plugin azure \
  --enable-pod-identity \
  --enable-azure-keyvault-secrets-provider

# 3. Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group devsecops-prod \
  --name devsecops-db \
  --location eastus \
  --admin-user admin \
  --admin-password SECURE_PASSWORD \
  --sku-name Standard_B2s \
  --tier Burstable \
  --storage-size 65536 \
  --backup-retention 30

# 4. Create Key Vault
az keyvault create \
  --resource-group devsecops-prod \
  --name devsecops-kv

# 5. Create secret in Key Vault
az keyvault secret set \
  --vault-name devsecops-kv \
  --name db-password \
  --value SECURE_PASSWORD

# 6. Get kubeconfig
az aks get-credentials \
  --resource-group devsecops-prod \
  --name devsecops-aks
```

### Helm Installation (Azure)

```bash
# 1. Install CSI Driver for Key Vault
helm repo add csi-secrets-store-provider-azure \
  https://raw.githubusercontent.com/Azure/secrets-store-csi-driver-provider-azure/master/charts
helm install csi-secrets-store-provider-azure/csi-secrets-store-provider-azure \
  --namespace kube-system

# 2. Deploy DevSecOps Agent
helm install devsecops devsecops/agent \
  --namespace devsecops \
  --values - <<EOF
environment: production
replicas: 3

database:
  host: devsecops-db.postgres.database.azure.com
  port: 5432
  name: devsecops_prod
  ssl: true

secrets:
  provider: azure-keyvault
  keyVaultName: devsecops-kv

azure:
  monitor:
    enabled: true
    workspaceId: /subscriptions/SUB-ID/resourcegroups/RESOURCE-GROUP/providers/microsoft.operationalinsights/workspaces/WORKSPACE-NAME

ingress:
  enabled: true
  className: azure-application-gateway
  annotations:
    appgw.ingress.kubernetes.io/override-hostname: devsecops.mycompany.com
  tls:
    - secretName: tls-cert
      hosts:
        - devsecops.mycompany.com
EOF
```

---

## 🌍 GCP Deployment

### GKE Setup

```bash
# 1. Create GKE cluster
gcloud container clusters create devsecops-prod \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 100 \
  --enable-ip-alias \
  --enable-stackdriver-kubernetes

# 2. Create Cloud SQL instance
gcloud sql instances create devsecops-db \
  --database-version POSTGRES_15 \
  --tier db-custom-2-8192 \
  --region us-central1 \
  --backup-start-time 02:00 \
  --retained-backups-count 30

# 3. Create database
gcloud sql databases create devsecops_prod \
  --instance devsecops-db

# 4. Create Secret Manager secrets
echo -n "SECURE_PASSWORD" | \
  gcloud secrets create devsecops-db-password --data-file=-

# 5. Get kubeconfig
gcloud container clusters get-credentials devsecops-prod
```

### Helm Installation (GCP)

```bash
helm install devsecops devsecops/agent \
  --namespace devsecops \
  --values - <<EOF
environment: production
replicas: 3

database:
  host: /cloudsql/PROJECT_ID:us-central1:devsecops-db
  port: 5432
  name: devsecops_prod
  cloudSqlProxy: true

secrets:
  provider: gcp-secret-manager

gcp:
  monitoring:
    enabled: true
    projectId: PROJECT_ID
  costAnomalyDetection:
    enabled: true
    billingAccountId: BILLING_ACCOUNT_ID

ingress:
  enabled: true
  className: gce
  annotations:
    kubernetes.io/ingress.class: gce
    kubernetes.io/ingress.global-static-ip-name: devsecops-ip
EOF
```

---

## 🔒 Security Hardening Checklist

### Network Security

```yaml
# Network Policy: Restrict ingress/egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: devsecops-netpol
  namespace: devsecops
spec:
  podSelector:
    matchLabels:
      app: devsecops-agent
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              role: monitoring
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

### Pod Security Policy

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: devsecops-restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'MustRunAs'
    seLinuxOptions:
      level: "s0:c123,c456"
  fsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1000
        max: 65535
  readOnlyRootFilesystem: true
```

---

## 📊 Monitoring & Alerting

### Prometheus Rules

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: devsecops-alerts
spec:
  groups:
    - name: devsecops.rules
      interval: 30s
      rules:
        - alert: HighErrorRate
          expr: |
            (sum(rate(devsecops_requests_total{status=~"5.."}[5m])) by (job))
            /
            (sum(rate(devsecops_requests_total[5m])) by (job))
            > 0.05
          for: 5m
          annotations:
            summary: "High error rate detected"
            
        - alert: DatabaseConnectionPoolExhausted
          expr: devsecops_db_connections_available < 5
          for: 1m
          annotations:
            summary: "Database connection pool nearly exhausted"
```

---

## 🚨 Disaster Recovery

### Backup Strategy

```bash
# Automated daily backups
0 2 * * * /usr/local/bin/backup-devsecops.sh

# Backup script
#!/bin/bash
BACKUP_DIR="/mnt/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
pg_dump -h $DB_HOST -U $DB_USER devsecops_prod | \
  gzip > "$BACKUP_DIR/devsecops_$TIMESTAMP.sql.gz"

# Upload to S3
aws s3 cp "$BACKUP_DIR/devsecops_$TIMESTAMP.sql.gz" \
  s3://my-backup-bucket/devsecops/

# Keep only last 30 days
find "$BACKUP_DIR" -name "devsecops_*.sql.gz" -mtime +30 -delete
```

### Restore Procedure

```bash
# 1. Restore database from backup
gunzip < /mnt/backups/devsecops_20260410_020000.sql.gz | \
  psql -h $DB_HOST -U $DB_USER devsecops_prod

# 2. Restart services
kubectl rollout restart deployment/devsecops-agent -n devsecops

# 3. Verify health
kubectl get pods -n devsecops
curl https://devsecops.mycompany.com/health/status
```

---

## 📞 Enterprise Support

**For production deployments:**
- 📧 Email: [qasimshafiq20@gmail.com](mailto:qasimshafiq20@gmail.com)
- 📅 Schedule consultation
- 📞 24/7 support available for enterprise tiers

---

*Last Updated: April 2026*
*For latest deployment guides: https://github.com/qasim8818/devsecops-agent/docs*
