data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/serverless-task-api-handler.zip"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14

  tags = {
    Name        = "/aws/lambda/${var.lambda_function_name}"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_lambda_function" "task_api" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_exec_role.arn

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  runtime = "python3.12"
  handler = "handler.lambda_handler"

  timeout     = 10
  memory_size = 256

  architectures = ["x86_64"]

  environment {
    variables = {
      AUDIT_BUCKET_NAME = aws_s3_bucket.audit.bucket
      LOG_LEVEL         = "INFO"
      # TASKS_TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy_attachment.lambda_s3_audit_write,
    aws_cloudwatch_log_group.lambda
  ]

  tags = {
    Name        = var.lambda_function_name
    Project     = var.project_name
    Environment = var.environment
  }
}