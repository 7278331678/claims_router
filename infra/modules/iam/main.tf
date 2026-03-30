terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "region" {
  type = string
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "router_lambda_role" {
  name               = "${var.project_name}-router-role-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role" "target_lambda_role" {
  name               = "${var.project_name}-target-role-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "router_basic_logs" {
  role       = aws_iam_role.router_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "target_basic_logs" {
  role       = aws_iam_role.target_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "router_inline" {
  statement {
    sid    = "InvokeBedrockModel"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel"
    ]
    resources = [
      "arn:aws:bedrock:${var.region}::foundation-model/anthropic.claude-3-sonnet*"
    ]
  }

  statement {
    sid    = "InvokeTargetLambdas"
    effect = "Allow"
    actions = [
      "lambda:InvokeFunction"
    ]
    resources = [
      "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-claim-public-${var.environment}",
      "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-claim-private-${var.environment}",
      "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-claim-summary-public-${var.environment}",
      "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-claim-summary-private-${var.environment}",
      "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-create-public-${var.environment}",
      "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-create-private-${var.environment}",
      "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-update-public-${var.environment}",
      "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-update-private-${var.environment}"
    ]
  }
}

resource "aws_iam_role_policy" "router_policy" {
  name   = "${var.project_name}-router-policy-${var.environment}"
  role   = aws_iam_role.router_lambda_role.id
  policy = data.aws_iam_policy_document.router_inline.json
}

output "router_lambda_role_arn" {
  value = aws_iam_role.router_lambda_role.arn
}

output "target_lambda_role_arn" {
  value = aws_iam_role.target_lambda_role.arn
}
