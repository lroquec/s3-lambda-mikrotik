locals {
  bucket_name = "${var.project_name}-bucket"
}

# S3 Bucket
resource "aws_s3_bucket" "mikrotik_bucket" {
  bucket = local.bucket_name
}

# S3 trigger for Lambda
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.mikrotik_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.mikrotik_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.input_file_path
    filter_suffix       = ".csv"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.mikrotik_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.input_file_path
    filter_suffix       = ".xlsx"
  }
}