SHELL := /bin/bash

AWS_REGION ?= us-east-1
TF_STATE_BUCKET ?=
TF_LOCK_TABLE ?= router-api-tf-locks
ENV ?= dev

ENV_DIR = infra/envs/$(ENV)
STATE_KEY = router-api/$(ENV)/terraform.tfstate

.PHONY: init validate plan apply deploy

init:
	@test -n "$(TF_STATE_BUCKET)" || (echo "TF_STATE_BUCKET is required"; exit 1)
	terraform -chdir=$(ENV_DIR) init \
		-backend-config="bucket=$(TF_STATE_BUCKET)" \
		-backend-config="region=$(AWS_REGION)" \
		-backend-config="dynamodb_table=$(TF_LOCK_TABLE)" \
		-backend-config="key=$(STATE_KEY)"

validate:
	terraform -chdir=$(ENV_DIR) validate

plan:
	terraform -chdir=$(ENV_DIR) plan -var-file=terraform.tfvars -out=tfplan

apply:
	terraform -chdir=$(ENV_DIR) apply -auto-approve tfplan

deploy: init validate plan apply
