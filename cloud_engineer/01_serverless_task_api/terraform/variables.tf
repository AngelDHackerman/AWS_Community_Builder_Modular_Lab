variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name in lowercase and hyphenated"
  type        = string
  default     = "serverless-task-api-project"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "lambda_function_name" {
  description = "Lambda function name"
  type        = string
  default     = "serverless-task-api-handler"
}

variable "force_destroy_audit_bucket" {
  description = "Allow Terraform to delete non-empty audit bucket. Useful for PoC only."
  type        = bool
  default     = true
}