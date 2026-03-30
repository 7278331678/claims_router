param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("dev", "int", "prod")]
  [string]$Environment,

  [Parameter(Mandatory = $true)]
  [string]$StateBucket,

  [string]$Region = "us-east-1",
  [string]$LockTable = "router-api-tf-locks"
)

$ErrorActionPreference = "Stop"

$envDir = "infra/envs/$Environment"
$stateKey = "router-api/$Environment/terraform.tfstate"

Write-Host "Initializing Terraform for environment: $Environment"
terraform -chdir=$envDir init `
  -backend-config="bucket=$StateBucket" `
  -backend-config="region=$Region" `
  -backend-config="dynamodb_table=$LockTable" `
  -backend-config="key=$stateKey"

Write-Host "Validating Terraform configuration"
terraform -chdir=$envDir validate

Write-Host "Planning infrastructure changes"
terraform -chdir=$envDir plan -var-file=terraform.tfvars -out=tfplan

Write-Host "Applying infrastructure changes"
terraform -chdir=$envDir apply -auto-approve tfplan

Write-Host "Deployment completed for $Environment"
