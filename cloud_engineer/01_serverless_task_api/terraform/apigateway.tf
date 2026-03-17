resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.project_name}-${var.environment}-http-api"
  retention_in_days = 14

  tags = {
    Name        = "/aws/apigateway/${var.project_name}-${var.environment}-http-api"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_apigatewayv2_api" "task_api" {
  name          = "${var.project_name}-${var.environment}-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
    allow_headers = ["content-type", "authorization"]
    max_age       = 300
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-http-api"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_apigatewayv2_integration" "task_api_lambda" {
  api_id = aws_apigatewayv2_api.task_api.id

  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.task_api.invoke_arn
  payload_format_version = "2.0"
  timeout_milliseconds   = 30000
}

resource "aws_apigatewayv2_authorizer" "cognito_jwt" {
  api_id           = aws_apigatewayv2_api.task_api.id
  name             = "${var.project_name}-${var.environment}-cognito-jwt"
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.task_api_client.id]
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.task_api_users.id}"
  }
}

# Apply security to specific routes in the API
resource "aws_apigatewayv2_route" "get_tasks" {
  api_id    = aws_apigatewayv2_api.task_api.id
  route_key = "GET /tasks"
  target    = "integrations/${aws_apigatewayv2_integration.task_api_lambda.id}"

  authorization_type = "NONE"
}

resource "aws_apigatewayv2_route" "get_task_by_id" {
  api_id    = aws_apigatewayv2_api.task_api.id
  route_key = "GET /tasks/{task_id}"
  target    = "integrations/${aws_apigatewayv2_integration.task_api_lambda.id}"

  authorization_type = "NONE"
}

resource "aws_apigatewayv2_route" "post_task" {
  api_id    = aws_apigatewayv2_api.task_api.id
  route_key = "POST /tasks"
  target    = "integrations/${aws_apigatewayv2_integration.task_api_lambda.id}"

  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_jwt.id
}

resource "aws_apigatewayv2_route" "patch_task_by_id" {
  api_id    = aws_apigatewayv2_api.task_api.id
  route_key = "PATCH /tasks/{task_id}"
  target    = "integrations/${aws_apigatewayv2_integration.task_api_lambda.id}"

  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_jwt.id
}

resource "aws_apigatewayv2_route" "delete_task_by_id" {
  api_id    = aws_apigatewayv2_api.task_api.id
  route_key = "DELETE /tasks/{task_id}"
  target    = "integrations/${aws_apigatewayv2_integration.task_api_lambda.id}"

  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_jwt.id
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.task_api.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn

    format = jsonencode({
      requestId      = "$context.requestId"
      sourceIp       = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      integrationErr = "$context.integrationErrorMessage"
    })
  }

  default_route_settings {
    throttling_burst_limit = 20
    throttling_rate_limit  = 10
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-default-stage"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_lambda_permission" "allow_http_api_invoke" {
  statement_id  = "AllowExecutionFromHttpApi"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.task_api.function_name
  principal     = "apigateway.amazonaws.com"

  # PoC: permiso amplio para este API.
  # Luego se puede restringir por método/ruta.
  source_arn = "${aws_apigatewayv2_api.task_api.execution_arn}/*/*"
}