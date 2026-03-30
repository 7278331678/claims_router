#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
STATE_BUCKET="${2:-}"
REGION="${3:-us-east-1}"
LOCK_TABLE="${4:-router-api-tf-locks}"

if [[ -z "${STATE_BUCKET}" ]]; then
  echo "Usage: ./scripts/deploy.sh <dev|int|prod> <state-bucket> [region] [lock-table]"
  exit 1
fi

ENV_DIR="infra/envs/${ENVIRONMENT}"
STATE_KEY="router-api/${ENVIRONMENT}/terraform.tfstate"

terraform -chdir="${ENV_DIR}" init \
  -backend-config="bucket=${STATE_BUCKET}" \
  -backend-config="region=${REGION}" \
  -backend-config="dynamodb_table=${LOCK_TABLE}" \
  -backend-config="key=${STATE_KEY}"

terraform -chdir="${ENV_DIR}" validate
terraform -chdir="${ENV_DIR}" plan -var-file=terraform.tfvars -out=tfplan
terraform -chdir="${ENV_DIR}" apply -auto-approve tfplan
