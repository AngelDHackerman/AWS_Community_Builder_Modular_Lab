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

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.task_api.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.task_api.arn
}

output "http_api_id" {
  description = "HTTP API ID"
  value       = aws_apigatewayv2_api.task_api.id
}

output "http_api_endpoint" {
  description = "Base endpoint for the HTTP API"
  value       = aws_apigatewayv2_api.task_api.api_endpoint
}

output "tasks_collection_url" {
  description = "GET all tasks URL"
  value       = "${aws_apigatewayv2_api.task_api.api_endpoint}/tasks"
}

output "task_item_url_example" {
  description = "GET one task URL example"
  value       = "${aws_apigatewayv2_api.task_api.api_endpoint}/tasks/123"
}

output "tasks_table_name" {
  description = "DynamoDB tasks table name"
  value       = aws_dynamodb_table.tasks.name
}

output "tasks_table_arn" {
  description = "DynamoDB tasks table ARN"
  value       = aws_dynamodb_table.tasks.arn
}

output "cognito_user_pool_id" {
  description = "El ID del User Pool de Cognito; se utiliza para identificar el directorio de usuarios en AWS."
  value       = aws_cognito_user_pool.task_api_users.id
}

output "cognito_user_pool_issuer" {
  description = "La URL del emisor (Issuer) del User Pool, requerida por el API Gateway Authorizer para validar la autenticidad de los tokens JWT."
  value       = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.task_api_users.id}"
}

output "cognito_app_client_id" {
  description = "El ID del App Client; es el identificador que el frontend o cliente móvil utiliza para interactuar con Cognito."
  value       = aws_cognito_user_pool_client.task_api_client.id
}