resource "aws_dynamodb_table" "tasks" {
  name         = "${var.project_name}-${var.environment}-tasks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "task_id"

  attribute {
    name = "task_id"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-tasks"
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "tasks-api"
  }
}