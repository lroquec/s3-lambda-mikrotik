locals {
  bucket_name = "${var.project_name}-bucket"
}

# S3 Bucket
resource "aws_s3_bucket" "mikrotik_bucket" {
  bucket = local.bucket_name
  tags = merge(local.common_tags, {
    Name = local.bucket_name
  })
}

# S3 trigger for Lambda
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.mikrotik_bucket.id

  depends_on = [aws_lambda_permission.allow_bucket]
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

resource "aws_s3_object" "input_prefix" {
  bucket       = aws_s3_bucket.mikrotik_bucket.id
  key          = var.input_file_path
  content_type = "application/x-directory"
}

resource "aws_s3_object" "output_prefix" {
  bucket       = aws_s3_bucket.mikrotik_bucket.id
  key          = var.output_file_path
  content_type = "application/x-directory"
}