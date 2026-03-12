output "audit_bucket_name" {
  description = "S3 audit bucket name"
  value       = aws_s3_bucket.audit.bucket
}

output "audit_bucket_arn" {
  description = "S3 audit bucket ARN"
  value       = aws_s3_bucket.audit.arn
}

output "lambda_exec_role_name" {
  description = "Lambda execution role name"
  value       = aws_iam_role.lambda_exec_role.name
}

output "lambda_exec_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_exec_role.arn
}