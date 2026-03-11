locals {
  audit_bucket_name = lower(
    "${var.project_name}-${var.environment}-audit-${data.aws_caller_identity.current.account_id}"
  )

  lambda_exec_role_name = "${var.project_name}-${var.environment}-lambda-exec-role"

  lambda_basic_execution_policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}