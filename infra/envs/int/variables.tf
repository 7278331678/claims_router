variable "project_name" {
  type    = string
  default = "router-api"
}

variable "environment" {
  type    = string
  default = "int"
}

variable "aws_region" {
  type = string
}

variable "bedrock_model_id" {
  type    = string
  default = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "log_level" {
  type    = string
  default = "INFO"
}
