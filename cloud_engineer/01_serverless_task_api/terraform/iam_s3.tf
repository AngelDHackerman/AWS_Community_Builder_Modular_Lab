data "aws_iam_policy_document" "lambda_s3_audit_write" {
  statement {
    sid    = "AllowWriteAuditObjects"
    effect = "Allow"

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.audit.arn}/*"
    ]
  }
}

resource "aws_iam_policy" "lambda_s3_audit_write" {
  name        = "${var.project_name}-${var.environment}-lambda-s3-audit-write"
  description = "Allows Lambda to write audit JSON objects to the S3 audit bucket"
  policy      = data.aws_iam_policy_document.lambda_s3_audit_write.json
}

resource "aws_iam_role_policy_attachment" "lambda_s3_audit_write" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_s3_audit_write.arn
}