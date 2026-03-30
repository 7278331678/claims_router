provider "aws" {
  region = var.aws_region
}

locals {
  env = var.environment
}

module "iam" {
  source       = "../../modules/iam"
  project_name = var.project_name
  environment  = local.env
  region       = var.aws_region
}

module "lambda_claim_public" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-claim-public-${local.env}"
  description   = "Public CLAIM handler for ${local.env}"
  source_dir    = "${path.root}/../../../lambda/targets/claim"
  handler       = "app.handler"
  role_arn      = module.iam.target_lambda_role_arn
  timeout       = 10
  environment_variables = {
    ENV           = local.env
    ENDPOINT_TYPE = "public"
    ACTION        = "claim"
    LOG_LEVEL     = var.log_level
  }
}

module "lambda_claim_private" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-claim-private-${local.env}"
  description   = "Private CLAIM handler for ${local.env}"
  source_dir    = "${path.root}/../../../lambda/targets/claim"
  handler       = "app.handler"
  role_arn      = module.iam.target_lambda_role_arn
  timeout       = 10
  environment_variables = {
    ENV           = local.env
    ENDPOINT_TYPE = "private"
    ACTION        = "claim"
    LOG_LEVEL     = var.log_level
  }
}

module "lambda_claim_summary_public" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-claim-summary-public-${local.env}"
  description   = "Public CLAIM SUMMARY handler for ${local.env}"
  source_dir    = "${path.root}/../../../lambda/targets/claim_summary"
  handler       = "app.handler"
  role_arn      = module.iam.target_lambda_role_arn
  timeout       = 10
  environment_variables = {
    ENV           = local.env
    ENDPOINT_TYPE = "public"
    ACTION        = "claim_summary"
    LOG_LEVEL     = var.log_level
  }
}

module "lambda_claim_summary_private" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-claim-summary-private-${local.env}"
  description   = "Private CLAIM SUMMARY handler for ${local.env}"
  source_dir    = "${path.root}/../../../lambda/targets/claim_summary"
  handler       = "app.handler"
  role_arn      = module.iam.target_lambda_role_arn
  timeout       = 10
  environment_variables = {
    ENV           = local.env
    ENDPOINT_TYPE = "private"
    ACTION        = "claim_summary"
    LOG_LEVEL     = var.log_level
  }
}

module "lambda_create_public" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-create-public-${local.env}"
  description   = "Public CREATE handler for ${local.env}"
  source_dir    = "${path.root}/../../../lambda/targets/create"
  handler       = "app.handler"
  role_arn      = module.iam.target_lambda_role_arn
  timeout       = 10
  environment_variables = {
    ENV           = local.env
    ENDPOINT_TYPE = "public"
    ACTION        = "create"
    LOG_LEVEL     = var.log_level
  }
}

module "lambda_create_private" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-create-private-${local.env}"
  description   = "Private CREATE handler for ${local.env}"
  source_dir    = "${path.root}/../../../lambda/targets/create"
  handler       = "app.handler"
  role_arn      = module.iam.target_lambda_role_arn
  timeout       = 10
  environment_variables = {
    ENV           = local.env
    ENDPOINT_TYPE = "private"
    ACTION        = "create"
    LOG_LEVEL     = var.log_level
  }
}

module "lambda_update_public" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-update-public-${local.env}"
  description   = "Public UPDATE handler for ${local.env}"
  source_dir    = "${path.root}/../../../lambda/targets/update"
  handler       = "app.handler"
  role_arn      = module.iam.target_lambda_role_arn
  timeout       = 10
  environment_variables = {
    ENV           = local.env
    ENDPOINT_TYPE = "public"
    ACTION        = "update"
    LOG_LEVEL     = var.log_level
  }
}

module "lambda_update_private" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-update-private-${local.env}"
  description   = "Private UPDATE handler for ${local.env}"
  source_dir    = "${path.root}/../../../lambda/targets/update"
  handler       = "app.handler"
  role_arn      = module.iam.target_lambda_role_arn
  timeout       = 10
  environment_variables = {
    ENV           = local.env
    ENDPOINT_TYPE = "private"
    ACTION        = "update"
    LOG_LEVEL     = var.log_level
  }
}

module "router_lambda" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-router-${local.env}"
  description   = "Router lambda using hybrid route resolution"
  source_dir    = "${path.root}/../../../lambda/router"
  handler       = "app.handler"
  role_arn      = module.iam.router_lambda_role_arn
  timeout       = 29
  memory_size   = 512

  environment_variables = {
    ENV                          = local.env
    LOG_LEVEL                    = var.log_level
    BEDROCK_MODEL_ID             = var.bedrock_model_id
    TARGET_CLAIM_PUBLIC          = module.lambda_claim_public.function_name
    TARGET_CLAIM_PRIVATE         = module.lambda_claim_private.function_name
    TARGET_CLAIM_SUMMARY_PUBLIC  = module.lambda_claim_summary_public.function_name
    TARGET_CLAIM_SUMMARY_PRIVATE = module.lambda_claim_summary_private.function_name
    TARGET_CREATE_PUBLIC         = module.lambda_create_public.function_name
    TARGET_CREATE_PRIVATE        = module.lambda_create_private.function_name
    TARGET_UPDATE_PUBLIC         = module.lambda_update_public.function_name
    TARGET_UPDATE_PRIVATE        = module.lambda_update_private.function_name
  }
}

module "api_gateway" {
  source                      = "../../modules/api_gateway"
  name                        = "${var.project_name}-http-${local.env}"
  router_lambda_invoke_arn    = module.router_lambda.function_arn
  router_lambda_function_name = module.router_lambda.function_name
}

output "api_url" {
  value = "${module.api_gateway.api_endpoint}/router"
}
