data "aws_iam_policy_document" "lambda_dynamodb_tasks_access" {
  statement {
    sid    = "AllowTasksTableCrud"
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem"
    ]

    resources = [
      aws_dynamodb_table.tasks.arn
    ]
  }
}

resource "aws_iam_policy" "lambda_dynamodb_tasks_access" {
  name        = "${var.project_name}-${var.environment}-lambda-dynamodb-tasks-access"
  description = "Allows Lambda to read and write tasks in DynamoDB"
  policy      = data.aws_iam_policy_document.lambda_dynamodb_tasks_access.json
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_tasks_access" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb_tasks_access.arn
}