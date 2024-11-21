variable "project_name" {
  description = "The name of the project"
  type        = string

}

variable "bucket_name" {
  description = "The name of the S3 bucket"
  type        = string

}

variable "input_file_path" {
  description = "The path for the input files"
  type        = string

}

variable "output_file_path" {
  description = "The path for the output files"
  type        = string

}