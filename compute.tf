# Lambda role
resource "aws_iam_role" "lambda_role" {
  name = "mikrotik_processor_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# S3 policy for Lambda
resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "lambda_s3_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.mikrotik_bucket.arn}/${var.input_file_path}*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.mikrotik_bucket.arn}/${var.output_file_path}*"
      }
    ]
  })
}

# CloudWatch Logs policy
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function
resource "aws_lambda_function" "mikrotik_processor" {
  filename         = "lambda_function.zip"
  function_name    = "mikrotik_processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 180
  memory_size     = 256

  environment {
    variables = {
      INPUT_PATH  = var.input_file_path
      OUTPUT_PATH = var.output_file_path
    }
  }

  layers = [aws_lambda_layer_version.pandas_layer.arn]
}

resource "aws_lambda_layer_version" "pandas_layer" {
  filename            = "pandas_layer.zip"
  layer_name          = "pandas"
  description         = "Pandas layer for Python"
  compatible_runtimes = ["python3.9"]
}

# Lambda permission for S3
resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mikrotik_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.mikrotik_bucket.arn
}